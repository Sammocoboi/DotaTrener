from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes as perm
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from django.utils import timezone
from .models import Match, Review, Mistake, Hero, Player, Coach, CoachService, CoachApplication
from .serializers import (
    MatchSerializer, ReviewListSerializer, ReviewDetailSerializer, MistakeSerializer,
    CoachListSerializer, CoachDetailSerializer, CoachServiceSerializer,
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
    """Привязать Steam Account ID (только при регистрации)"""
    player, _ = Player.objects.get_or_create(user=request.user)
    if player.steam_account_id:
        return Response({"error": "Steam аккаунт уже привязан. Перепривязка запрещена."}, status=400)

    steam_id = request.data.get("steam_account_id")
    if not steam_id:
        return Response({"error": "steam_account_id обязателен"}, status=400)
    try:
        steam_id = int(steam_id)
    except (TypeError, ValueError):
        return Response({"error": "steam_account_id должен быть числом"}, status=400)

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
def coach_list(request):
    """Список всех тренеров"""
    coaches = Coach.objects.filter(user__player_profile__is_coach=True).select_related('user__player_profile')
    serializer = CoachListSerializer(coaches, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def coach_detail(request, coach_id):
    """Детальная информация о тренере + его услуги"""
    coach = get_object_or_404(Coach, id=coach_id)
    serializer = CoachDetailSerializer(coach)
    return Response(serializer.data)


@api_view(["GET", "POST"])
@perm([permissions.IsAuthenticated])
def my_services(request):
    """Услуги текущего тренера"""
    coach = getattr(request.user, "coach_profile", None)
    if not coach:
        return Response({"error": "Вы не тренер"}, status=400)

    if request.method == "POST":
        serializer = CoachServiceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(coach=coach)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    services = coach.services.all()
    serializer = CoachServiceSerializer(services, many=True)
    return Response(serializer.data)


@api_view(["PATCH", "DELETE"])
@perm([permissions.IsAuthenticated])
def my_service_detail(request, service_id):
    """Изменить/удалить услугу"""
    coach = getattr(request.user, "coach_profile", None)
    if not coach:
        return Response({"error": "Вы не тренер"}, status=400)
    service = get_object_or_404(CoachService, id=service_id, coach=coach)

    if request.method == "DELETE":
        service.delete()
        return Response(status=204)

    serializer = CoachServiceSerializer(service, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)


@api_view(["GET", "PATCH"])
@perm([permissions.IsAuthenticated])
def profile(request):
    """Профиль пользователя: Player + Coach + Steam rank"""
    player, _ = Player.objects.get_or_create(user=request.user)
    coach = getattr(request.user, "coach_profile", None)

    if request.method == "PATCH":
        data = request.data
        if "favorite_role" in data:
            player.favorite_role = data["favorite_role"]
            player.save(update_fields=["favorite_role"])
        if "stratz_token" in data:
            player.stratz_token = data["stratz_token"]
            player.save(update_fields=["stratz_token"])
        if coach and "bio" in data:
            coach.bio = data["bio"]
            coach.save(update_fields=["bio"])
        if coach and "specialization" in data:
            coach.specialization = data["specialization"]
            coach.save(update_fields=["specialization"])

    from stratz_meta.services import StratzClient
    client = StratzClient(token=player.stratz_token if player.stratz_token else None)
    rank_data = client.fetch_player_rank(player.steam_account_id) if player.steam_account_id else {}

    return Response({
        "user": {
            "id": request.user.id,
            "username": request.user.username,
            "date_joined": request.user.date_joined,
            "is_staff": request.user.is_staff,
        },
        "player": {
            "steam_account_id": player.steam_account_id,
            "steam_id_64": player.steam_id_64,
            "stratz_token": bool(player.stratz_token),
            "current_mmr": player.current_mmr,
            "peak_mmr": player.peak_mmr,
            "favorite_role": player.favorite_role,
            "is_coach": player.is_coach,
        },
        "coach": {
            "specialization": coach.specialization if coach else "",
            "bio": coach.bio if coach else "",
            "rating": coach.rating if coach else 0.0,
            "mmr_verified": coach.mmr_verified if coach else 0,
            "mmr_verified_at": coach.mmr_verified_at if coach else None,
        } if coach else None,
        "rank": {
            "season_rank": rank_data.get("seasonRank", 0),
            "leaderboard_rank": rank_data.get("seasonLeaderboardRank"),
            "season_rank_label": _rank_label(rank_data.get("seasonRank", 0)),
            "is_immortal": (rank_data.get("seasonRank", 0) or 0) >= 80,
        } if rank_data else None,
    })


def _rank_label(season_rank: int) -> str:
    MEDALS = [
        (1, "Herald"), (2, "Guardian"), (3, "Crusader"),
        (4, "Archon"), (5, "Legend"), (6, "Ancient"),
        (7, "Divine"),
    ]
    if season_rank <= 0:
        return "Uncalibrated"
    if season_rank >= 80:
        return "Immortal"
    medal_id = season_rank // 10
    star = season_rank % 10
    for mid, name in MEDALS:
        if medal_id == mid:
            return f"{name} {star}" if 1 <= star <= 5 else name
    return f"Rank {season_rank}"


@api_view(["POST"])
@perm([permissions.IsAuthenticated])
def become_coach(request):
    """Подать заявку на становление тренером"""
    player, _ = Player.objects.get_or_create(user=request.user)
    if not player.steam_account_id:
        return Response({"error": "Сначала привяжи Steam аккаунт"}, status=400)

    existing = CoachApplication.objects.filter(user=request.user, status="pending").first()
    if existing:
        return Response({"error": "У тебя уже есть активная заявка"}, status=400)

    message = request.data.get("message", "")
    application = CoachApplication.objects.create(user=request.user, message=message)

    return Response({
        "ok": True,
        "application": {
            "id": application.id,
            "status": application.status,
            "message": application.message,
            "created_at": application.created_at,
        },
    })


@api_view(["GET"])
@perm([permissions.IsAuthenticated])
def my_application(request):
    """Статус моей заявки"""
    app = CoachApplication.objects.filter(user=request.user).order_by("-created_at").first()
    if not app:
        return Response({"application": None})
    return Response({
        "application": {
            "id": app.id,
            "status": app.status,
            "message": app.message,
            "created_at": app.created_at,
            "reviewed_at": app.reviewed_at,
        }
    })


@api_view(["GET", "POST"])
@perm([permissions.IsAdminUser])
def applications_list(request):
    """Список заявок (для админа)"""
    if request.method == "POST":
        app_id = request.data.get("application_id")
        action = request.data.get("action")
        app = get_object_or_404(CoachApplication, id=app_id)

        if action == "accept":
            app.status = "accepted"
            app.reviewed_at = timezone.now()
            app.reviewed_by = request.user
            app.save()

            player, _ = Player.objects.get_or_create(user=app.user)
            player.is_coach = True
            player.save(update_fields=["is_coach"])

            Coach.objects.get_or_create(user=app.user)
        elif action == "reject":
            app.status = "rejected"
            app.reviewed_at = timezone.now()
            app.reviewed_by = request.user
            app.save()
        else:
            return Response({"error": "Действие должно быть accept или reject"}, status=400)

        return Response({"ok": True, "status": app.status})

    status_filter = request.query_params.get("status", "pending")
    apps = CoachApplication.objects.filter(status=status_filter).order_by("-created_at")
    return Response([{
        "id": a.id,
        "user_id": a.user.id,
        "username": a.user.username,
        "message": a.message,
        "status": a.status,
        "created_at": a.created_at,
    } for a in apps])


@api_view(["GET"])
@perm([permissions.IsAuthenticatedOrReadOnly])
def hero_builds(request, hero_id):
    """Сборки героя из Stratz API (предметы + скиллы)"""
    from django.core.cache import cache
    from stratz_meta.services import StratzClient
    from coaching.models import Hero, Item, Ability

    hero = Hero.objects.filter(steam_id=int(hero_id)).first()
    if not hero:
        return Response({"error": "Герой не найден"}, status=404)

    cache_key = f"hero_builds:v2:{hero_id}:DIVINE_IMMORTAL"
    cached = cache.get(cache_key)
    if cached:
        return Response(cached)

    client = StratzClient()
    client.load_item_catalog()
    client.load_ability_catalog()

    item_builds = client.fetch_hero_builds(int(hero_id), "item", take=20)
    skill_builds = client.fetch_hero_builds(int(hero_id), "skill", take=10)
    talent_builds = client.fetch_hero_talents(int(hero_id))

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

    def enrich_talents(talents):
        result = []
        for t in talents:
            aid = t["abilityId"]
            ability_obj = Ability.objects.filter(steam_id=aid).first() if aid else None
            result.append({
                "abilityId": aid,
                "tier": t["tier"],
                "slot": t["slot"],
                "name": ability_obj.display_name if ability_obj else t.get("name", f"Ability {aid}"),
                "image": ability_obj.image_url if ability_obj else (client.get_ability_image_url(aid) if aid else ""),
                "matchCount": t.get("matchCount", 0),
                "win_rate": t.get("win_rate", 0),
                "pick_rate": t.get("pick_rate", 0),
            })
        return result

    result = {
        "hero_id": hero.steam_id,
        "hero_name": hero.localized_name,
        "hero_image": hero.image_url,
        "item_builds": enrich_items(item_builds),
        "skill_builds": enrich_skills(skill_builds),
        "talent_builds": enrich_talents(talent_builds),
    }
    cache.set(cache_key, result, 60 * 60)
    return Response(result)


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
      backpack0Id
      backpack1Id
      backpack2Id
      neutral0Id
      playbackData {
        purchaseEvents {
          time
          itemId
        }
      }
      abilities {
        abilityId
        time
        level
        isTalent
      }
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
    client.load_ability_catalog()

    players = []
    for p in all_players:
        hid = p.get("heroId")
        hero_obj = hero_lookup.get(int(hid)) if hid else None

        purchase_events = (p.get("playbackData") or {}).get("purchaseEvents") or []
        purchase_time = {}
        for ev in purchase_events:
            iid = ev.get("itemId")
            t = ev.get("time")
            if iid is not None and t is not None:
                purchase_time[int(iid)] = int(t)

        items = []
        for j in range(6):
            iid = p.get(f"item{j}Id")
            if iid:
                items.append({
                    "id": iid,
                    "name": client.get_item_name(int(iid)),
                    "image": client.get_item_image_url(int(iid)),
                    "time": purchase_time.get(int(iid)),
                })
        for j in range(3):
            iid = p.get(f"backpack{j}Id")
            if iid:
                items.append({
                    "id": iid,
                    "name": client.get_item_name(int(iid)),
                    "image": client.get_item_image_url(int(iid)),
                    "time": purchase_time.get(int(iid)),
                })
        nid = p.get("neutral0Id")
        if nid:
            items.append({
                "id": nid,
                "name": client.get_item_name(int(nid)),
                "image": client.get_item_image_url(int(nid)),
                "time": purchase_time.get(int(nid)),
            })
        items.sort(key=lambda x: x.get("time") or 0)

        raw_abilities = p.get("abilities") or []
        abilities = []
        talents = []
        for ab in raw_abilities:
            aid = ab.get("abilityId")
            if aid is not None:
                aid = int(aid)
                if ab.get("isTalent"):
                    talents.append({
                        "id": aid,
                        "name": client.get_ability_name(aid),
                        "image": client.get_ability_image_url(aid),
                        "level": ab.get("level", 1),
                        "time": ab.get("time"),
                    })
                else:
                    abilities.append({
                        "id": aid,
                        "name": client.get_ability_name(aid),
                        "image": client.get_ability_image_url(aid),
                        "level": ab.get("level", 1),
                        "time": ab.get("time"),
                    })
        abilities.sort(key=lambda a: a.get("time") or 0)
        talents.sort(key=lambda a: a.get("level") or 0)

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
            "abilities": abilities,
            "talents": talents,
        })

    return Response({
        "match_id": api.get("id", match_id),
        "duration": duration,
        "radiant_win": api.get("didRadiantWin", False),
        "start_time": api.get("startDateTime", 0),
        "players": players,
    })
