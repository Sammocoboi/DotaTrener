import logging
from typing import Any, Dict, List

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes as perm
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

logger = logging.getLogger(__name__)

from django.utils import timezone
from .models import Match, Review, Mistake, Hero, Player, Coach, CoachService, CoachApplication, Conversation, Message, CoachReview, CoachVideo
from .serializers import (
    MatchSerializer, ReviewListSerializer, ReviewDetailSerializer, MistakeSerializer,
    CoachListSerializer, CoachDetailSerializer, CoachServiceSerializer,
    CoachReviewSerializer, CoachVideoSerializer,
)
from .serializers import HeroSerializer
class MatchViewSet(viewsets.ModelViewSet):
    serializer_class = MatchSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        player = getattr(self.request.user, "player_profile", None)
        if not player:
            return Match.objects.none()
        return Match.objects.filter(
            player=player
        ).select_related('hero', 'review').order_by('-played_at')

    def perform_create(self, serializer):
        player, _ = Player.objects.get_or_create(user=self.request.user)
        serializer.save(player=player)


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
        if "avatar_url" in data:
            player.avatar_url = data["avatar_url"]
            player.save(update_fields=["avatar_url"])
        if "username" in data and data["username"].strip():
            request.user.username = data["username"].strip()
            request.user.save(update_fields=["username"])
        if coach and "bio" in data:
            coach.bio = data["bio"]
            coach.save(update_fields=["bio"])
        if coach and "specialization" in data:
            coach.specialization = data["specialization"]
            coach.save(update_fields=["specialization"])
        if coach and "social_links" in data and isinstance(data["social_links"], dict):
            coach.social_links = data["social_links"]
            coach.save(update_fields=["social_links"])

    from stratz_meta.services import StratzClient
    client = StratzClient(token=player.stratz_token if player.stratz_token else None)
    rank_data = client.fetch_player_rank(player.steam_account_id) if player.steam_account_id else {}

    match_stats = None
    if player.steam_account_id:
        profile_data = client.fetch_player_profile(player.steam_account_id)
        if profile_data:
            match_stats = {
                "win_count": int(profile_data.get("winCount") or 0),
                "lose_count": int(profile_data.get("loseCount") or 0),
                "match_count": int(profile_data.get("matchCount") or 0),
                "win_rate": float(profile_data.get("winRate") or 0),
            }

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
            "avatar_url": player.avatar_url,
        },
        "coach": {
            "specialization": coach.specialization if coach else "",
            "bio": coach.bio if coach else "",
            "rating": coach.rating if coach else 0.0,
            "mmr_verified": coach.mmr_verified if coach else 0,
            "mmr_verified_at": coach.mmr_verified_at if coach else None,
            "social_links": coach.social_links if coach else {},
        } if coach else None,
        "rank": {
            "season_rank": rank_data.get("seasonRank", 0),
            "leaderboard_rank": rank_data.get("seasonLeaderboardRank"),
            "season_rank_label": _rank_label(rank_data.get("seasonRank", 0)),
            "is_immortal": (rank_data.get("seasonRank", 0) or 0) >= 80,
        } if rank_data else None,
        "match_stats": match_stats,
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
def upload_avatar(request):
    """Загрузить аватарку (файл)"""
    file = request.FILES.get("file")
    if not file:
        return Response({"error": "Файл не передан"}, status=400)
    if file.size > 5 * 1024 * 1024:
        return Response({"error": "Файл слишком большой (макс 5 МБ)"}, status=400)
    ext = file.name.rsplit(".", 1)[-1].lower() if "." in file.name else "jpg"
    if ext not in ("jpg", "jpeg", "png", "gif", "webp"):
        return Response({"error": "Допустимые форматы: jpg, png, gif, webp"}, status=400)
    import uuid
    filename = f"avatars/{request.user.id}_{uuid.uuid4().hex[:8]}.{ext}"
    from django.conf import settings
    import os
    path = os.path.join(settings.MEDIA_ROOT, filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb+") as dest:
        for chunk in file.chunks():
            dest.write(chunk)
    url = f"{request.scheme}://{request.get_host()}/{settings.MEDIA_URL.lstrip('/')}{filename}"
    player, _ = Player.objects.get_or_create(user=request.user)
    player.avatar_url = url
    player.save(update_fields=["avatar_url"])
    return Response({"url": url})


@api_view(["POST"])
@perm([permissions.IsAuthenticated])
def upload_video(request):
    """Загрузить видео (файл, макс 600 МБ)"""
    coach = getattr(request.user, "coach_profile", None)
    if not coach:
        return Response({"error": "Вы не тренер"}, status=400)

    file = request.FILES.get("file")
    if not file:
        return Response({"error": "Файл не передан"}, status=400)

    max_size = 600 * 1024 * 1024
    if file.size > max_size:
        return Response({"error": "Файл слишком большой (макс 600 МБ)"}, status=400)

    ext = file.name.rsplit(".", 1)[-1].lower() if "." in file.name else "mp4"
    if ext not in ("mp4", "webm", "ogg", "mov", "mkv"):
        return Response({"error": "Допустимые форматы: mp4, webm, ogg, mov, mkv"}, status=400)

    import uuid
    filename = f"videos/{request.user.id}_{uuid.uuid4().hex[:8]}.{ext}"
    from django.conf import settings
    import os
    path = os.path.join(settings.MEDIA_ROOT, filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb+") as dest:
        for chunk in file.chunks():
            dest.write(chunk)

    url = f"{request.scheme}://{request.get_host()}/{settings.MEDIA_URL.lstrip('/')}{filename}"

    title = request.data.get("title", file.name.rsplit(".", 1)[0])
    description = request.data.get("description", "")
    duration = int(request.data.get("duration_seconds", 0))
    price = request.data.get("price", "0")

    video = CoachVideo.objects.create(
        coach=coach,
        title=title,
        description=description,
        file_url=url,
        duration_seconds=duration,
        price=price,
    )

    return Response({
        "id": video.id,
        "url": url,
        "title": video.title,
    }, status=201)


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


@api_view(["GET", "POST"])
@perm([permissions.IsAuthenticatedOrReadOnly])
def coach_reviews(request, coach_id):
    """Отзывы о тренере: список / создать"""
    coach = get_object_or_404(Coach, id=coach_id)

    if request.method == "POST":
        if not request.user.is_authenticated:
            return Response({"error": "Авторизация обязательна"}, status=401)
        if CoachReview.objects.filter(coach=coach, reviewer=request.user).exists():
            return Response({"error": "Вы уже оставляли отзыв"}, status=400)
        serializer = CoachReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(coach=coach, reviewer=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    reviews = coach.coach_reviews.select_related('reviewer').all()
    serializer = CoachReviewSerializer(reviews, many=True)
    return Response(serializer.data)


@api_view(["GET", "POST"])
@perm([permissions.IsAuthenticated])
def my_videos(request):
    """Видео текущего тренера: список / создать"""
    coach = getattr(request.user, "coach_profile", None)
    if not coach:
        return Response({"error": "Вы не тренер"}, status=400)

    if request.method == "POST":
        serializer = CoachVideoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(coach=coach)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    videos = coach.videos.all()
    serializer = CoachVideoSerializer(videos, many=True)
    return Response(serializer.data)


@api_view(["PATCH", "DELETE"])
@perm([permissions.IsAuthenticated])
def my_video_detail(request, video_id):
    """Изменить/удалить видео тренера"""
    coach = getattr(request.user, "coach_profile", None)
    if not coach:
        return Response({"error": "Вы не тренер"}, status=400)
    video = get_object_or_404(CoachVideo, id=video_id, coach=coach)

    if request.method == "DELETE":
        video.delete()
        return Response(status=204)

    serializer = CoachVideoSerializer(video, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)


@api_view(["GET"])
def coach_videos(request, coach_id):
    """Публичный список видео тренера"""
    coach = get_object_or_404(Coach, id=coach_id)
    videos = coach.videos.filter(is_active=True)
    serializer = CoachVideoSerializer(videos, many=True)
    return Response(serializer.data)


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
    durationSeconds
    players {
      steamAccountId
      steamAccount {
        name
        avatar
      }
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
    duration = api.get("durationSeconds", 0) or 0

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
            "steam_account_id": p.get("steamAccountId"),
            "hero_id": hid,
            "hero_name": hero_obj.localized_name if hero_obj else f"Hero {hid}",
            "hero_image": hero_obj.image_url if hero_obj else "",
            "is_radiant": p.get("isRadiant", False),
            "is_me": player.steam_account_id is not None and p.get("steamAccountId") == player.steam_account_id,
            "nickname": (p.get("steamAccount") or {}).get("name") or "",
            "avatar_url": (p.get("steamAccount") or {}).get("avatar") or "",
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


PLAYER_PROFILE_QUERY = """{
  player(steamAccountId: %s) {
    steamAccountId
    winCount
    matchCount
    steamAccount {
      name
      avatar
    }
  }
}"""


@api_view(["GET"])
def public_player_profile(request, steam_id):
    """Публичный профиль игрока по steamAccountId"""
    from stratz_meta.services import StratzClient
    from stratz_meta.services.opendota_client import OpenDotaClient
    client = StratzClient()
    data = client.graphql(PLAYER_PROFILE_QUERY % steam_id)
    if not data or not data.get("player"):
        return Response({"error": "Игрок не найден"}, status=404)

    p = data["player"]
    sa = p.get("steamAccount") or {}

    win_count = int(p.get("winCount") or 0)
    match_count = int(p.get("matchCount") or 0)
    lose_count = match_count - win_count
    win_rate = round(win_count / match_count * 100, 1) if match_count else 0

    rank_data = client.fetch_player_rank(steam_id)

    # OpenDota — последние матчи и лучшие герои
    recent_matches: List[Dict[str, Any]] = []
    best_heroes: List[Dict[str, Any]] = []

    try:
        od = OpenDotaClient()

        od_matches = od.fetch_player_recent_matches(int(steam_id))
        for m in od_matches:
            hero_id = m.get("hero_id")
            hero = Hero.objects.filter(steam_id=int(hero_id)).first() if hero_id else None
            player_slot = m.get("player_slot", 0)
            is_radiant = player_slot < 128
            won = is_radiant == m.get("radiant_win", False)

            recent_matches.append({
                "match_id": str(m.get("match_id", "")),
                "won": won,
                "is_radiant": is_radiant,
                "hero_name": hero.localized_name if hero else f"Hero {hero_id}",
                "hero_image": hero.image_url if hero else "",
                "duration": int(m.get("duration") or 0),
                "kills": int(m.get("kills") or 0),
                "deaths": int(m.get("deaths") or 0),
                "assists": int(m.get("assists") or 0),
                "gpm": int(m.get("gold_per_min") or 0),
                "xpm": int(m.get("xp_per_min") or 0),
                "networth": 0,
                "start_time": int(m.get("start_time") or 0),
            })

        od_heroes = od.fetch_player_heroes(int(steam_id))
        for h in od_heroes[:10]:
            hero_id = h.get("hero_id")
            hero = Hero.objects.filter(steam_id=int(hero_id)).first() if hero_id else None
            h_games = int(h.get("games") or 0)
            h_wins = int(h.get("win") or 0)
            best_heroes.append({
                "hero_id": hero_id,
                "hero_name": hero.localized_name if hero else f"Hero {hero_id}",
                "hero_image": hero.image_url if hero else "",
                "games": h_games,
                "wins": h_wins,
                "win_rate": round(h_wins / h_games * 100, 1) if h_games else 0,
            })
    except Exception:
        logger.exception("OpenDota fetch failed for player %s", steam_id)

    avatar = sa.get("avatar") or ""
    if not avatar:
        try:
            pl = Player.objects.filter(steam_account_id=int(steam_id)).first()
            if pl and pl.avatar_url:
                avatar = pl.avatar_url
        except Exception:
            pass

    return Response({
        "steam_account_id": p.get("steamAccountId"),
        "nickname": sa.get("name") or "",
        "avatar_url": avatar,
        "season_rank": rank_data.get("seasonRank", 0),
        "win_count": win_count,
        "lose_count": lose_count,
        "match_count": match_count,
        "win_rate": win_rate,
        "recent_matches": recent_matches,
        "best_heroes": best_heroes,
    })


@api_view(["GET", "POST"])
@perm([permissions.IsAuthenticated])
def conversations_list(request):
    """Список чатов / создать новый чат"""
    if request.method == "POST":
        coach_id = request.data.get("coach_id")
        service_id = request.data.get("service_id")
        first_message = request.data.get("message", "")

        coach = get_object_or_404(Coach, id=coach_id)
        service = None
        if service_id:
            service = get_object_or_404(CoachService, id=service_id, coach=coach)

        if Conversation.objects.filter(user=request.user, coach=coach).exists():
            conv = Conversation.objects.get(user=request.user, coach=coach)
        else:
            conv = Conversation.objects.create(user=request.user, coach=coach, service=service)

        if first_message.strip():
            Message.objects.create(conversation=conv, sender=request.user, text=first_message.strip())

        return Response({"id": conv.id, "created_at": conv.created_at}, status=201)

    qs = Conversation.objects.filter(
        user=request.user
    ) | Conversation.objects.filter(
        coach__user=request.user
    )
    qs = qs.select_related("user", "coach__user", "service").prefetch_related("messages")
    data = []
    for c in qs.distinct():
        last_msg = c.messages.order_by("-created_at").first()
        unread_count = c.messages.filter(sender__is_staff=False).exclude(sender=request.user).count() if request.user.is_staff else 0
        data.append({
            "id": c.id,
            "other_user": c.coach.user.username if c.coach.user != request.user else c.user.username,
            "other_id": c.coach.id if c.coach.user != request.user else c.user.id,
            "is_coach_side": c.coach.user == request.user,
            "service_title": c.service.title if c.service else None,
            "last_message": last_msg.text[:100] if last_msg else "",
            "last_message_at": last_msg.created_at if last_msg else c.created_at,
            "unread_count": unread_count,
            "created_at": c.created_at,
        })
    return Response(data)


@api_view(["GET", "POST"])
@perm([permissions.IsAuthenticated])
def conversation_detail(request, conv_id):
    """Детали чата + сообщения / отправить сообщение"""
    conv = get_object_or_404(Conversation, id=conv_id)
    if conv.user != request.user and conv.coach.user != request.user:
        return Response({"error": "Нет доступа"}, status=403)

    if request.method == "POST":
        text = request.data.get("text", "").strip()
        if not text:
            return Response({"error": "Текст сообщения обязателен"}, status=400)
        msg = Message.objects.create(conversation=conv, sender=request.user, text=text)
        return Response({
            "id": msg.id,
            "sender": msg.sender.username,
            "text": msg.text,
            "created_at": msg.created_at,
        }, status=201)

    msgs = conv.messages.select_related("sender").all()
    return Response({
        "id": conv.id,
        "service_title": conv.service.title if conv.service else None,
        "user": {"id": conv.user.id, "username": conv.user.username},
        "coach": {"id": conv.coach.id, "username": conv.coach.user.username},
        "messages": [{
            "id": m.id,
            "sender": m.sender.username,
            "text": m.text,
            "created_at": m.created_at,
        } for m in msgs],
    })
