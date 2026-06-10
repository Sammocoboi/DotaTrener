from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from coaching.auth_views import SteamLoginView, SteamCallbackView


def auth_callback_view(request):
    token = request.GET.get("token", "")
    steam_id = request.GET.get("steam_id", "")
    username = request.GET.get("username", "")
    next_page = request.GET.get("next", "")
    app_link = f"client://auth-callback?token={token}&steam_id={steam_id}&username={username}&next={next_page}"
    FRONTEND_URL = getattr(settings, "FRONTEND_URL", "http://localhost:8081")
    html = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>Vhod cherez Steam vypolnen</title></head>
<body style="background:#0d1117;color:#c9d1d9;display:flex;flex-direction:column;align-items:center;justify-content:center;height:100vh;font-family:sans-serif;margin:0;text-align:center;padding:20px">
<h2>Vhod cherez Steam vypolnen</h2>
<p id="msg">Perenapravlenie v prilozhenie...</p>
<script>
window.location.href = "{app_link}";
setTimeout(function() {{ document.getElementById('msg').textContent = 'Esli prilozhenie ne otkrylos avtomaticheski, zakrojte etu vkladku i vernites v prilozhenie.'; }}, 2000);
</script>
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
