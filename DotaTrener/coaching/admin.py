from django.contrib import admin
from .models import Player, Coach, Hero, Match, Review, Mistake, MistakeCategory

class MistakeInline(admin.TabularInline):
    model = Mistake
    extra = 1

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    inlines = [MistakeInline]
    list_display = ['match', 'coach', 'overall_score', 'status', 'created_at']
    list_filter = ['status', 'coach']

admin.site.register(Player)
admin.site.register(Coach)
admin.site.register(Hero)
admin.site.register(Match)
admin.site.register(MistakeCategory)