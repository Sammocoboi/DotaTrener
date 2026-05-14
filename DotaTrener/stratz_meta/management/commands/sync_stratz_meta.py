import time
import requests
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import transaction

from stratz_meta.models import StratzPatch, HeroMeta, HeroBuild
from coaching.models import Hero

STRATZ_GRAPHQL_URL = "https://api.stratz.com/api/graphql"
STRATZ_API_KEY = getattr(settings, "STRATZ_API_KEY", None)

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {STRATZ_API_KEY}" if STRATZ_API_KEY else "",
}

class Command(BaseCommand):
    help = "Синхронизация меты и билдов героев с Stratz GraphQL API"

    def add_arguments(self, parser):
        parser.add_argument('--patch', type=str, default='current', 
                            help="Версия патча (напр. 7.35c). 'current' = актуальный")
        parser.add_argument('--top-builds', type=int, default=5)

    def handle(self, *args, **kwargs):
        patch_version = kwargs['patch']
        top_builds = kwargs['top_builds']

        if not STRATZ_API_KEY:
            self.stderr.write(self.style.ERROR("❌ Укажите STRATZ_API_KEY в settings.py"))
            return

        patch, _ = StratzPatch.objects.update_or_create(
            version=patch_version,
            defaults={'is_current': (patch_version == 'current')}
        )
        self.stdout.write(f"🔄 Синхронизация данных для патча {patch.version}...")

        # GraphQL запрос (адаптируйте поля под актуальную схему Stratz)
        query = """
        query HeroData($patchId: String, $limit: Int) {
          heroMeta(patchId: $patchId) {
            heroId
            pickRate
            winRate
            banRate
            games
            roles
            itemBuilds(limit: $limit) {
              items
              pickRate
              winRate
              games
              role
            }
            skillBuilds(limit: $limit) {
              skills
              pickRate
              winRate
              games
              role
            }
          }
        }
        """

        response = requests.post(
            STRATZ_GRAPHQL_URL,
            json={"query": query, "variables": {"patchId": patch.version, "limit": top_builds}},
            headers=HEADERS,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()

        if 'errors' in data:
            self.stderr.write(self.style.ERROR(f"❌ Ошибка API: {data['errors']}"))
            return

        heroes_data = data.get('data', {}).get('heroMeta', [])
        if not heroes_data:
            self.stdout.write(self.style.WARNING("⚠️ Нет данных. Проверьте патч и API-ключ."))
            return

        with transaction.atomic():
            for h in heroes_data:
                try:
                    hero_obj = Hero.objects.get(steam_id=h['heroId'])
                except Hero.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"⚠️ Герой ID {h['heroId']} отсутствует в coaching.Hero. Пропуск."))
                    continue

                meta, _ = HeroMeta.objects.update_or_create(
                    hero=hero_obj,
                    patch=patch,
                    defaults={
                        'pick_rate': h.get('pickRate', 0),
                        'win_rate': h.get('winRate', 0),
                        'ban_rate': h.get('banRate', 0),
                        'games_played': h.get('games', 0),
                        'roles': h.get('roles', {}),
                    }
                )

                self._sync_builds(meta, h.get('itemBuilds', []), 'item')
                self._sync_builds(meta, h.get('skillBuilds', []), 'skill')
                time.sleep(0.1)

        self.stdout.write(self.style.SUCCESS("✅ Синхронизация завершена."))

    def _sync_builds(self, meta_obj, builds_data, build_type):
        meta_obj.builds.filter(build_type=build_type).delete()
        if not builds_data:
            return

        bulk = []
        for b in builds_data:
            bulk.append(HeroBuild(
                hero_meta=meta_obj,
                build_type=build_type,
                sequence=b.get('items') or b.get('skills', []),
                pick_rate=b.get('pickRate', 0),
                win_rate=b.get('winRate', 0),
                games=b.get('games', 0),
                role=b.get('role')
            ))
        HeroBuild.objects.bulk_create(bulk)