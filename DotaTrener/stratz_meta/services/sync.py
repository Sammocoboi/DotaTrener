import logging
import time
from dataclasses import dataclass
from datetime import date
from typing import Any, Dict, List, Optional

from django.conf import settings
from django.db import transaction

from coaching.models import Hero
from stratz_meta.match_items import endgame_build_from_builds_data, sequence_to_slot_defaults
from stratz_meta.models import HeroBuild, HeroEndgameLoadout, HeroMeta, StratzPatch

from .stratz_client import StratzClient

logger = logging.getLogger(__name__)

HERO_BATCH_SIZE = 15


@dataclass
class SyncStats:
    total: int = 0
    success: int = 0
    failed: int = 0
    builds: int = 0

    def as_dict(self) -> Dict[str, int]:
        return {
            "total": self.total,
            "success": self.success,
            "failed": self.failed,
            "builds": self.builds,
        }


@dataclass
class HeroLoadStats:
    created: int = 0
    updated: int = 0
    skipped: int = 0


class StratzSyncService:
    def __init__(self, client: Optional[StratzClient] = None):
        self.client = client or StratzClient()
        self.request_delay = settings.STRATZ_REQUEST_DELAY
        self.builds_take = settings.STRATZ_BUILDS_TAKE

    def sync_patches(self, target_version: Optional[str] = None) -> StratzPatch:
        versions = self.client.fetch_patches()
        if versions:
            StratzPatch.objects.update(is_current=False)
            for gv in versions:
                version = gv.get("name") or str(gv.get("id", ""))
                if version:
                    StratzPatch.objects.update_or_create(
                        version=version,
                        defaults={"release_date": None, "is_current": False},
                    )
            target = target_version or versions[0].get("name") or str(versions[0].get("id", ""))
        else:
            target = target_version or settings.STRATZ_PATCH_VERSION
            StratzPatch.objects.update(is_current=False)
            StratzPatch.objects.update_or_create(
                version=target,
                defaults={"release_date": date.today(), "is_current": False},
            )

        patch = StratzPatch.objects.get(version=target)
        patch.is_current = True
        patch.save(update_fields=["is_current"])
        self.client.get_version_map()
        return patch

    def load_heroes(self) -> HeroLoadStats:
        heroes = self.client.fetch_heroes()
        attrs = self.client.fetch_hero_primary_attrs()
        stats = HeroLoadStats()
        if not heroes:
            return stats

        with transaction.atomic():
            for hero in heroes:
                hero_id = hero.get("id")
                if not hero_id:
                    stats.skipped += 1
                    continue
                name = hero.get("name") or hero.get("shortName") or ""
                localized = (
                    hero.get("displayName")
                    or hero.get("shortName")
                    or name
                    or f"Hero {hero_id}"
                )
                primary_attr = attrs.get(int(hero_id), "str")
                _, created = Hero.objects.update_or_create(
                    steam_id=int(hero_id),
                    defaults={
                        "name": name[:100],
                        "localized_name": localized[:100],
                        "primary_attr": primary_attr,
                    },
                )
                if created:
                    stats.created += 1
                else:
                    stats.updated += 1
        return stats

    def resolve_hero(
        self, api_hero: Dict[str, Any], ensure: bool = True
    ) -> Optional[Hero]:
        hero_id = api_hero.get("id")
        if hero_id is None:
            return None
        hero = Hero.objects.filter(steam_id=int(hero_id)).first()
        if hero or not ensure:
            return hero
        name = api_hero.get("name") or ""
        localized = api_hero.get("displayName") or name or f"Hero {hero_id}"
        return Hero.objects.create(
            steam_id=int(hero_id),
            name=name[:100],
            localized_name=localized[:100],
            primary_attr="str",
        )

    def save_hero_meta(
        self,
        meta_data: Dict[str, Any],
        hero_obj: Hero,
        patch_obj: StratzPatch,
        builds_data: List[Dict[str, Any]],
    ) -> int:
        defaults = {
            "pick_rate": meta_data["pick_rate"],
            "win_rate": meta_data["win_rate"],
            "ban_rate": meta_data["ban_rate"],
            "games_played": meta_data["games_played"],
            "roles": meta_data.get("roles", {}),
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
        }
        meta, _ = HeroMeta.objects.update_or_create(
            hero=hero_obj,
            patch=patch_obj,
            defaults=defaults,
        )
        HeroBuild.objects.filter(hero_meta=meta).delete()
        if builds_data:
            HeroBuild.objects.bulk_create(
                [
                    HeroBuild(
                        hero_meta=meta,
                        build_type=row["build_type"],
                        sequence=row["sequence"],
                        pick_rate=row["pick_rate"],
                        win_rate=row["win_rate"],
                        games=row["games"],
                        role=row["role"] or None,
                    )
                    for row in builds_data
                ]
            )

        sequence, eg_games, eg_wr = endgame_build_from_builds_data(builds_data)
        if sequence:
            HeroEndgameLoadout.objects.update_or_create(
                hero_meta=meta,
                defaults={
                    **sequence_to_slot_defaults(sequence),
                    "games": eg_games,
                    "win_rate": eg_wr,
                },
            )
        else:
            HeroEndgameLoadout.objects.filter(hero_meta=meta).delete()

        return len(builds_data)

    def sync_meta(
        self,
        *,
        patch_version: Optional[str] = None,
        hero_ids: Optional[List[int]] = None,
        limit: Optional[int] = None,
        rank: str = "DIVINE_IMMORTAL",
        skip_builds: bool = False,
        builds_take: Optional[int] = None,
        ensure_heroes: bool = True,
        delay: Optional[float] = None,
        on_progress=None,
    ) -> SyncStats:
        patch = self.sync_patches(target_version=patch_version)
        if ensure_heroes:
            self.load_heroes()
        self.client.load_item_catalog()
        self.client.load_ability_catalog()

        heroes = self.client.fetch_heroes()
        if not heroes:
            return SyncStats()

        if hero_ids:
            hero_id_set = set(hero_ids)
            heroes = [h for h in heroes if h.get("id") in hero_id_set]
        if limit:
            heroes = heroes[:limit]

        game_version_id = self.client.resolve_game_version_id(patch.version)
        if game_version_id is None:
            logger.error("Cannot resolve gameVersionId for patch %s", patch.version)
            return SyncStats(total=len(heroes), failed=len(heroes))

        take = builds_take if builds_take is not None else self.builds_take
        pause = delay if delay is not None else self.request_delay
        stats = SyncStats(total=len(heroes))
        started = time.time()
        processed = 0

        for batch_start in range(0, len(heroes), HERO_BATCH_SIZE):
            batch = heroes[batch_start : batch_start + HERO_BATCH_SIZE]
            batch_ids = [int(h["id"]) for h in batch if h.get("id") is not None]
            meta_map = self.client.fetch_meta_batch(batch_ids, game_version_id, rank)
            time.sleep(pause)

            for api_hero in batch:
                processed += 1
                label = api_hero.get("displayName") or api_hero.get("name")
                hero_id = int(api_hero["id"])
                if on_progress:
                    on_progress(processed, stats.total, label, hero_id)

                hero_obj = self.resolve_hero(api_hero, ensure=ensure_heroes)
                if not hero_obj:
                    stats.failed += 1
                    continue

                meta = meta_map.get(hero_id)
                if not meta:
                    logger.warning("No meta for hero %s (%s)", label, hero_id)
                    stats.failed += 1
                    continue

                builds: List[Dict[str, Any]] = []
                if not skip_builds:
                    for build_type in ("item", "skill"):
                        builds.extend(
                            self.client.fetch_hero_builds(
                                hero_id,
                                build_type,
                                patch_id=patch.version,
                                rank=rank,
                                take=take,
                            )
                        )
                        time.sleep(pause)

                try:
                    count = self.save_hero_meta(meta, hero_obj, patch, builds)
                    stats.success += 1
                    stats.builds += count
                    logger.info(
                        "[%s/%s] %s: WR=%s%% games=%s builds=%s",
                        processed,
                        stats.total,
                        label,
                        meta["win_rate"],
                        meta["games_played"],
                        count,
                    )
                except Exception as exc:
                    logger.exception("Failed to save hero %s: %s", hero_id, exc)
                    stats.failed += 1

            if batch_start + HERO_BATCH_SIZE < len(heroes):
                time.sleep(pause)

        logger.info(
            "Stratz sync done in %.1fs: %s",
            time.time() - started,
            stats.as_dict(),
        )
        return stats
