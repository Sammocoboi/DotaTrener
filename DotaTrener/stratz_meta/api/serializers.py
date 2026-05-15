# stratz_meta/serializers.py
from rest_framework import serializers
from ..models import StratzPatch, HeroMeta, HeroBuild


class HeroBuildSerializer(serializers.ModelSerializer):
    class Meta:
        model = HeroBuild
        fields = ['id', 'build_type', 'sequence', 'pick_rate', 'win_rate', 'games', 'role']


class StratzPatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = StratzPatch
        fields = ['version', 'release_date', 'is_current']


class HeroMetaListSerializer(serializers.ModelSerializer):
    hero_name = serializers.CharField(source='hero.localized_name', read_only=True)
    patch_version = serializers.CharField(source='patch.version', read_only=True)

    class Meta:
        model = HeroMeta
        fields = [
            'id', 'hero', 'hero_name', 'patch_version',
            'win_rate', 'pick_rate', 'ban_rate', 'games_played'
        ]


class HeroMetaDetailSerializer(serializers.ModelSerializer):
    hero_name = serializers.CharField(source='hero.localized_name', read_only=True)
    patch_version = serializers.CharField(source='patch.version', read_only=True)
    builds = HeroBuildSerializer(many=True, read_only=True)

    class Meta:
        model = HeroMeta
        fields = [
            'id', 'hero', 'hero_name', 'patch_version',
            'win_rate', 'pick_rate', 'ban_rate', 'games_played',
            'roles', 'builds', 'updated_at'
        ]