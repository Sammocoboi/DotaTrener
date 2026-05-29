import logging
import time
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger(__name__)

OPEN_DOTA_BASE = "https://api.opendota.com/api"

HERO_ATTRS = {
    0: "str", 1: "agi", 2: "int", 3: "uni",
}


class OpenDotaClient:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "DotaTrener/1.0"})
        self._heroes: Optional[List[Dict[str, Any]]] = None
        self._hero_stats: Optional[List[Dict[str, Any]]] = None

    def _get(self, endpoint: str, retries: int = 3, timeout: int = 90) -> Any:
        url = f"{OPEN_DOTA_BASE}{endpoint}"
        for attempt in range(retries):
            try:
                resp = self.session.get(url, timeout=timeout)
                if resp.status_code == 429:
                    wait = int(resp.headers.get("Retry-After", 5))
                    logger.warning("OpenDota rate limited, waiting %ds", wait)
                    time.sleep(wait)
                    continue
                resp.raise_for_status()
                return resp.json()
            except requests.RequestException as exc:
                logger.error("OpenDota request failed (attempt %d): %s", attempt + 1, exc)
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
        return None

    def fetch_heroes(self) -> List[Dict[str, Any]]:
        if self._heroes is not None:
            return self._heroes
        data = self._get("/heroes")
        self._heroes = data if isinstance(data, list) else []
        logger.info("OpenDota: loaded %d heroes", len(self._heroes))
        return self._heroes

    def fetch_hero_stats(self) -> List[Dict[str, Any]]:
        if self._hero_stats is not None:
            return self._hero_stats
        data = self._get("/heroStats", timeout=120)
        self._hero_stats = data if isinstance(data, list) else []
        logger.info("OpenDota: loaded stats for %d heroes", len(self._hero_stats))
        return self._hero_stats

    def get_hero_map(self) -> Dict[int, Dict[str, Any]]:
        heroes = self.fetch_heroes()
        return {h["id"]: h for h in heroes if "id" in h}

    def get_hero_stats_map(self) -> Dict[int, Dict[str, Any]]:
        stats = self.fetch_hero_stats()
        return {s["id"]: s for s in stats if "id" in s}

    def build_meta_for_hero(self, hero_stat: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        hero_id = hero_stat.get("id")
        if hero_id is None:
            return None

        pick = int(hero_stat.get("pro_pick") or hero_stat.get("8_pick") or 0)
        win = int(hero_stat.get("pro_win") or hero_stat.get("8_win") or 0)
        ban = int(hero_stat.get("pro_ban") or hero_stat.get("8_ban") or 0)

        if pick == 0:
            pick = int(hero_stat.get("128_pick") or hero_stat.get("7_pick") or 0)
            win = int(hero_stat.get("128_win") or hero_stat.get("7_win") or 0)
            ban = int(hero_stat.get("128_ban") or hero_stat.get("7_ban") or 0)

        if pick == 0:
            pick = int(hero_stat.get("pro_pick") or 0)
            win = int(hero_stat.get("pro_win") or 0)
            ban = int(hero_stat.get("pro_ban") or 0)

        win_rate = round(win / pick * 100, 2) if pick else 0.0
        ban_rate = round(ban / pick * 100, 2) if pick else 0.0

        attr_id = hero_stat.get("primary_attr")
        primary_attr = HERO_ATTRS.get(attr_id, "str")

        localized = hero_stat.get("localized_name") or hero_stat.get("name") or f"Hero {hero_id}"
        internal_name = hero_stat.get("name") or ""
        short_name = internal_name.replace("npc_dota_hero_", "") if internal_name else ""

        image_url = f"https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/{short_name}.png"

        return {
            "id": hero_id,
            "name": internal_name,
            "displayName": localized,
            "shortName": short_name,
            "primary_attr": primary_attr,
            "image_url": image_url,
            "pick_rate": round(pick / 100, 2) if pick else 0.0,
            "win_rate": win_rate,
            "ban_rate": ban_rate,
            "games_played": pick,
            "avg_kills": _float_or_none(hero_stat.get("pro_avg_kills") or hero_stat.get("8_avg_kills")),
            "avg_deaths": _float_or_none(hero_stat.get("pro_avg_deaths") or hero_stat.get("8_avg_deaths")),
            "avg_assists": _float_or_none(hero_stat.get("pro_avg_assists") or hero_stat.get("8_avg_assists")),
            "avg_gpm": _float_or_none(hero_stat.get("pro_avg_gpm") or hero_stat.get("8_avg_gpm")),
            "avg_xpm": _float_or_none(hero_stat.get("pro_avg_xpm") or hero_stat.get("8_avg_xpm")),
            "avg_last_hits": _float_or_none(hero_stat.get("pro_avg_last_hits") or hero_stat.get("8_avg_last_hits")),
            "avg_denies": _float_or_none(hero_stat.get("pro_avg_denies") or hero_stat.get("8_avg_denies")),
            "avg_kda": _float_or_none(hero_stat.get("pro_kda") or hero_stat.get("8_kda")),
            "avg_hero_damage": _float_or_none(hero_stat.get("pro_avg_hero_damage") or hero_stat.get("8_avg_hero_damage")),
            "avg_tower_damage": _float_or_none(hero_stat.get("pro_avg_tower_damage") or hero_stat.get("8_avg_tower_damage")),
            "avg_networth": None,
            "avg_kill_participation": None,
        }


def _float_or_none(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        return round(float(value), 2)
    except (TypeError, ValueError):
        return None
