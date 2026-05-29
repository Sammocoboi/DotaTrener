from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


class Player(models.Model):
    """Профиль игрока, который запрашивает разборы"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='player_profile')
    current_mmr = models.IntegerField(default=0, help_text="Текущий рейтинг MMR")
    peak_mmr = models.IntegerField(default=0)
    favorite_role = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Player: {self.user.username} (MMR: {self.current_mmr})"

    class Meta:
        verbose_name = "Игрок"
        verbose_name_plural = "Игроки"


class Coach(models.Model):
    """Профиль тренера"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='coach_profile')
    specialization = models.CharField(max_length=100, blank=True, help_text="Специализация (позиция, герои, меты)")
    bio = models.TextField(blank=True)
    rating = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(5.0)])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Coach: {self.user.username}"

    class Meta:
        verbose_name = "Тренер"
        verbose_name_plural = "Тренеры"


class Hero(models.Model):
    """Справочник героев (заполняется автоматически через Steam/OpenDota API)"""
    steam_id = models.PositiveIntegerField(unique=True, help_text="Hero ID из Steam API")
    name = models.CharField(max_length=100)
    localized_name = models.CharField(max_length=100)
    primary_attr = models.CharField(
        max_length=20,
        choices=[('str', 'Сила'), ('agi', 'Ловкость'), ('int', 'Интеллект'), ('uni', 'Универсал')]
    )
    image_url = models.URLField(max_length=500, blank=True, default="")
    roles = models.JSONField(blank=True, null=True, help_text="Список ролей, напр. ['Carry', 'Nuker']")

    def __str__(self):
        return self.localized_name

    class Meta:
        verbose_name = "Герой"
        verbose_name_plural = "Герои"


class Match(models.Model):
    """Матч игрока с базовой статистикой"""
    SIDE_CHOICES = [('radiant', 'Свет'), ('dire', 'Тьма')]
    RESULT_CHOICES = [('win', 'Победа'), ('loss', 'Поражение')]
    LOBBY_CHOICES = [('ranked', 'Рейтинг'), ('normal', 'Обычная'), ('tournament', 'Турнир')]

    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='matches')
    match_id = models.CharField(max_length=50, unique=True, help_text="ID матча из OpenDota API")
    hero = models.ForeignKey(Hero, on_delete=models.SET_NULL, null=True, blank=True)
    player_side = models.CharField(max_length=10, choices=SIDE_CHOICES)
    result = models.CharField(max_length=10, choices=RESULT_CHOICES)
    lobby_type = models.CharField(max_length=20, choices=LOBBY_CHOICES, default='ranked')
    duration_seconds = models.PositiveIntegerField()
    played_at = models.DateTimeField(default=timezone.now)

    # Статистика игрока в этом матче
    kills = models.PositiveIntegerField(default=0)
    deaths = models.PositiveIntegerField(default=0)
    assists = models.PositiveIntegerField(default=0)
    gpm = models.PositiveIntegerField(default=0)
    xpm = models.PositiveIntegerField(default=0)
    last_hits = models.PositiveIntegerField(default=0)
    denies = models.PositiveIntegerField(default=0)

    # Гибкое поле для сырых данных API (позволяет расширять без миграций)
    api_data = models.JSONField(blank=True, null=True, help_text="Полный JSON матча с OpenDota")

    def __str__(self):
        return f"Match {self.match_id} | {self.hero} | {self.get_result_display()}"

    class Meta:
        ordering = ['-played_at']
        indexes = [
            models.Index(fields=['player', 'played_at']),
            models.Index(fields=['match_id']),
        ]
        verbose_name = "Матч"
        verbose_name_plural = "Матчи"


class MistakeCategory(models.Model):
    """Категории ошибок для систематизации разбора"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория ошибки"
        verbose_name_plural = "Категории ошибок"


class Review(models.Model):
    """Разбор матча тренером"""
    STATUS_CHOICES = [('pending', 'Ожидает'), ('in_progress', 'В работе'), ('completed', 'Завершён')]

    match = models.OneToOneField(Match, on_delete=models.CASCADE, related_name='review')
    coach = models.ForeignKey(Coach, on_delete=models.CASCADE, related_name='reviews')
    overall_score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Общая оценка выступления (1-10)"
    )
    summary = models.TextField(help_text="Итоговые рекомендации и паттерны")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Review by {self.coach.user.username} for {self.match.match_id}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Разбор матча"
        verbose_name_plural = "Разборы матчей"


class Mistake(models.Model):
    """Конкретная ошибка с привязкой ко времени матча"""
    SEVERITY_CHOICES = [('low', 'Низкая'), ('medium', 'Средняя'), ('high', 'Высокая'), ('critical', 'Критическая')]

    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='mistakes')
    category = models.ForeignKey(MistakeCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='mistakes')
    timestamp_seconds = models.PositiveIntegerField(help_text="Время в матче (секунды). Используется для клипов в реплее")
    description = models.TextField(help_text="Что произошло и почему это ошибка")
    recommendation = models.TextField(help_text="Как исправить/избежать в будущем")
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.get_severity_display()}] {self.category or 'Без категории'} @ {self.timestamp_seconds}s"

    class Meta:
        ordering = ['timestamp_seconds']
        verbose_name = "Ошибка"
        verbose_name_plural = "Ошибки"

