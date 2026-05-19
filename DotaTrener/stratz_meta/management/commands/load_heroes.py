from django.core.management.base import BaseCommand

from stratz_meta.services import StratzSyncService


class Command(BaseCommand):
    help = "Загрузить/обновить справочник coaching.Hero из Stratz constants"

    def handle(self, *args, **options):
        service = StratzSyncService()
        stats = service.load_heroes()
        self.stdout.write(
            self.style.SUCCESS(
                f"Готово: создано {stats.created}, обновлено {stats.updated}, "
                f"пропущено {stats.skipped}"
            )
        )
