"""Заполнить HeroEndgameLoadout из существующих HeroBuild (без полного resync)."""
from django.core.management.base import BaseCommand

from stratz_meta.match_items import (
    endgame_build_from_builds_data,
    pick_titan_endgame_sequence,
    sequence_to_slot_defaults,
)
from stratz_meta.models import HeroBuild, HeroEndgameLoadout, HeroMeta


class Command(BaseCommand):
    help = "Создать строки endgame (item0_id…item5_id) из HeroBuild в БД"

    def handle(self, *args, **options):
        created = 0
        for meta in HeroMeta.objects.select_related("hero", "patch").iterator():
            builds = list(
                HeroBuild.objects.filter(hero_meta=meta, build_type="item").values(
                    "build_type", "sequence", "games", "win_rate", "role"
                )
            )
            if not builds:
                continue

            builds_data = [
                {
                    "build_type": b["build_type"],
                    "sequence": b["sequence"],
                    "games": b["games"],
                    "win_rate": b["win_rate"],
                    "role": b["role"] or "",
                }
                for b in builds
            ]
            sequence, games, win_rate = endgame_build_from_builds_data(builds_data)
            if len(sequence) < 2:
                sequence = pick_titan_endgame_sequence(
                    HeroBuild.objects.filter(hero_meta=meta, build_type="item")
                )
                games = 0
                win_rate = 0.0

            if not sequence:
                continue

            HeroEndgameLoadout.objects.update_or_create(
                hero_meta=meta,
                defaults={
                    **sequence_to_slot_defaults(sequence),
                    "games": games,
                    "win_rate": win_rate,
                },
            )
            created += 1

        self.stdout.write(self.style.SUCCESS(f"Обновлено строк endgame: {created}"))
