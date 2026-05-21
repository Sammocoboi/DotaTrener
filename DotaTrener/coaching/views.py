from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Match, Review, Mistake
from .serializers import (
    MatchSerializer, ReviewListSerializer, ReviewDetailSerializer, MistakeSerializer, 
)

class MatchViewSet(viewsets.ModelViewSet):
    serializer_class = MatchSerializer
    # Пока разрешено всем авторизованным пользователям. 
    # Позже легко заменить на кастомные права.
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Match.objects.filter(
            player=self.request.user.player_profile
        ).select_related('hero', 'review').order_by('-played_at')

    def perform_create(self, serializer):
        serializer.save(player=self.request.user.player_profile)


class ReviewViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        return ReviewDetailSerializer if self.action == 'retrieve' else ReviewListSerializer

    def get_queryset(self):
        user = self.request.user
        # Простая фильтрация: если есть профиль тренера → свои разборы, иначе → разборы своих матчей
        if hasattr(user, 'coach_profile'):
            return Review.objects.filter(
                coach=user.coach_profile
            ).select_related('match__hero').prefetch_related('mistakes').order_by('-created_at')
        
        if hasattr(user, 'player_profile'):
            return Review.objects.filter(
                match__player=user.player_profile
            ).select_related('match__hero', 'coach__user').prefetch_related('mistakes').order_by('-created_at')
        
        return Review.objects.none()

    def perform_create(self, serializer):
        # Пока просто привязываем к профилю, если он есть
        if hasattr(self.request.user, 'coach_profile'):
            serializer.save(coach=self.request.user.coach_profile)
        else:
            serializer.save()

    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        review = self.get_object()
        new_status = request.data.get('status')
        if new_status not in dict(Review.STATUS_CHOICES):
            return Response({'error': 'Некорректный статус'}, status=status.HTTP_400_BAD_REQUEST)
        review.status = new_status
        review.save()
        return Response({'status': review.status})


class MistakeViewSet(viewsets.ModelViewSet):
    serializer_class = MistakeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Mistake.objects.all().select_related('category', 'review__match').order_by('timestamp_seconds')

    def perform_create(self, serializer):
        # Привязываем ошибку к review, переданному в теле запроса
        review_id = self.request.data.get('review')
        if not review_id:
            return Response({'error': 'Поле review обязательно'}, status=status.HTTP_400_BAD_REQUEST)
        review = get_object_or_404(Review, id=review_id)
        serializer.save(review=review)


