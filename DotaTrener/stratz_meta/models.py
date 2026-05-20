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
    """Мета-статистика героя по патчу (Stratz)"""
    hero = models.ForeignKey('coaching.Hero', on_delete=models.CASCADE, related_name='stratz_meta')
    patch = models.ForeignKey(StratzPatch, on_delete=models.CASCADE)
    
    # 🔥 Stratz использует 'Day' суффикс для статистики
    pick_rate = models.FloatField(default=0.0, help_text="% пиков (pickDay)")
    win_rate = models.FloatField(default=0.0, help_text="% побед (winDay)")
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