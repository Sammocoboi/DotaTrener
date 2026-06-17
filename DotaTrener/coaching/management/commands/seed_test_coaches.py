from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from coaching.models import Player, Coach, CoachService, Subscription
from django.utils import timezone
from datetime import timedelta

COACHES = [
    {
        "username": "pro_gamer_1",
        "title": "Immortal Coach · Pos 1-2",
        "specialization": "Carry, Mid, Механика игры",
        "bio": "Бывший про-игрок с 10+ годами опыта. Специализируюсь на керри и миде. Помогу поднять MMR с фокусировкой на лейнинг, фарм и принятие решений.",
        "mmr_verified": 85,
        "services": [
            {"title": "Разбор 1 матча", "description": "Полный разбор твоего реплея с указанием ошибок и планом исправления", "price": 20, "duration_minutes": 60},
            {"title": "Коучинг 1 час", "description": "Live coaching с обратной связью в голосовом канале", "price": 35, "duration_minutes": 60},
            {"title": "Пак 5 разборов", "description": "5 полных разборов с отслеживанием прогресса", "price": 80, "duration_minutes": 300},
        ],
    },
    {
        "username": "support_main",
        "title": "Divine Coach · Pos 4-5",
        "specialization": "Саппорт, Вардинг, Роуминг",
        "bio": "Топ-100 саппорт в регионе. Научу правильно вардить, роумить и контролировать карту. Специализация на хард-саппорте.",
        "mmr_verified": 80,
        "services": [
            {"title": "Вардинг мастер-класс", "description": "Урок по установке вардов, девардингу и контролю карты", "price": 15, "duration_minutes": 45},
            {"title": "Разбор матча", "description": "Подробный разбор твоей игры на саппорте", "price": 25, "duration_minutes": 60},
        ],
    },
    {
        "username": "mid_legend",
        "title": "Mid Coach · Immortal 8.5k",
        "specialization": "Мидер, Соло-убийства, Контроль рун",
        "bio": "8.5k MMR мидер. Учу побеждать на линии, контролировать руны и доминировать в мид-гейме. Индивидуальный подход.",
        "mmr_verified": 85,
        "services": [
            {"title": "Интенсив по миду 2ч", "description": "Двухчасовое занятие по мид-лейнингу с практикой", "price": 50, "duration_minutes": 120},
            {"title": "Разбор + игра вместе", "description": "Смотрим твой реплей, потом играем пару каток вместе", "price": 40, "duration_minutes": 90},
        ],
    },
    {
        "username": "offlane_pro",
        "title": "Offlane Specialist",
        "specialization": "Офлейн, Инициация, Тимфайты",
        "bio": "Играю на офлейне с 2016. Помогу стать неубиваемым на линии и научиться правильно инициировать файты.",
        "mmr_verified": 82,
        "services": [
            {"title": "Базовая консультация", "description": "Знакомство, определение проблем, план развития", "price": 10, "duration_minutes": 30},
            {"title": "Полный разбор + план", "description": "Разбор матча + индивидуальный план тренировок на месяц", "price": 45, "duration_minutes": 90},
            {"title": "3 занятия", "description": "Три полноценных занятия с разборами и совместной игрой", "price": 100, "duration_minutes": 360},
        ],
    },
    {
        "username": "draft_king",
        "title": "Draft & Strategy Coach",
        "specialization": "Драфты, Меты, Контр-пики",
        "bio": "Аналитик с опытом работы в киберспортивной организации. Помогу с драфтами, пониманием меты и контр-пиками.",
        "mmr_verified": 80,
        "services": [
            {"title": "Анализ драфта", "description": "Разбор твоих драфтов + реплеи с фокусом на пики", "price": 20, "duration_minutes": 60},
            {"title": "Мета-гид по патчу", "description": "Полный разбор текущего патча: сильные герои, стратегии, имбы", "price": 30, "duration_minutes": 60},
        ],
    },
]


class Command(BaseCommand):
    help = "Создать тестовых тренеров с услугами"

    def handle(self, *args, **options):
        created_count = 0
        for data in COACHES:
            username = data["username"]
            user, user_created = User.objects.get_or_create(
                username=username,
                defaults={
                    "first_name": username.replace("_", " ").title(),
                },
            )
            if user_created:
                user.set_password("test123456")
                user.save()

            player, _ = Player.objects.get_or_create(user=user)
            player.is_coach = True
            player.save(update_fields=["is_coach"])

            coach, coach_created = Coach.objects.get_or_create(
                user=user,
                defaults={
                    "title": data["title"],
                    "specialization": data["specialization"],
                    "bio": data["bio"],
                    "mmr_verified": data["mmr_verified"],
                    "rating": 5.0,
                },
            )
            if not coach_created:
                coach.title = data["title"]
                coach.specialization = data["specialization"]
                coach.bio = data["bio"]
                coach.mmr_verified = data["mmr_verified"]
                coach.rating = 5.0
                coach.save()

            Subscription.objects.update_or_create(
                user=user,
                defaults={
                    "is_active": True,
                    "plan": "monthly",
                    "started_at": timezone.now(),
                    "expires_at": timezone.now() + timedelta(days=365),
                },
            )

            for svc_data in data["services"]:
                CoachService.objects.get_or_create(
                    coach=coach,
                    title=svc_data["title"],
                    defaults=svc_data,
                )

            created_count += 1
            self.stdout.write(f"  {'Created' if user_created else 'Updated'}: {username}")

        self.stdout.write(self.style.SUCCESS(f"Done. {created_count} coaches synced."))
