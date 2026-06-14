# stratz_meta/models.py
from django.db import models
import datetime

class StratzPatch(models.Model):
    version = models.CharField(max_length=20, unique=True, primary_key=True)
    release_date = models.DateField(default=datetime.date.today, null=True, blank=True)
    is_current = models.BooleanField(default=False)

    def __str__(self):
        return f"Patch {self.version}"

    class Meta:
        verbose_name = "Патч"
        verbose_name_plural = "Патчи"


class HeroMeta(models.Model):
    """Мета-статистика героя по патчу"""
    SOURCE_CHOICES = [('stratz', 'Stratz'), ('opendota', 'OpenDota')]
    source = models.CharField(max_length=10, choices=SOURCE_CHOICES, default='stratz', help_text="Источник данных")
    hero = models.ForeignKey('coaching.Hero', on_delete=models.CASCADE, related_name='stratz_meta')
    patch = models.ForeignKey(StratzPatch, on_delete=models.CASCADE)
    
    pick_rate = models.FloatField(default=0.0, help_text="% пиков")
    win_rate = models.FloatField(default=0.0, help_text="% побед")
    ban_rate = models.FloatField(default=0.0, help_text="% банов (banDay)")
    games_played = models.PositiveIntegerField(default=0, help_text="gamesPlayed")
    roles = models.JSONField(default=dict, blank=True, help_text="{'Carry': 42.5, 'Mid': 31.0}")
    # Средние показатели по матчам (Stratz heroStats.stats, Divine+ и т.д.)
    avg_kills = models.FloatField(null=True, blank=True)
    avg_deaths = models.FloatField(null=True, blank=True)
    avg_assists = models.FloatField(null=True, blank=True)
    avg_gpm = models.FloatField(null=True, blank=True, help_text="gold/min (оценка из networth, если API null)")
    avg_xpm = models.FloatField(null=True, blank=True, help_text="xp/min (оценка из xp)")
    avg_last_hits = models.FloatField(null=True, blank=True, help_text="cs")
    avg_denies = models.FloatField(null=True, blank=True, help_text="dn")
    avg_networth = models.FloatField(null=True, blank=True)
    avg_hero_damage = models.FloatField(null=True, blank=True)
    avg_tower_damage = models.FloatField(null=True, blank=True)
    avg_kda = models.FloatField(null=True, blank=True)
    avg_kill_participation = models.FloatField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('hero', 'patch')
        verbose_name = "Мета героя (Stratz)"
        verbose_name_plural = "Мета героев"


class HeroEndgameLoadout(models.Model):
    """
    Эталонные 6 слотов предметов в конце игры (титаны) — одна строка на героя и патч.
    Заполняется при sync_stratz_meta.
    """
    hero_meta = models.OneToOneField(
        HeroMeta,
        on_delete=models.CASCADE,
        related_name="endgame_loadout",
    )
    item0_id = models.PositiveIntegerField(
        null=True, blank=True, help_text="Обычно сапоги (itemBootPurchase)"
    )
    item0_time = models.PositiveIntegerField(
        null=True, blank=True, help_text="Секунда покупки (Stratz itemFullPurchase.time)"
    )
    item1_id = models.PositiveIntegerField(null=True, blank=True)
    item1_time = models.PositiveIntegerField(null=True, blank=True)
    item2_id = models.PositiveIntegerField(null=True, blank=True)
    item2_time = models.PositiveIntegerField(null=True, blank=True)
    item3_id = models.PositiveIntegerField(null=True, blank=True)
    item3_time = models.PositiveIntegerField(null=True, blank=True)
    item4_id = models.PositiveIntegerField(null=True, blank=True)
    item4_time = models.PositiveIntegerField(null=True, blank=True)
    item5_id = models.PositiveIntegerField(null=True, blank=True)
    item5_time = models.PositiveIntegerField(null=True, blank=True)
    games = models.PositiveIntegerField(
        default=0,
        help_text="Суммарный matchCount по предметам endgame из Stratz",
    )
    win_rate = models.FloatField(default=0.0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Endgame 6 слотов (титаны)"
        verbose_name_plural = "Endgame 6 слотов (титаны)"

    def slot_ids(self) -> list[int | None]:
        return [
            self.item0_id,
            self.item1_id,
            self.item2_id,
            self.item3_id,
            self.item4_id,
            self.item5_id,
        ]

    def slot_times(self) -> list[int | None]:
        return [
            self.item0_time,
            self.item1_time,
            self.item2_time,
            self.item3_time,
            self.item4_time,
            self.item5_time,
        ]

    def __str__(self) -> str:
        hero = self.hero_meta.hero.localized_name
        filled = sum(1 for i in self.slot_ids() if i)
        return f"{hero} endgame ({filled}/6)"


class HeroBuild(models.Model):
    """Топовые сборки (предметы/скиллы)"""
    TYPE_CHOICES = [('item', 'Предметы'), ('skill', 'Способности')]
    
    hero_meta = models.ForeignKey(HeroMeta, on_delete=models.CASCADE, related_name='builds')
    build_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    sequence = models.JSONField(help_text="Список ID предметов или аббревиатур скиллов")
    pick_rate = models.FloatField(default=0.0, help_text="pickDay")
    win_rate = models.FloatField(default=0.0, help_text="winDay")
    games = models.PositiveIntegerField(default=0)
    role = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        verbose_name = "Билд героя"
        verbose_name_plural = "Билды героев"