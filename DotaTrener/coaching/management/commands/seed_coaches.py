import logging
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from coaching.models import Coach, CoachService, CoachVideo, Player, Subscription
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)

COACHES = [
    {
        "username": "coach_immortal",
        "title": "Immortal Coach | 10k MMR",
        "specialization": "Mid Lane, Invoker, Storm Spirit",
        "bio": "Professional Dota 2 coach with 8 years of experience. Immortal rank, peak 10.2k MMR. Specializing in mid lane mechanics, map awareness, and late-game decision making.",
        "rating": 4.8,
        "mmr_verified": 10200,
        "social_links": {"telegram": "@immortal_coach", "discord": "immortal#1234"},
        "services": [
            {
                "title": "1-on-1 Coaching Session (1 hour)",
                "description": "Personal coaching session focusing on your gameplay analysis, hero pool expansion, and strategic improvement.",
                "price": Decimal("25.00"),
                "duration_minutes": 60,
            },
            {
                "title": "Replay Analysis",
                "description": "Detailed analysis of your replay with timestamped mistakes, recommendations, and improvement plan.",
                "price": Decimal("15.00"),
                "duration_minutes": 30,
            },
            {
                "title": "Draft Analysis & Strategy",
                "description": "Analysis of your draft patterns, counter-picking strategy, and team composition optimization.",
                "price": Decimal("20.00"),
                "duration_minutes": 45,
            },
        ],
    },
    {
        "username": "coach_support",
        "title": "Position 5 Specialist | Divine 5",
        "specialization": "Support, Warding, Teamfight",
        "bio": "Former pro player turned coach. Divine 5 rank with deep understanding of support mechanics, warding patterns, and teamfight positioning.",
        "rating": 4.6,
        "mmr_verified": 8700,
        "social_links": {"telegram": "@support_coach", "discord": "support#5678"},
        "services": [
            {
                "title": "Support Mastery Session",
                "description": "Learn optimal warding, pulling, stacking, and teamfight positioning for support role.",
                "price": Decimal("20.00"),
                "duration_minutes": 60,
            },
            {
                "title": "Vision & Map Control",
                "description": "Deep dive into ward placement, dewarding, and how to control the map as a support.",
                "price": Decimal("18.00"),
                "duration_minutes": 45,
            },
        ],
    },
    {
        "username": "coach_carry",
        "title": "Carry Player | Immortal 8k",
        "specialization": "Safe Lane, Farming Patterns, Late Game",
        "bio": "Carry specialist with 6 years of competitive experience. Focus on farming efficiency, item timings, and late-game carry vs carry matchups.",
        "rating": 4.7,
        "mmr_verified": 8900,
        "social_links": {"telegram": "@carry_coach", "discord": "carry#9012"},
        "services": [
            {
                "title": "Carry Bootcamp",
                "description": "Comprehensive carry training: last hitting, farming patterns, item builds, and late-game decision making.",
                "price": Decimal("30.00"),
                "duration_minutes": 90,
            },
            {
                "title": "Farming Efficiency Review",
                "description": "Analyze your farming patterns, identify inefficiencies, and optimize your gold/XP gain.",
                "price": Decimal("15.00"),
                "duration_minutes": 30,
            },
        ],
    },
    {
        "username": "coach_offlane",
        "title": "Offlane Expert | Ancient 7",
        "specialization": "Offlane, Initiation, Space Creation",
        "bio": "Offlane main with strong understanding of lane matchups, initiation timing, and creating space for your team.",
        "rating": 4.4,
        "mmr_verified": 7500,
        "social_links": {"telegram": "@offlane_coach", "discord": "offlane#3456"},
        "services": [
            {
                "title": "Offlane Fundamentals",
                "description": "Master the offlane: creep equilibrium, trading, itemization, and teamfight initiation.",
                "price": Decimal("20.00"),
                "duration_minutes": 60,
            },
            {
                "title": "Hero Pool Expansion",
                "description": "Learn new offlane heroes, their matchups, and optimal playstyles for each.",
                "price": Decimal("22.00"),
                "duration_minutes": 60,
            },
        ],
    },
    {
        "username": "coach_mid",
        "title": "Mid Lane Assassin | Immortal 9k",
        "specialization": "Mid Lane, Ganking, Tempo Control",
        "bio": "Aggressive mid player focused on tempo control, ganking, and snowballing. Former pub star with 9k peak MMR.",
        "rating": 4.9,
        "mmr_verified": 9400,
        "social_links": {"telegram": "@mid_coach", "discord": "mid#7890"},
        "services": [
            {
                "title": "Mid Lane Domination",
                "description": "Learn to dominate your lane: rune control, creep agro, harassment, and kill pressure.",
                "price": Decimal("28.00"),
                "duration_minutes": 60,
            },
            {
                "title": "Ganking & Map Pressure",
                "description": "Master the art of ganking, rotation timing, and creating pressure across the map.",
                "price": Decimal("25.00"),
                "duration_minutes": 45,
            },
            {
                "title": "Full Coaching Package",
                "description": "Complete mid lane training: laning, ganking, itemization, and teamfight participation.",
                "price": Decimal("45.00"),
                "duration_minutes": 120,
            },
        ],
    },
]


class Command(BaseCommand):
    help = "Заполняет базу данных тренерами и услугами (seed data)"

    def handle(self, *args, **options):
        created_coaches = 0
        created_services = 0

        for coach_data in COACHES:
            user, _ = User.objects.get_or_create(
                username=coach_data["username"],
                defaults={
                    "first_name": coach_data["title"].split("|")[0].strip(),
                    "email": f"{coach_data['username']}@dotatrainer.com",
                },
            )

            coach, was_created = Coach.objects.update_or_create(
                user=user,
                defaults={
                    "title": coach_data["title"],
                    "specialization": coach_data["specialization"],
                    "bio": coach_data["bio"],
                    "rating": coach_data["rating"],
                    "mmr_verified": coach_data["mmr_verified"],
                    "social_links": coach_data["social_links"],
                },
            )

            Player.objects.update_or_create(
                user=user,
                defaults={
                    "is_coach": True,
                    "current_mmr": coach_data["mmr_verified"],
                    "peak_mmr": coach_data["mmr_verified"],
                },
            )

            Subscription.objects.update_or_create(
                user=user,
                defaults={
                    "is_active": True,
                    "plan": "monthly",
                    "started_at": timezone.now(),
                    "expires_at": timezone.now() + timedelta(days=365),
                },
            )

            if was_created:
                created_coaches += 1

            for svc_data in coach_data.get("services", []):
                _, svc_created = CoachService.objects.update_or_create(
                    coach=coach,
                    title=svc_data["title"],
                    defaults={
                        "description": svc_data["description"],
                        "price": svc_data["price"],
                        "duration_minutes": svc_data["duration_minutes"],
                        "is_active": True,
                    },
                )
                if svc_created:
                    created_services += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Готово: создано тренеров {created_coaches}, услуг {created_services}"
            )
        )
