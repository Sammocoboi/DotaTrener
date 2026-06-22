import json
import urllib.parse
import requests
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseRedirect
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

STEAM_OPENID_URL = "https://steamcommunity.com/openid/login"
STEAM_ID_OFFSET = 76561197960265728


def _steam64_to_account_id(steam_id_64: int) -> int:
    return steam_id_64 - STEAM_ID_OFFSET


def _build_steam_login_url(callback_url: str) -> str:
    params = {
        "openid.ns": "http://specs.openid.net/auth/2.0",
        "openid.mode": "checkid_setup",
        "openid.return_to": callback_url,
        "openid.realm": callback_url,
        "openid.identity": "http://specs.openid.net/auth/2.0/identifier_select",
        "openid.claimed_id": "http://specs.openid.net/auth/2.0/identifier_select",
    }
    return f"{STEAM_OPENID_URL}?{urllib.parse.urlencode(params)}"


def _verify_steam_response(params: dict) -> str | None:
    verify_params = {
        "openid.assoc_handle": params.get("openid.assoc_handle", ""),
        "openid.signed": params.get("openid.signed", ""),
        "openid.sig": params.get("openid.sig", ""),
        "openid.ns": params.get("openid.ns", ""),
    }
    signed_fields = params.get("openid.signed", "").split(",")
    for field in signed_fields:
        key = f"openid.{field}"
        if key in params:
            verify_params[key] = params[key]

    verify_params["openid.mode"] = "check_authentication"

    try:
        resp = requests.post(STEAM_OPENID_URL, data=verify_params, timeout=10)
        if "is_valid:true" in resp.text.lower():
            identity = params.get("openid.identity", "")
            if "/id/" in identity:
                return identity.split("/id/")[-1].rstrip("/")
    except requests.RequestException:
        pass
    return None


def _get_or_create_user(steam_id: str) -> tuple[User, bool]:
    steam_id_64 = int(steam_id)
    account_id = _steam64_to_account_id(steam_id_64)

    from coaching.models import Player

    existing_player = Player.objects.filter(steam_account_id=account_id).select_related('user').first()
    if existing_player:
        return existing_player.user, False

    username = f"steam_{steam_id_64}"
    user, created = User.objects.get_or_create(
        username=username,
        defaults={"first_name": f"Steam {steam_id_64}"},
    )

    player, _ = Player.objects.get_or_create(user=user)
    if not player.steam_account_id:
        player.steam_account_id = account_id
        player.steam_id_64 = steam_id_64
        player.save(update_fields=["steam_account_id", "steam_id_64"])

    return user, created


class SteamLoginView(View):
    def get(self, request):
        next_page = request.GET.get("next", "")
        return_to = request.GET.get("return_to", "")
        site_url = getattr(settings, "SITE_URL", "http://localhost:8000")
        callback = f"{site_url}/api/auth/steam/callback/"
        params = []
        if next_page:
            params.append(f"next={urllib.parse.quote(next_page)}")
        if return_to:
            params.append(f"return_to={urllib.parse.quote(return_to)}")
        if params:
            callback += "?" + "&".join(params)
        login_url = _build_steam_login_url(callback)
        return HttpResponseRedirect(login_url)


@method_decorator(csrf_exempt, name="dispatch")
class SteamCallbackView(View):
    def get(self, request):
        params = request.GET.dict()

        if params.get("openid.mode") != "id_res":
            return JsonResponse({"error": "Invalid Steam OpenID response"}, status=400)

        steam_id = _verify_steam_response(params)
        if not steam_id:
            return JsonResponse({"error": "Steam verification failed"}, status=400)

        user, created = _get_or_create_user(steam_id)

        from rest_framework.authtoken.models import Token

        token, _ = Token.objects.get_or_create(user=user)

        next_page = request.GET.get("next", "")
        return_to = request.GET.get("return_to", "")
        site_url = getattr(settings, "SITE_URL", "http://localhost:8000")
        redirect_url = (
            f"{site_url}/auth-callback/"
            f"?token={token.key}"
            f"&steam_id={user.player_profile.steam_account_id}"
            f"&username={user.username}"
        )
        if next_page:
            redirect_url += f"&next={urllib.parse.quote(next_page)}"
        if return_to:
            redirect_url += f"&return_to={urllib.parse.quote(return_to)}"
        return HttpResponseRedirect(redirect_url)


@csrf_exempt
def register_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    email = (body.get("email") or "").strip().lower()
    username = (body.get("username") or "").strip()
    password = body.get("password") or ""

    if not email or not username or not password:
        return JsonResponse({"error": "Email, имя и пароль обязательны"}, status=400)

    if len(password) < 6:
        return JsonResponse({"error": "Пароль минимум 6 символов"}, status=400)

    if User.objects.filter(email=email).exists():
        return JsonResponse({"error": "Email уже зарегистрирован"}, status=400)

    if User.objects.filter(username=username).exists():
        return JsonResponse({"error": "Имя пользователя уже занято"}, status=400)

    user = User.objects.create_user(username=username, email=email, password=password)

    from coaching.models import Player
    Player.objects.create(user=user)

    from rest_framework.authtoken.models import Token
    token, _ = Token.objects.get_or_create(user=user)

    return JsonResponse({
        "token": token.key,
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
    })


@csrf_exempt
def login_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    email = (body.get("email") or "").strip().lower()
    password = body.get("password") or ""

    if not email or not password:
        return JsonResponse({"error": "Email и пароль обязательны"}, status=400)

    try:
        user_obj = User.objects.get(email=email)
    except User.DoesNotExist:
        return JsonResponse({"error": "Неверный email или пароль"}, status=400)

    user = authenticate(username=user_obj.username, password=password)
    if user is None:
        return JsonResponse({"error": "Неверный email или пароль"}, status=400)

    from rest_framework.authtoken.models import Token
    token, _ = Token.objects.get_or_create(user=user)

    steam_id = None
    try:
        steam_id = user.player_profile.steam_account_id
    except Exception:
        pass

    return JsonResponse({
        "token": token.key,
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "steam_id": steam_id,
    })
