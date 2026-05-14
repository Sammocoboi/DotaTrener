from django.contrib import admin
from .models import StratzPatch, HeroMeta, HeroBuild

class HeroBuildInline(admin.TabularInline):
    model = HeroBuild
    extra = 0
    fields = ['build_type', 'role', 'pick_rate', 'win_rate', 'games']

@admin.register(HeroMeta)
class HeroMetaAdmin(admin.ModelAdmin):
    list_display = ('hero', 'patch', 'win_rate', 'pick_rate', 'ban_rate', 'games_played', 'updated_at')
    list_filter = ('patch', 'hero__primary_attr')
    search_fields = ('hero__localized_name',)
    inlines = [HeroBuildInline]
    ordering = ('-updated_at',)

admin.site.register(StratzPatch)