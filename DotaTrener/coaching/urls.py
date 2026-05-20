from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'matches', views.MatchViewSet, basename='match')
router.register(r'reviews', views.ReviewViewSet, basename='review')
router.register(r'mistakes', views.MistakeViewSet, basename='mistake')
router.register(r'checkgpms',views.CheckGpm,basename="checkgpm")
urlpatterns = [
    path('', include(router.urls)),
]