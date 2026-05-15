from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'patches', views.StratzPatchViewSet, basename='patch')
router.register(r'hero-meta', views.HeroMetaViewSet, basename='herometa')
router.register(r'hero-builds', views.HeroBuildViewSet, basename='herobuild')

urlpatterns = [
    path('', include(router.urls)),
]