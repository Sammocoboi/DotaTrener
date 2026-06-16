from rest_framework import serializers
from .models import Hero, Match, Review, Mistake, MistakeCategory, Coach, CoachService, CoachReview, CoachVideo, Subscription


class HeroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hero
        fields = ['id', 'name', 'localized_name', 'primary_attr', 'roles', 'image_url']


class MistakeSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Mistake
        fields = [
            'id', 'review', 'category', 'category_name',
            'timestamp_seconds', 'description', 'recommendation',
            'severity', 'created_at'
        ]


class MatchSerializer(serializers.ModelSerializer):
    hero = HeroSerializer(read_only=True)
    review_status = serializers.CharField(source='review.status', read_only=True)

    class Meta:
        model = Match
        fields = [
            'id', 'match_id', 'hero', 'player_side', 'result', 'lobby_type',
            'duration_seconds', 'played_at', 'kills', 'deaths', 'assists',
            'gpm', 'xpm', 'last_hits', 'denies', 'api_data', 'review_status'
        ]
        read_only_fields = ['player']


class ReviewListSerializer(serializers.ModelSerializer):
    coach_username = serializers.CharField(source='coach.user.username', read_only=True)
    match_hero = serializers.CharField(source='match.hero.localized_name', read_only=True)
    match_id = serializers.CharField(source='match.match_id', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'match_id', 'match_hero', 'coach_username', 'overall_score', 'status', 'created_at']


class ReviewDetailSerializer(serializers.ModelSerializer):
    coach_username = serializers.CharField(source='coach.user.username', read_only=True)
    mistakes = MistakeSerializer(many=True, read_only=True)
    match_id = serializers.CharField(source='match.match_id', read_only=True)

    class Meta:
        model = Review
        fields = [
            'id', 'match_id', 'coach_username', 'overall_score', 'summary',
            'status', 'mistakes', 'created_at', 'updated_at'
        ]


class CoachVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoachVideo
        fields = ['id', 'title', 'description', 'file_url', 'thumbnail_url', 'duration_seconds', 'price', 'view_count', 'is_active', 'created_at']
        read_only_fields = ['id', 'view_count', 'created_at']


class CoachReviewSerializer(serializers.ModelSerializer):
    reviewer_username = serializers.CharField(source='reviewer.username', read_only=True)

    class Meta:
        model = CoachReview
        fields = ['id', 'coach', 'reviewer', 'reviewer_username', 'rating', 'text', 'created_at']
        read_only_fields = ['id', 'reviewer', 'created_at']


class CoachServiceSerializer(serializers.ModelSerializer):
    video_title = serializers.CharField(source='video.title', read_only=True, default=None)
    video_url = serializers.CharField(source='video.file_url', read_only=True, default=None)

    class Meta:
        model = CoachService
        fields = ['id', 'title', 'description', 'price', 'duration_minutes', 'video', 'video_title', 'video_url', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class CoachListSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    avatar_url = serializers.CharField(source='user.player_profile.avatar_url', read_only=True, default='')
    service_count = serializers.SerializerMethodField()
    min_price = serializers.SerializerMethodField()

    class Meta:
        model = Coach
        fields = ['id', 'username', 'avatar_url', 'title', 'specialization', 'bio', 'rating', 'mmr_verified', 'service_count', 'min_price']

    def get_service_count(self, obj):
        return obj.services.filter(is_active=True).count()

    def get_min_price(self, obj):
        min_price = obj.services.filter(is_active=True).order_by('price').values_list('price', flat=True).first()
        return float(min_price) if min_price else None


class CoachDetailSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    avatar_url = serializers.CharField(source='user.player_profile.avatar_url', read_only=True, default='')
    services = CoachServiceSerializer(many=True, read_only=True)
    videos = CoachVideoSerializer(many=True, read_only=True)
    coach_reviews = CoachReviewSerializer(many=True, read_only=True)
    review_count = serializers.SerializerMethodField()
    avg_rating = serializers.SerializerMethodField()

    class Meta:
        model = Coach
        fields = ['id', 'username', 'avatar_url', 'title', 'specialization', 'bio', 'rating', 'mmr_verified', 'social_links', 'services', 'videos', 'coach_reviews', 'review_count', 'avg_rating']

    def get_review_count(self, obj):
        return obj.coach_reviews.count()

    def get_avg_rating(self, obj):
        from django.db.models import Avg
        result = obj.coach_reviews.aggregate(avg=Avg('rating'))
        return round(result['avg'], 1) if result['avg'] else None


class SubscriptionSerializer(serializers.ModelSerializer):
    is_expired = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = ['id', 'is_active', 'plan', 'started_at', 'expires_at', 'is_expired']
        read_only_fields = ['id', 'is_active', 'started_at', 'expires_at']

    def get_is_expired(self, obj):
        if not obj.expires_at:
            return True
        from django.utils import timezone
        return obj.expires_at < timezone.now()