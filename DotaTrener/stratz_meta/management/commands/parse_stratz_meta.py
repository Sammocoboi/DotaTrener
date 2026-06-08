# stratz_meta/management/commands/parse_stratz_meta.py
import requests
from datetime import date
from django.core.management.base import BaseCommand
from django.db import transaction
from coaching.models import Hero
from stratz_meta.models import StratzPatch, HeroMeta

OPEN_DOTA_URL = "https://api.opendota.com/api/heroStats"


class Command(BaseCommand):
    help = (
        "Синхронизация мета-статистики героев через OpenDota (fallback). "
        "Для Stratz используйте: python manage.py sync_stratz_meta"
    )

    def add_arguments(self, parser):
        parser.add_argument('--patch', type=str, default='current', help="Версия патча для записи в БД")

    def handle(self, *args, **options):
        patch_version = options['patch']
        
        # 1️ Создаём/обновляем запись патча
        patch, _ = StratzPatch.objects.update_or_create(
            version=patch_version,
            defaults={'release_date': date.today(), 'is_current': (patch_version == 'current')}
        )
        self.stdout.write(f"Zagruzka meta-dannyh s OpenDota dlya patch {patch.version}...")

        # 2️ Загружаем данные
        try:
            resp = requests.get(OPEN_DOTA_URL, timeout=60)
            resp.raise_for_status()
            heroes_data = resp.json()
        except requests.RequestException as e:
            self.stderr.write(self.style.ERROR(f"Oshibka seti: {e}"))
            return

        if not isinstance(heroes_data, list):
            self.stderr.write(self.style.ERROR("Nevernyj format otveta ot OpenDota"))
            return

        saved_count = 0
        with transaction.atomic():
            for h in heroes_data:
                # OpenDota ID совпадает с steam_id в Dota 2
                hero_id = h.get('id')
                try:
                    hero_obj = Hero.objects.get(steam_id=hero_id)
                except Hero.DoesNotExist:
                    continue  # Пропускаем, если герой не в справочнике

                # OpenDota отдаёт win/pick/ban как доли (0.0 - 1.0). Конвертируем в %.
                def to_percent(val):
                    v = val or 0
                    return v * 100 if v <= 1.0 else v

                win_rate = round(to_percent(h.get('win')), 2)
                pick_rate = round(to_percent(h.get('pick')), 2)
                ban_rate = round(to_percent(h.get('ban')), 2)
                games = int(h.get('games_played') or 0)

                HeroMeta.objects.update_or_create(
                    hero=hero_obj,
                    patch=patch,
                    defaults={
                        'win_rate': win_rate,
                        'pick_rate': pick_rate,
                        'ban_rate': ban_rate,
                        'games_played': games,
                        'roles': {}
                    }
                )
                saved_count += 1

        self.stdout.write(self.style.SUCCESS(f"Uspeshno sohraneno meta-dannyh dlya {saved_count} geroev."))