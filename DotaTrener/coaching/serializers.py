from rest_framework import serializers
from .models import Hero, Match, Review, Mistake, MistakeCategory


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