import logging
import time
from dataclasses import dataclass, field
from datetime import date
from typing import Any, Dict, List, Optional

from django.db import transaction

from coaching.models import Hero
from stratz_meta.models import HeroMeta, StratzPatch

from .opendota_client import OpenDotaClient

logger = logging.getLogger(__name__)


@dataclass
class OpenDotaSyncStats:
    total: int = 0
    success: int = 0
    failed: int = 0
    heroes_created: int = 0
    heroes_updated: int = 0

    def as_dict(self) -> Dict[str, int]:
        return {k: v for k, v in self.__dict__.items() if isinstance(v, int)}


@dataclass
class HeroLoadStats:
    created: int = 0
    updated: int = 0
    skipped: int = 0


class OpenDotaSyncService:
    def __init__(self, client: Optional[OpenDotaClient] = None):
        self.client = client or OpenDotaClient()

    def sync_patches(self, target_version: str = "7.41c") -> StratzPatch:
        StratzPatch.objects.update(is_current=False)
        patch, _ = StratzPatch.objects.update_or_create(
            version=target_version,
            defaults={"release_date": date.today(), "is_current": True},
        )
        StratzPatch.objects.exclude(pk=patch.pk).update(is_current=False)
        logger.info("OpenDota: patch set to %s", target_version)
        return patch

    def load_heroes(self) -> HeroLoadStats:
        stats = self.client.fetch_hero_stats()
        stats_map = {s["id"]: s for s in stats if "id" in s}
        hero_map = self.client.get_hero_map()
        result = HeroLoadStats()

        with transaction.atomic():
            for hero_id, hero_stat in stats_map.items():
                hero_info = hero_map.get(hero_id, {})
                name = hero_info.get("name") or hero_stat.get("name") or ""
                localized = (
                    hero_info.get("localized_name")
                    or hero_stat.get("localized_name")
                    or f"Hero {hero_id}"
                )
                attr_id = hero_stat.get("primary_attr")
                from .opendota_client import HERO_ATTRS
                primary_attr = HERO_ATTRS.get(attr_id, "str")
                internal_name = hero_stat.get("name") or ""
                short_name = internal_name.replace("npc_dota_hero_", "") if internal_name else ""
                image_url = f"https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/{short_name}.png"

                _, created = Hero.objects.update_or_create(
                    steam_id=int(hero_id),
                    defaults={
                        "name": name[:100],
                        "localized_name": localized[:100],
                        "primary_attr": primary_attr,
                        "image_url": image_url,
                    },
                )
                if created:
                    result.created += 1
                else:
                    result.updated += 1

        logger.info("OpenDota: heroes loaded (created=%d, updated=%d)", result.created, result.updated)
        return result

    def sync_meta(
        self,
        *,
        patch_version: str = "7.41c",
        bracket: str = "immortal",
        hero_ids: Optional[List[int]] = None,
        limit: Optional[int] = None,
        ensure_heroes: bool = True,
        on_progress=None,
    ) -> OpenDotaSyncStats:
        patch = self.sync_patches(target_version=patch_version)

        if ensure_heroes:
            self.load_heroes()

        stats = self.client.fetch_hero_stats()
        if not stats:
            logger.error("OpenDota: no hero stats returned")
            return OpenDotaSyncStats()

        stats_map = {s["id"]: s for s in stats if "id" in s}
        total_games = self.client.compute_total_games_per_bracket()
        bracket_total = total_games.get(bracket)

        hero_ids_list = list(stats_map.keys())
        if hero_ids:
            hero_id_set = set(hero_ids)
            hero_ids_list = [hid for hid in hero_ids_list if hid in hero_id_set]
        if limit:
            hero_ids_list = hero_ids_list[:limit]

        sync_stats = OpenDotaSyncStats(total=len(hero_ids_list))
        processed = 0
        started = time.time()

        for hero_id in hero_ids_list:
            processed += 1
            hero_stat = stats_map[hero_id]
            label = hero_stat.get("localized_name") or hero_stat.get("name") or f"Hero {hero_id}"

            if on_progress:
                on_progress(processed, sync_stats.total, label, hero_id)

            meta_data = self.client.build_meta_for_hero(
                hero_stat,
                bracket=bracket,
                total_games_bracket=bracket_total,
            )
            if not meta_data:
                sync_stats.failed += 1
                logger.warning("OpenDota: no meta for hero %s", label)
                continue

            hero_obj = Hero.objects.filter(steam_id=int(hero_id)).first()
            if not hero_obj:
                hero_obj = Hero.objects.create(
                    steam_id=int(hero_id),
                    name=(hero_stat.get("name") or f"hero_{hero_id}")[:100],
                    localized_name=label[:100],
                    primary_attr=meta_data["primary_attr"],
                    image_url=meta_data["image_url"],
                )
                sync_stats.heroes_created += 1

            try:
                HeroMeta.objects.update_or_create(
                    hero=hero_obj,
                    patch=patch,
                    defaults={
                        "source": "opendota",
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
                sync_stats.success += 1
                logger.info("[%s/%s] %s: WR=%s%% games=%s", processed, sync_stats.total, label, meta_data["win_rate"], meta_data["games_played"])
            except Exception as exc:
                logger.exception("Failed to save hero %s: %s", hero_id, exc)
                sync_stats.failed += 1

        elapsed = time.time() - started
        logger.info("OpenDota sync done in %.1fs: %s", elapsed, sync_stats.as_dict())
        return sync_stats
