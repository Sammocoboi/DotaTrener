from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes as perm
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Match, Review, Mistake, Hero, Player
from .serializers import (
    MatchSerializer, ReviewListSerializer, ReviewDetailSerializer, MistakeSerializer,
)
from .serializers import HeroSerializer
class MatchViewSet(viewsets.ModelViewSet):
    serializer_class = MatchSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Match.objects.filter(
            player=self.request.user.player_profile
        ).select_related('hero', 'review').order_by('-played_at')

    def perform_create(self, serializer):
        serializer.save(player=self.request.user.player_profile)


class ReviewViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        return ReviewDetailSerializer if self.action == 'retrieve' else ReviewListSerializer

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'coach_profile'):
            return Review.objects.filter(
                coach=user.coach_profile
            ).select_related('match__hero').prefetch_related('mistakes').order_by('-created_at')
        
        if hasattr(user, 'player_profile'):
            return Review.objects.filter(
                match__player=user.player_profile
            ).select_related('match__hero', 'coach__user').prefetch_related('mistakes').order_by('-created_at')
        
        return Review.objects.none()

    def perform_create(self, serializer):
        if hasattr(self.request.user, 'coach_profile'):
            serializer.save(coach=self.request.user.coach_profile)
        else:
            serializer.save()

    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        review = self.get_object()
        new_status = request.data.get('status')
        if new_status not in dict(Review.STATUS_CHOICES):
            return Response({'error': 'Некорректный статус'}, status=status.HTTP_400_BAD_REQUEST)
        review.status = new_status
        review.save()
        return Response({'status': review.status})


class MistakeViewSet(viewsets.ModelViewSet):
    serializer_class = MistakeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Mistake.objects.all().select_related('category', 'review__match').order_by('timestamp_seconds')

    def perform_create(self, serializer):
        review_id = self.request.data.get('review')
        if not review_id:
            return Response({'error': 'Поле review обязательно'}, status=status.HTTP_400_BAD_REQUEST)
        review = get_object_or_404(Review, id=review_id)
        serializer.save(review=review)


class HeroViewSet(viewsets.ReadOnlyModelViewSet):
    """Только чтение списка героев"""
    queryset = Hero.objects.all().order_by('localized_name')
    serializer_class = HeroSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


@api_view(["POST"])
@perm([permissions.IsAuthenticated])
def link_steam_account(request):
    """Привязать Steam Account ID к профилю игрока"""
    steam_id = request.data.get("steam_account_id")
    if not steam_id:
        return Response({"error": "steam_account_id обязателен"}, status=400)
    try:
        steam_id = int(steam_id)
    except (TypeError, ValueError):
        return Response({"error": "steam_account_id должен быть числом"}, status=400)

    player, _ = Player.objects.get_or_create(user=request.user)
    player.steam_account_id = steam_id
    player.save(update_fields=["steam_account_id"])
    return Response({"steam_account_id": player.steam_account_id})


@api_view(["POST"])
@perm([permissions.IsAuthenticated])
def set_stratz_token(request):
    """Сохранить персональный Stratz API токен"""
    token = request.data.get("stratz_token", "").strip()
    if not token:
        return Response({"error": "stratz_token обязателен"}, status=400)
    player, _ = Player.objects.get_or_create(user=request.user)
    player.stratz_token = token
    player.save(update_fields=["stratz_token"])
    return Response({"ok": True})


@api_view(["GET"])
@perm([permissions.IsAuthenticated])
def fetch_my_matches(request):
    """Получить историю матчей залогиненного игрока из Stratz"""
    player = getattr(request.user, "player_profile", None)
    if not player or not player.steam_account_id:
        return Response(
            {"error": "Steam Account ID не привязан. Сначала POST /api/coaching/link-steam/"},
            status=400,
        )

    limit = int(request.query_params.get("limit", 20))

    from stratz_meta.services import StratzClient

    stratz_token = getattr(player, "stratz_token", "") or ""
    client = StratzClient(token=stratz_token if stratz_token else None)
    profile = client.fetch_player_profile(player.steam_account_id)
    matches = client.fetch_player_matches(player.steam_account_id, take=limit)

    import logging
    logger = logging.getLogger(__name__)
    logger.warning("Stratz profile for %s: %s", player.steam_account_id, profile)
    logger.warning("Stratz matches for %s: %d found", player.steam_account_id, len(matches))

    hero_map = {}
    for m in matches:
        for p in m.get("players", []):
            hid = p.get("heroId")
            if hid and hid not in hero_map:
                hero_map[hid] = Hero.objects.filter(steam_id=int(hid)).first()

    results = []
    for m in matches:
        players = m.get("players", [])
        user_steam_id = player.steam_account_id
        my_player = next(
            (pl for pl in players if pl.get("steamAccountId") == user_steam_id),
            players[0] if players else {},
        )
        hero = hero_map.get(my_player.get("heroId"))

        duration = m.get("duration", 0)
        side = "radiant" if my_player.get("isRadiant") else "dire"
        won = (my_player.get("isRadiant") and m.get("didRadiantWin")) or (
            not my_player.get("isRadiant") and not m.get("didRadiantWin")
        )
        result = "win" if won else "loss"
        played = m.get("startDateTime", 0)

        from django.utils import timezone
        import datetime

        played_at = timezone.now()
        if played:
            played_at = timezone.make_aware(
                datetime.datetime.fromtimestamp(played)
            )

        items = [my_player.get(f"item{j}Id") for j in range(6)]

        match_obj, created = Match.objects.update_or_create(
            match_id=str(m.get("id")),
            player=player,
            defaults={
                "hero": hero,
                "player_side": side,
                "result": result,
                "lobby_type": "ranked",
                "duration_seconds": duration,
                "played_at": played_at,
                "kills": my_player.get("kills", 0),
                "deaths": my_player.get("deaths", 0),
                "assists": my_player.get("assists", 0),
                "gpm": my_player.get("goldPerMinute", 0),
                "xpm": my_player.get("experiencePerMinute", 0),
                "last_hits": my_player.get("numLastHits", 0),
                "denies": my_player.get("numDenies", 0),
                "api_data": m,
            },
        )

        results.append({
            "match_id": m.get("id"),
            "hero": hero.localized_name if hero else f"Hero {my_player.get('heroId')}",
            "result": result,
            "side": side,
            "duration": duration,
            "kda": f"{my_player.get('kills',0)}/{my_player.get('deaths',0)}/{my_player.get('assists',0)}",
            "gpm": my_player.get("goldPerMinute", 0),
            "xpm": my_player.get("experiencePerMinute", 0),
            "created": created,
        })

    return Response({
        "steam_account_id": player.steam_account_id,
        "wins": profile.get("winCount") if profile else 0,
        "losses": profile.get("loseCount") if profile else 0,
        "matches": results,
    })


@api_view(["GET"])
@perm([permissions.IsAuthenticatedOrReadOnly])
def hero_builds(request, hero_id):
    """Сборки героя из Stratz API (предметы + скиллы)"""
    from stratz_meta.services import StratzClient
    from coaching.models import Hero, Item, Ability

    hero = Hero.objects.filter(steam_id=int(hero_id)).first()
    if not hero:
        return Response({"error": "Герой не найден"}, status=404)

    client = StratzClient()
    client.load_item_catalog()
    client.load_ability_catalog()

    item_builds = client.fetch_hero_builds(int(hero_id), "item", take=20)
    skill_builds = client.fetch_hero_builds(int(hero_id), "skill", take=10)

    def enrich_items(builds):
        result = []
        for b in builds:
            seq = []
            for entry in b.get("sequence", []):
                iid = entry.get("id")
                item_obj = Item.objects.filter(steam_id=iid).first() if iid else None
                seq.append({
                    "id": iid,
                    "name": entry.get("name") or client.get_item_name(iid) if iid else "",
                    "image": item_obj.image_url if item_obj else client.get_item_image_url(iid) if iid else "",
                    "time": entry.get("time"),
                })
            result.append({
                "build_type": "item",
                "sequence": seq,
                "win_rate": b.get("win_rate", 0),
                "games": b.get("games", 0),
                "role": b.get("role", ""),
            })
        return result

    def enrich_skills(builds):
        result = []
        for b in builds:
            seq = []
            for entry in b.get("sequence", []):
                aid = entry.get("id")
                ability_obj = Ability.objects.filter(steam_id=aid).first() if aid else None
                seq.append({
                    "id": aid,
                    "name": entry.get("name") or client.get_ability_name(aid) if aid else "",
                    "image": ability_obj.image_url if ability_obj else client.get_ability_image_url(aid) if aid else "",
                })
            result.append({
                "build_type": "skill",
                "sequence": seq,
                "win_rate": b.get("win_rate", 0),
                "games": b.get("games", 0),
            })
        return result

    return Response({
        "hero_id": hero.steam_id,
        "hero_name": hero.localized_name,
        "hero_image": hero.image_url,
        "item_builds": enrich_items(item_builds),
        "skill_builds": enrich_skills(skill_builds),
    })


MATCH_DETAIL_QUERY = """{
  match(id: %s) {
    id
    didRadiantWin
    startDateTime
    players {
      steamAccountId
      heroId
      isRadiant
      kills
      deaths
      assists
      goldPerMinute
      experiencePerMinute
      numLastHits
      numDenies
      heroDamage
      towerDamage
      networth
      item0Id
      item1Id
      item2Id
      item3Id
      item4Id
      item5Id
    }
  }
}"""


@api_view(["GET"])
@perm([permissions.IsAuthenticated])
def match_detail(request, match_id):
    """Полная статистика матча"""
    player = getattr(request.user, "player_profile", None)
    if not player:
        return Response({"error": "Профиль не найден"}, status=400)

    from stratz_meta.services import StratzClient

    client = StratzClient()
    data = client.graphql(MATCH_DETAIL_QUERY % match_id)
    api = (data or {}).get("match") or {}

    if not api:
        return Response({"error": "Матч не найден"}, status=404)

    all_players = api.get("players", [])
    duration = 0

    hero_ids = [p.get("heroId") for p in all_players if p.get("heroId")]
    hero_objs = Hero.objects.filter(steam_id__in=[int(h) for h in hero_ids if h])
    hero_lookup = {h.steam_id: h for h in hero_objs}

    client.load_item_catalog()

    players = []
    for p in all_players:
        hid = p.get("heroId")
        hero_obj = hero_lookup.get(int(hid)) if hid else None

        items = []
        for j in range(6):
            iid = p.get(f"item{j}Id")
            if iid:
                items.append({
                    "id": iid,
                    "name": client.get_item_name(int(iid)),
                    "image": client.get_item_image_url(int(iid)),
                })

        players.append({
            "hero_id": hid,
            "hero_name": hero_obj.localized_name if hero_obj else f"Hero {hid}",
            "hero_image": hero_obj.image_url if hero_obj else "",
            "is_radiant": p.get("isRadiant", False),
            "kills": p.get("kills", 0),
            "deaths": p.get("deaths", 0),
            "assists": p.get("assists", 0),
            "gpm": p.get("goldPerMinute", 0),
            "xpm": p.get("experiencePerMinute", 0),
            "last_hits": p.get("numLastHits", 0),
            "denies": p.get("numDenies", 0),
            "hero_damage": p.get("heroDamage", 0),
            "tower_damage": p.get("towerDamage", 0),
            "networth": p.get("networth", 0),
            "items": items,
        })

    return Response({
        "match_id": api.get("id", match_id),
        "duration": duration,
        "radiant_win": api.get("didRadiantWin", False),
        "start_time": api.get("startDateTime", 0),
        "players": players,
    })
