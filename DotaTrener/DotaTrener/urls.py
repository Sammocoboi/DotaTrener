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
    if return_to:
        redirect = f"{return_to}/#token={token}&steam_id={steam_id}&next={next_page}"
    else:
        redirect = f"dotatrener://auth-callback?token={token}&steam_id={steam_id}&username={username}&next={next_page}"
    return HttpResponseRedirect(redirect)


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
