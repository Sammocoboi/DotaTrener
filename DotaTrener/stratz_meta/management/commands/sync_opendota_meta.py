import logging
import sys

from django.core.management.base import BaseCommand

from stratz_meta.services.opendota_client import BRACKET_LABELS
from stratz_meta.services.opendota_sync import OpenDotaSyncService

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = (
        "Парсинг меты героев через OpenDota API (бесплатно, без ключа). "
        "Сохраняет данные в HeroMeta как и StratZ sync."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--patch",
            type=str,
            default="7.38",
            help="Версия патча (по умолчанию 7.38)",
        )
        parser.add_argument(
            "--bracket",
            type=str,
            default="immortal",
            choices=list(BRACKET_LABELS.keys()) + ["pro"],
            help="Ранговый брекет: herald, guardian, crusader, archon, legend, ancient, divine, immortal, pro",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Лимит героев (для теста)",
        )
        parser.add_argument(
            "--hero-ids",
            type=str,
            default=None,
            help="ID героев через запятую",
        )
        parser.add_argument(
            "--skip-heroes",
            action="store_true",
            default=False,
            help="Не обновлять справочник героев",
        )

    def handle(self, *args, **options):
        self.stdout.write("=== OpenDota Meta Sync ===")
        self.stdout.write(f"Patch: {options['patch']}, Bracket: {options['bracket']}")

        service = OpenDotaSyncService()
        hero_ids = None
        if options.get("hero_ids"):
            hero_ids = [int(x.strip()) for x in options["hero_ids"].split(",") if x.strip()]

        stats = service.sync_meta(
            patch_version=options["patch"],
            bracket=options["bracket"],
            hero_ids=hero_ids,
            limit=options.get("limit"),
            ensure_heroes=not options["skip_heroes"],
            on_progress=self._on_progress,
        )

        self.stdout.write()
        self.stdout.write(
            self.style.SUCCESS(
                f"Готово: {stats.success}/{stats.total} успешно, "
                f"{stats.failed} ошибок, "
                f"героев создано {stats.heroes_created}"
            )
        )
        if stats.failed > 0:
            sys.exit(1)

    def _on_progress(self, current: int, total: int, label: str, hero_id: int):
        if current % 5 == 0 or current == total:
            self.stdout.write(f"  [{current}/{total}] {label} (ID: {hero_id})")
            self.stdout.flush()
