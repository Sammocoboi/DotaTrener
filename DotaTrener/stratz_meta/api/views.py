from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import StratzPatch, HeroMeta, HeroBuild
from .serializers import (
    StratzPatchSerializer, HeroMetaListSerializer, HeroMetaDetailSerializer, HeroBuildSerializer
)
"""
валидация входящего данных вызов
метода сервиса сериализация результатов
"""


class StratzPatchViewSet(viewsets.ReadOnlyModelViewSet):
    """Список и детали патчей"""
    queryset = StratzPatch.objects.all()
    serializer_class = StratzPatchSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    ordering_fields = ['release_date', 'version']


# stratz_meta/views.py (фрагмент HeroMetaViewSet)
class HeroMetaViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        return HeroMetaDetailSerializer if self.action == 'retrieve' else HeroMetaListSerializer

    def get_queryset(self):
        qs = HeroMeta.objects.select_related('hero', 'patch').prefetch_related('builds')
        
        patch = self.request.query_params.get('patch')
        hero_name = self.request.query_params.get('hero')
        min_winrate = self.request.query_params.get('min_wr')
        source = self.request.query_params.get('source')
        min_games = self.request.query_params.get('min_games', '5')
        
        if patch:
            qs = qs.filter(patch__version=patch)
        else:
            current_patch = StratzPatch.objects.filter(is_current=True).first()
            if current_patch:
                qs = qs.filter(patch=current_patch)

        if hero_name:
            qs = qs.filter(hero__localized_name__icontains=hero_name)
        if min_winrate:
            qs = qs.filter(win_rate__gte=float(min_winrate))
        if source:
            qs = qs.filter(source=source)
        if min_games:
            qs = qs.filter(games_played__gte=int(min_games))
            
        return qs.order_by('-win_rate')

    @action(detail=False, methods=['get'])
    def current(self, request):
        """Мета актуального патча"""
        current_patch = StratzPatch.objects.filter(is_current=True).first()
        if not current_patch:
            return Response({'error': 'Актуальный патч не найден'}, status=404)
        
        qs = HeroMeta.objects.filter(patch=current_patch).select_related('hero')
        source = request.query_params.get('source')
        min_games = request.query_params.get('min_games', '5')
        if source:
            qs = qs.filter(source=source)
        if min_games:
            qs = qs.filter(games_played__gte=int(min_games))
        qs = qs.order_by('-win_rate')
        
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class HeroBuildViewSet(viewsets.ReadOnlyModelViewSet):
    """Отдельный доступ к билдам (полезно для фильтров)"""
    queryset = HeroBuild.objects.select_related('hero_meta__hero', 'hero_meta__patch').all()
    serializer_class = HeroBuildSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        qs = super().get_queryset()
        build_type = self.request.query_params.get('type')
        if build_type:
            qs = qs.filter(build_type=build_type)
        return qs.order_by('-win_rate')

