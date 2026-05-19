from django.core.management.base import BaseCommand

from stratz_meta.services import StratzSyncService


class Command(BaseCommand):
    help = (
        "Синхронизация мета и билдов для ВСЕХ героев Dota 2 из Stratz "
        "(по умолчанию ~126 героев, без --limit). Билды — все доступные."
    )

    def add_arguments(self, parser):
        parser.add_argument("--patch", type=str, help="Версия патча Stratz")
        parser.add_argument(
            "--limit",
            type=int,
            help="Ограничить число героев (только для отладки)",
        )
        parser.add_argument(
            "--hero-ids",
            type=str,
            help="Список ID героев через запятую, например 1,2,3",
        )
        parser.add_argument(
            "--builds-take",
            type=int,
            help="Параметр take для запроса builds (по умолчанию STRATZ_BUILDS_TAKE)",
        )
        parser.add_argument(
            "--rank",
            type=str,
            default="DIVINE_IMMORTAL",
            help="Брекет: DIVINE_IMMORTAL, ALL, LEGEND_ANCIENT и др. (ALL — шире выборка)",
        )
        parser.add_argument(
            "--skip-builds",
            action="store_true",
            help="Синхронизировать только мету, без билдов",
        )
        parser.add_argument(
            "--delay",
            type=float,
            help="Пауза между запросами в секундах",
        )
        parser.add_argument(
            "--no-ensure-heroes",
            action="store_true",
            help="Не вызывать load_heroes перед синхронизацией",
        )

    def handle(self, *args, **options):
        hero_ids = None
        if options.get("hero_ids"):
            hero_ids = [int(x.strip()) for x in options["hero_ids"].split(",") if x.strip()]

        service = StratzSyncService()

        def progress(index, total, label, hero_id):
            self.stdout.write(f"[{index}/{total}] {label} (ID:{hero_id})")

        stats = service.sync_meta(
            patch_version=options.get("patch"),
            hero_ids=hero_ids,
            limit=options.get("limit"),
            rank=options["rank"],
            skip_builds=options["skip_builds"],
            builds_take=options.get("builds_take"),
            ensure_heroes=not options["no_ensure_heroes"],
            delay=options.get("delay"),
            on_progress=progress,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Синхронизация завершена: успешно {stats.success}/{stats.total}, "
                f"ошибок {stats.failed}, билдов сохранено {stats.builds}"
            )
        )
