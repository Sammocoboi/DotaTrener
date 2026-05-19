from django.core.management.base import BaseCommand
from django.db import transaction

from stratz_meta.models import HeroBuild
from stratz_meta.services import StratzClient


class Command(BaseCommand):
    help = "Обновить name в HeroBuild.sequence по справочнику Stratz (без полного resync)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Только показать примеры, не сохранять",
        )

    def handle(self, *args, **options):
        client = StratzClient()
        client.load_item_catalog()
        client.load_ability_catalog()

        builds = HeroBuild.objects.select_related("hero_meta__hero").iterator()
        updated = 0
        samples = []

        with transaction.atomic():
            for build in builds:
                if not build.sequence:
                    continue
                new_sequence = [
                    client.enrich_sequence_entry(entry, build.build_type)
                    for entry in build.sequence
                ]
                if new_sequence == build.sequence:
                    continue
                if options["dry_run"]:
                    if len(samples) < 3:
                        samples.append((build.id, build.sequence[:2], new_sequence[:2]))
                    updated += 1
                    continue
                build.sequence = new_sequence
                build.save(update_fields=["sequence"])
                updated += 1

        if options["dry_run"]:
            for build_id, old, new in samples:
                self.stdout.write(f"Build #{build_id}:")
                self.stdout.write(f"  was: {old}")
                self.stdout.write(f"  now: {new}")
        self.stdout.write(
            self.style.SUCCESS(
                f"{'Would update' if options['dry_run'] else 'Updated'} {updated} builds"
            )
        )
