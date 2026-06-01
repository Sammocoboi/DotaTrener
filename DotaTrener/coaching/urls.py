from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'matches', views.MatchViewSet, basename='match')
router.register(r'reviews', views.ReviewViewSet, basename='review')
router.register(r'mistakes', views.MistakeViewSet, basename='mistake')
router.register(r'heroes', views.HeroViewSet, basename='hero')
urlpatterns = [
    path('', include(router.urls)),
    path('link-steam/', views.link_steam_account, name='link-steam'),
    path('my-matches/', views.fetch_my_matches, name='my-matches'),
    path('set-stratz-token/', views.set_stratz_token, name='set-stratz-token'),
    path('match/<str:match_id>/', views.match_detail, name='match-detail'),
    path('hero/<int:hero_id>/builds/', views.hero_builds, name='hero-builds'),
]