from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse, HttpResponseRedirect
from coaching.auth_views import SteamLoginView, SteamCallbackView, register_view, login_view
import urllib.parse


def auth_callback_view(request):
    token = request.GET.get("token", "")
    steam_id = request.GET.get("steam_id", "")
    username = request.GET.get("username", "")
    next_page = request.GET.get("next", "")
    return_to = request.GET.get("return_to", "")
    app_link = f"client://auth-callback?token={token}&steam_id={steam_id}&username={username}&next={next_page}"
    hash_params = f"token={token}&steam_id={steam_id}&next={next_page}"
    frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:8081")
    web_redirect = f"{return_to}/#{hash_params}" if return_to else f"{frontend_url}/#{hash_params}"
    has_return_to = bool(return_to)
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Vkhod cherez Steam</title>
</head>
<body>
<script>
(function(){{
  var hasReturnTo = { 'true' if has_return_to else 'false' };
  if (hasReturnTo) {{
    window.location.href = '{web_redirect}';
  }} else {{
    window.location.href = '{app_link}';
  }}
}})();
</script>
<p>Perenapravlenie...</p>
</body>
</html>"""
    return HttpResponse(html)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/coaching/', include('coaching.urls')),
    path('api/stratz/', include('stratz_meta.api.urls')),
    path('api-auth/', include('rest_framework.urls')),
    path('api/auth/steam/login/', SteamLoginView.as_view(), name='steam-login'),
    path('api/auth/steam/callback/', SteamCallbackView.as_view(), name='steam-callback'),
    path('api/auth/register/', register_view, name='register'),
    path('api/auth/login/', login_view, name='login'),
    path('auth-callback/', auth_callback_view, name='auth-callback'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
