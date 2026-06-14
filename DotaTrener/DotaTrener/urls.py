from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse, HttpResponseRedirect
from coaching.auth_views import SteamLoginView, SteamCallbackView


def auth_callback_view(request):
    token = request.GET.get("token", "")
    steam_id = request.GET.get("steam_id", "")
    username = request.GET.get("username", "")
    next_page = request.GET.get("next", "")
    app_link = f"client://auth-callback?token={token}&steam_id={steam_id}&username={username}&next={next_page}"
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta http-equiv="refresh" content="0;url={app_link}">
<title>Otvka cherez Steam</title>
</head>
<body>
<p>Perenapravlenie... <a href="{app_link}">Otkryt prilozhenie</a></p>
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
    path('auth-callback/', auth_callback_view, name='auth-callback'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
