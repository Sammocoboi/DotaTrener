from django.shortcuts import render
from rest_framework.viewsets import ReadOnlyModelViewSet
from .models import HeroEndgameLoadout
from .serializers import HeroEndgameLoadoutSerializer

class HeroEndGameViews(ReadOnlyModelViewSet):
    queryset = HeroEndgameLoadout.objects.all()
    serializer_class = HeroEndgameLoadoutSerializer
 