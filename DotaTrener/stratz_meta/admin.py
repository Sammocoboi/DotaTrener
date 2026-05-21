from django.contrib import admin
from .models import StratzPatch, HeroMeta, HeroBuild, HeroEndgameLoadout

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

@admin.register(HeroEndgameLoadout)
class HeroEndgameLoadoutAdmin(admin.ModelAdmin):
    list_display = (
        "hero_name",
        "patch_version",
        "slot0",
        "slot1",
        "slot2",
        "slot3",
        "slot4",
        "slot5",
        "games",
        "updated_at",
    )
    list_select_related = ("hero_meta__hero", "hero_meta__patch")
    search_fields = ("hero_meta__hero__localized_name",)

    @admin.display(description="Герой")
    def hero_name(self, obj):
        return obj.hero_meta.hero.localized_name

    @admin.display(description="Патч")
    def patch_version(self, obj):
        return obj.hero_meta.patch.version

    def _slot_label(self, obj, index: int) -> str:
        from stratz_meta.match_items import format_purchase_time

        item_id = obj.slot_ids()[index]
        if not item_id:
            return "—"
        t = obj.slot_times()[index]
        return f"{item_id} @ {format_purchase_time(t)}"

    @admin.display(description="0")
    def slot0(self, obj):
        return self._slot_label(obj, 0)

    @admin.display(description="1")
    def slot1(self, obj):
        return self._slot_label(obj, 1)

    @admin.display(description="2")
    def slot2(self, obj):
        return self._slot_label(obj, 2)

    @admin.display(description="3")
    def slot3(self, obj):
        return self._slot_label(obj, 3)

    @admin.display(description="4")
    def slot4(self, obj):
        return self._slot_label(obj, 4)

    @admin.display(description="5")
    def slot5(self, obj):
        return self._slot_label(obj, 5)


admin.site.register(StratzPatch)