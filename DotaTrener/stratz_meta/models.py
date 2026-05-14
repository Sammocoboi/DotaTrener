from django.db import models

class StratzPatch(models.Model):
    version = models.CharField(max_length=20, unique=True, primary_key=True)
    release_date = models.DateField()
    is_current = models.BooleanField(default=False)

    def __str__(self):
        return f"Patch {self.version}"

    class Meta:
        verbose_name = "Патч"
        verbose_name_plural = "Патчи"


class HeroMeta(models.Model):
    """Мета-статистика героя по патчу (winrate, pickrate, роли)"""
    # Ссылка на Hero из приложения coaching
    hero = models.ForeignKey('coaching.Hero', on_delete=models.CASCADE, related_name='stratz_meta')
    patch = models.ForeignKey(StratzPatch, on_delete=models.CASCADE)
    
    pick_rate = models.FloatField(default=0.0, help_text="% пиков")
    win_rate = models.FloatField(default=0.0, help_text="% побед")
    ban_rate = models.FloatField(default=0.0, help_text="% банов")
    games_played = models.PositiveIntegerField(default=0)
    roles = models.JSONField(default=dict, help_text="{'Carry': 42.5, 'Mid': 31.0}")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('hero', 'patch')
        verbose_name = "Мета героя (Stratz)"
        verbose_name_plural = "Мета героев"


class HeroBuild(models.Model):
    """Топовые сборки (предметы/скиллы) с винрейтами"""
    TYPE_CHOICES = [('item', 'Предметы'), ('skill', 'Способности')]
    
    hero_meta = models.ForeignKey(HeroMeta, on_delete=models.CASCADE, related_name='builds')
    build_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    sequence = models.JSONField(help_text="Список ID предметов или аббревиатур скиллов")
    pick_rate = models.FloatField(default=0.0)
    win_rate = models.FloatField(default=0.0)
    games = models.PositiveIntegerField(default=0)
    role = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        verbose_name = "Билд героя"
        verbose_name_plural = "Билды героев"