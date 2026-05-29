from django.core.management.base import BaseCommand
from stratz_meta.services import StratzClient


class Command(BaseCommand):
    help = "Показать доступные патчи из Stratz API"

    def handle(self, *args, **options):
        client = StratzClient()
        versions = client.fetch_patches()

        if not versions:
            self.stdout.write(self.style.WARNING("Stratz не вернул патчей"))
            return

        self.stdout.write(f"Доступно {len(versions)} патчей:\n")
        for i, v in enumerate(versions):
            vid = v.get("id")
            name = v.get("name") or str(vid)
            marker = " ← latest" if i == 0 else ""
            self.stdout.write(f"  {name} (id={vid}){marker}")

        self.stdout.write(f"\nПример: python manage.py sync_stratz_meta --patch {versions[0].get('name', '')}")
