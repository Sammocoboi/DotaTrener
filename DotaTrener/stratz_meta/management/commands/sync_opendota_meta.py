from django.core.management.base import BaseCommand

from stratz_meta.services.opendota_client import OpenDotaClient
from stratz_meta.services.sync import StratzSyncService


class Command(BaseCommand):
    help = (
        "Синхронизация мета героев из OpenDota API "
        "(не требует STRATZ_API_KEY, данные актуальнее)."
    )

    def add_arguments(self, parser):
        parser.add_argument("--patch", type=str, default="7.41c", help="Версия патча")
        parser.add_argument("--limit", type=int, help="Ограничить число героев")
        parser.add_argument("--hero-ids", type=str, help="ID героев через запятую")
        parser.add_argument("--skip-builds", action="store_true", help="Без билдов")

    def handle(self, *args, **options):
        client = OpenDotaClient()
        service = StratzSyncService.__new__(StratzSyncService)
        service.client = None
        service.request_delay = 0
        service.builds_take = 100

        self.stdout.write("Fetching hero stats from OpenDota...")
        stats_map = client.get_hero_stats_map()
        hero_map = client.get_hero_map()

        if not stats_map:
            self.stdout.write(self.style.ERROR("OpenDota не вернул данных"))
            return

        from coaching.models import Hero
        from stratz_meta.models import HeroMeta, StratzPatch
        from django.db import transaction
        from datetime import date

        patch_version = options["patch"]
        patch, _ = StratzPatch.objects.update_or_create(
            version=patch_version,
            defaults={"release_date": date.today(), "is_current": True},
        )
        StratzPatch.objects.exclude(pk=patch.pk).update(is_current=False)

        hero_ids_filter = None
        if options.get("hero_ids"):
            hero_ids_filter = [int(x.strip()) for x in options["hero_ids"].split(",") if x.strip()]

        items_to_process = list(stats_map.values())
        if hero_ids_filter:
            items_to_process = [h for h in items_to_process if h.get("id") in hero_ids_filter]
        if options.get("limit"):
            items_to_process = items_to_process[:options["limit"]]

        total = len(items_to_process)
        success = 0
        failed = 0
        self.stdout.write(f"Syncing {total} heroes for patch {patch_version}...")

        with transaction.atomic():
            for i, hero_stat in enumerate(items_to_process):
                hero_id = hero_stat.get("id")
                if not hero_id:
                    failed += 1
                    continue

                meta_data = client.build_meta_for_hero(hero_stat)
                if not meta_data:
                    failed += 1
                    continue

                hero_info = hero_map.get(hero_id, {})
                name = hero_info.get("name") or hero_stat.get("name") or ""
                localized = (
                    hero_info.get("localized_name")
                    or hero_stat.get("localized_name")
                    or f"Hero {hero_id}"
                )
                short_name = meta_data["shortName"]
                image_url = meta_data["image_url"]
                primary_attr = meta_data["primary_attr"]

                hero_obj, _ = Hero.objects.update_or_create(
                    steam_id=int(hero_id),
                    defaults={
                        "name": name[:100],
                        "localized_name": localized[:100],
                        "primary_attr": primary_attr,
                        "image_url": image_url,
                    },
                )

                HeroMeta.objects.update_or_create(
                    hero=hero_obj,
                    patch=patch,
                    defaults={
                        "pick_rate": meta_data["pick_rate"],
                        "win_rate": meta_data["win_rate"],
                        "ban_rate": meta_data["ban_rate"],
                        "games_played": meta_data["games_played"],
                        "roles": {},
                        "avg_kills": meta_data.get("avg_kills"),
                        "avg_deaths": meta_data.get("avg_deaths"),
                        "avg_assists": meta_data.get("avg_assists"),
                        "avg_gpm": meta_data.get("avg_gpm"),
                        "avg_xpm": meta_data.get("avg_xpm"),
                        "avg_last_hits": meta_data.get("avg_last_hits"),
                        "avg_denies": meta_data.get("avg_denies"),
                        "avg_networth": meta_data.get("avg_networth"),
                        "avg_hero_damage": meta_data.get("avg_hero_damage"),
                        "avg_tower_damage": meta_data.get("avg_tower_damage"),
                        "avg_kda": meta_data.get("avg_kda"),
                        "avg_kill_participation": meta_data.get("avg_kill_participation"),
                    },
                )
                success += 1
                self.stdout.write(f"  [{i+1}/{total}] {localized} - WR {meta_data['win_rate']}%")

        self.stdout.write(
            self.style.SUCCESS(
                f"OpenDota sync завершён: {success}/{total} успешно, ошибок {failed}"
            )
        )
