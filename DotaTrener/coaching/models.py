from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


class Player(models.Model):
    """Профиль игрока, который запрашивает разборы"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='player_profile')
    steam_account_id = models.BigIntegerField(
        null=True, blank=True, unique=True,
        help_text="32-bit Steam Account ID (Stratz, OpenDota)",
    )
    steam_id_64 = models.BigIntegerField(
        null=True, blank=True,
        help_text="64-bit Steam ID (Steam OpenID)",
    )
    stratz_token = models.CharField(
        max_length=500, blank=True, default="",
        help_text="Персональный Stratz API токен (stratz.com/api → скопировать)",
    )
    current_mmr = models.IntegerField(default=0, help_text="Текущий рейтинг MMR")
    peak_mmr = models.IntegerField(default=0)
    favorite_role = models.CharField(max_length=50, blank=True, null=True)
    is_coach = models.BooleanField(default=False, help_text="Зарегистрирован как тренер")
    avatar_url = models.CharField(max_length=500, blank=True, default="", help_text="URL аватарки")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Player: {self.user.username} (MMR: {self.current_mmr})"

    class Meta:
        verbose_name = "Игрок"
        verbose_name_plural = "Игроки"


class Coach(models.Model):
    """Профиль тренера"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='coach_profile')
    title = models.CharField(max_length=200, blank=True, default="", help_text="Звание (напр. Immortal Coach, Pro Coach)")
    specialization = models.CharField(max_length=100, blank=True, help_text="Специализация (позиция, герои, меты)")
    bio = models.TextField(blank=True)
    rating = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(5.0)])
    mmr_verified = models.IntegerField(default=0, help_text="MMR на момент верификации тренера")
    mmr_verified_at = models.DateTimeField(null=True, blank=True, help_text="Дата последней верификации MMR")
    social_links = models.JSONField(default=dict, blank=True, help_text="Соцсети: {\"telegram\": \"...\", \"discord\": \"...\"}")
    created_at = models.DateTimeField(auto_now_add=True)

    def is_eligible(self) -> bool:
        return self.mmr_verified >= 80

    def __str__(self):
        return self.title or f"Coach: {self.user.username}"

    class Meta:
        verbose_name = "Тренер"
        verbose_name_plural = "Тренеры"


class CoachReview(models.Model):
    """Отзыв пользователя о тренере"""
    coach = models.ForeignKey(Coach, on_delete=models.CASCADE, related_name='coach_reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='coach_reviews_left')
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Оценка 1-5"
    )
    text = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['coach', 'reviewer']
        verbose_name = "Отзыв о тренере"
        verbose_name_plural = "Отзывы о тренерах"

    def __str__(self):
        return f"Review for {self.coach.user.username} by {self.reviewer.username} ({self.rating})"


class CoachVideo(models.Model):
    """Видео тренера (ролик до 60 минут)"""
    coach = models.ForeignKey(Coach, on_delete=models.CASCADE, related_name='videos')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    file_url = models.CharField(max_length=1000, help_text="URL видео или путь к файлу")
    thumbnail_url = models.URLField(max_length=500, blank=True, default="")
    duration_seconds = models.PositiveIntegerField(default=0, help_text="Длительность в секундах (макс 3600)")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Цена в USD (0 = бесплатно)")
    view_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Видео тренера"
        verbose_name_plural = "Видео тренеров"

    def __str__(self):
        return f"{self.title} by {self.coach.user.username}"


class CoachService(models.Model):
    """Услуга тренера"""
    coach = models.ForeignKey(Coach, on_delete=models.CASCADE, related_name='services')
    title = models.CharField(max_length=200, help_text="Название услуги")
    description = models.TextField(blank=True, help_text="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Цена в USD/RUB")
    duration_minutes = models.IntegerField(default=60, help_text="Длительность в минутах")
    video = models.ForeignKey(
        CoachVideo, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='services', help_text="Видео, привязанное к услуге"
    )
    is_active = models.BooleanField(default=True, help_text="Активна ли услуга")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} (${self.price})"

    class Meta:
        verbose_name = "Услуга тренера"
        verbose_name_plural = "Услуги тренеров"


class Conversation(models.Model):
    """Чат между пользователем и тренером"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="conversations_as_user")
    coach = models.ForeignKey(Coach, on_delete=models.CASCADE, related_name="conversations")
    service = models.ForeignKey(CoachService, on_delete=models.SET_NULL, null=True, blank=True, help_text="Услуга, с которой начался разговор")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        verbose_name = "Чат"
        verbose_name_plural = "Чаты"

    def __str__(self):
        return f"{self.user.username} - {self.coach.user.username}"


class Message(models.Model):
    """Сообщение в чате"""
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"

    def __str__(self):
        return f"{self.sender.username}: {self.text[:50]}"


class CoachApplication(models.Model):
    """Заявка на становление тренером"""
    STATUS_CHOICES = [
        ("pending", "На рассмотрении"),
        ("accepted", "Принята"),
        ("rejected", "Отклонена"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="coach_applications")
    message = models.TextField(blank=True, help_text="Почему хочешь стать тренером?")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="reviewed_applications",
    )

    def __str__(self):
        return f"Application: {self.user.username} ({self.status})"

    class Meta:
        verbose_name = "Заявка тренера"
        verbose_name_plural = "Заявки тренеров"
        ordering = ["-created_at"]


class Subscription(models.Model):
    """Подписка тренера (ежемесячная)"""
    PLAN_CHOICES = [
        ("monthly", "Ежемесячная"),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="subscription")
    is_active = models.BooleanField(default=False)
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default="monthly")
    started_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        status = "активна" if self.is_active else "неактивна"
        return f"Subscription: {self.user.username} ({status})"

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"


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


class Item(models.Model):
    """Предмет Dota 2 (синхронизация из Stratz API)"""
    steam_id = models.PositiveIntegerField(unique=True, help_text="Item ID из Dota 2 API")
    name = models.CharField(max_length=200, blank=True, default="")
    display_name = models.CharField(max_length=200, blank=True, default="")
    short_name = models.CharField(max_length=100, blank=True, default="")
    image_url = models.URLField(max_length=500, blank=True, default="")

    description = models.TextField(blank=True, default="", help_text="Описание предмета")
    lore = models.TextField(blank=True, default="", help_text="Лор / flavor text")
    notes = models.JSONField(blank=True, null=True, help_text="Примечания (список строк)")
    attributes_text = models.JSONField(blank=True, null=True, help_text="Атрибуты (список строк из language)")

    cost = models.IntegerField(default=0, help_text="Стоимость в золоте")
    mana_cost = models.JSONField(blank=True, null=True, help_text="Стоимость маны по уровням")
    cooldown = models.JSONField(blank=True, null=True, help_text="Кулдаун по уровням")
    cast_range = models.JSONField(blank=True, null=True, help_text="Дальность применения")
    shop_tags = models.CharField(max_length=200, blank=True, default="")
    quality = models.CharField(max_length=50, blank=True, default="")

    is_sellable = models.BooleanField(default=True)
    is_droppable = models.BooleanField(default=True)
    is_purchasable = models.BooleanField(default=True)
    is_stackable = models.BooleanField(default=False)
    is_support = models.BooleanField(default=False)
    is_recipe = models.BooleanField(default=False)
    needs_components = models.BooleanField(default=False)

    neutral_item_tier = models.CharField(max_length=20, blank=True, default="", help_text="Тир нейтрального предмета")
    attributes = models.JSONField(blank=True, null=True, help_text="Атрибуты предмета [{name, value}]")
    components = models.JSONField(blank=True, null=True, help_text="ID предметов-компонентов")

    api_data = models.JSONField(blank=True, null=True, help_text="Сырой JSON из API")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.display_name or self.name or f"Item {self.steam_id}"

    class Meta:
        verbose_name = "Предмет"
        verbose_name_plural = "Предметы"


class Ability(models.Model):
    """Способность Dota 2 (синхронизация из Stratz API)"""
    steam_id = models.PositiveIntegerField(unique=True, help_text="Ability ID из Dota 2 API")
    name = models.CharField(max_length=200, blank=True, default="")
    display_name = models.CharField(max_length=200, blank=True, default="")
    image_url = models.URLField(max_length=500, blank=True, default="")

    description = models.JSONField(blank=True, null=True, help_text="Описание способности (список строк)")
    lore = models.TextField(blank=True, default="", help_text="Лор")
    notes = models.JSONField(blank=True, null=True, help_text="Примечания (список строк)")
    attributes_text = models.JSONField(blank=True, null=True, help_text="Атрибуты (список строк)")
    aghanim_description = models.TextField(blank=True, default="", help_text="Описание апгрейда Аганима")
    shard_description = models.TextField(blank=True, default="", help_text="Описание апгрейда Шарда")

    ability_type = models.IntegerField(default=0, help_text="Тип способности (0=basic, 1=ultimate, ...)")
    behavior = models.BigIntegerField(default=0, help_text="Битовая маска поведения")
    unit_damage_type = models.IntegerField(default=0, help_text="Тип урона")
    spell_immunity = models.IntegerField(default=0, help_text="Взаимодействие с spell immunity")
    max_level = models.SmallIntegerField(default=4, help_text="Максимальный уровень")
    is_ultimate = models.BooleanField(default=False)
    has_scepter_upgrade = models.BooleanField(default=False)
    has_shard_upgrade = models.BooleanField(default=False)
    is_innate = models.BooleanField(default=False, help_text="Врождённая способность")
    is_talent = models.BooleanField(default=False, help_text="Талант")

    cooldown = models.JSONField(blank=True, null=True, help_text="Кулдаун по уровням")
    mana_cost = models.JSONField(blank=True, null=True, help_text="Стоимость маны по уровням")
    damage = models.JSONField(blank=True, null=True, help_text="Урон по уровням")
    cast_range = models.JSONField(blank=True, null=True, help_text="Дальность по уровням")
    cast_point = models.JSONField(blank=True, null=True, help_text="Задержка применения")
    channel_time = models.JSONField(blank=True, null=True, help_text="Время канала")
    duration = models.CharField(max_length=100, blank=True, default="", help_text="Длительность")
    charges = models.CharField(max_length=100, blank=True, default="", help_text="Заряды")

    attributes = models.JSONField(blank=True, null=True, help_text="Атрибуты [{name, value}]")

    api_data = models.JSONField(blank=True, null=True, help_text="Сырой JSON из API")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.display_name or self.name or f"Ability {self.steam_id}"

    class Meta:
        verbose_name = "Способность"
        verbose_name_plural = "Способности"


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

