from rest_framework import serializers
from .models import HeroMeta

class HeroMetaSerializer(serializers.ModelSerializer):
    class Meta:
        model = HeroMeta
        fields = '__all__'

