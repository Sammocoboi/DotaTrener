import logging
import time
from typing import Any, Dict, List, Optional, Tuple

import requests

logger = logging.getLogger(__name__)

OPEN_DOTA_BASE = "https://api.opendota.com/api"

HERO_ATTRS = {
    0: "str", 1: "agi", 2: "int", 3: "uni",
}

BRACKET_LABELS: Dict[str, int] = {
    "herald": 1,
    "guardian": 2,
    "crusader": 3,
    "archon": 4,
    "legend": 5,
    "ancient": 6,
    "divine": 7,
    "immortal": 8,
}

BRACKET_PREFIXES: Dict[str, str] = {
    "herald": "1",
    "guardian": "2",
    "crusader": "3",
    "archon": "4",
    "legend": "5",
    "ancient": "6",
    "divine": "7",
    "immortal": "8",
    "pro": "pro",
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

    def compute_total_games_per_bracket(self) -> Dict[str, int]:
        stats = self.fetch_hero_stats()
        totals: Dict[str, int] = {}
        for prefix in BRACKET_PREFIXES.values():
            total = sum(
                int(s.get(f"{prefix}_pick") or 0)
                for s in stats
                if s.get("id") is not None
            )
            if total > 0:
                labels = [k for k, v in BRACKET_PREFIXES.items() if v == prefix]
                key = labels[0] if labels else prefix
                totals[key] = total
        return totals

    def compute_total_games_for_prefixes(self, prefixes: List[str]) -> int:
        stats = self.fetch_hero_stats()
        total = 0
        for prefix in prefixes:
            total += sum(
                int(s.get(f"{prefix}_pick") or 0)
                for s in stats
                if s.get("id") is not None
            )
        return total

    BRACKET_FALLBACK_ORDER: Dict[str, List[str]] = {
        "pro": ["pro"],
        "immortal": ["8", "7", "6", "5", "4", "3", "2", "1"],
        "divine": ["7", "6", "5", "4", "3", "2", "1"],
        "ancient": ["6", "5", "4", "3", "2", "1"],
        "legend": ["5", "4", "3", "2", "1"],
        "archon": ["4", "3", "2", "1"],
        "crusader": ["3", "2", "1"],
        "guardian": ["2", "1"],
        "herald": ["1"],
    }

    AVERAGE_FIELDS = (
        "avg_kills", "avg_deaths", "avg_assists", "avg_gpm", "avg_xpm",
        "avg_last_hits", "avg_denies", "avg_kda", "avg_hero_damage", "avg_tower_damage",
    )

    def _aggregate_bracket_stats(self, hero_stat: Dict[str, Any], prefixes: List[str]) -> Dict[str, Any]:
        total_pick = 0
        total_win = 0
        total_ban = 0

        for prefix in prefixes:
            pick = int(hero_stat.get(f"{prefix}_pick") or 0)
            if pick == 0:
                continue
            win = int(hero_stat.get(f"{prefix}_win") or 0)
            ban = int(hero_stat.get(f"{prefix}_ban") or 0)
            total_pick += pick
            total_win += win
            total_ban += ban

        result: Dict[str, Any] = {
            "pick": total_pick,
            "win": total_win,
            "ban": total_ban,
        }

        top_prefix = prefixes[0] if prefixes else None
        use_pro = top_prefix == "pro" if top_prefix else False

        for field in self.AVERAGE_FIELDS:
            val = None
            if field == "avg_kda":
                field_key = "kda"
            else:
                field_key = field

            for prefix in prefixes:
                val = _float_or_none(hero_stat.get(f"{prefix}_{field_key}"))
                if val is not None:
                    break

            if val is None:
                val = _float_or_none(hero_stat.get(field_key))

            if val is None and use_pro:
                val = _float_or_none(hero_stat.get(f"pro_{field_key}"))

            result[field] = val

        return result

    def build_meta_for_hero(
        self,
        hero_stat: Dict[str, Any],
        bracket: str = "immortal",
        total_games_bracket: Optional[int] = None,
        min_games: int = 300,
    ) -> Optional[Dict[str, Any]]:
        hero_id = hero_stat.get("id")
        if hero_id is None:
            return None

        fallback_order = self.BRACKET_FALLBACK_ORDER.get(bracket.lower(), ["8", "7", "6", "5", "4", "3", "2", "1"])

        used_prefixes: List[str] = []
        for idx in range(len(fallback_order)):
            prefixes = fallback_order[:idx + 1]
            aggr = self._aggregate_bracket_stats(hero_stat, prefixes)
            if aggr["pick"] >= min_games:
                used_prefixes = prefixes
                break

        if not used_prefixes:
            return None

        aggr = self._aggregate_bracket_stats(hero_stat, used_prefixes)
        pick = aggr["pick"]
        win = aggr["win"]
        ban = aggr["ban"]

        if pick == 0:
            return None

        win_rate = round(win / pick * 100, 2) if pick else 0.0
        ban_rate = round(ban / (pick + ban) * 100, 2) if (pick + ban) else 0.0
        pick_rate = round(pick / total_games_bracket * 100, 2) if (total_games_bracket and total_games_bracket > 0) else (round(pick / 100, 2) if pick else 0.0)

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
            "pick_rate": pick_rate,
            "win_rate": win_rate,
            "ban_rate": ban_rate,
            "games_played": pick,
            "bracket": f"{bracket}_{used_prefixes[0]}-{used_prefixes[-1]}",
            "avg_kills": aggr.get("avg_kills"),
            "avg_deaths": aggr.get("avg_deaths"),
            "avg_assists": aggr.get("avg_assists"),
            "avg_gpm": aggr.get("avg_gpm"),
            "avg_xpm": aggr.get("avg_xpm"),
            "avg_last_hits": aggr.get("avg_last_hits"),
            "avg_denies": aggr.get("avg_denies"),
            "avg_kda": aggr.get("avg_kda"),
            "avg_hero_damage": aggr.get("avg_hero_damage"),
            "avg_tower_damage": aggr.get("avg_tower_damage"),
            "avg_networth": None,
            "avg_kill_participation": None,
            "_used_brackets": used_prefixes,
        }

    def fetch_player_recent_matches(self, account_id: int) -> List[Dict[str, Any]]:
        data = self._get(f"/players/{account_id}/recentMatches", timeout=15)
        return data if isinstance(data, list) else []

    def fetch_player_heroes(self, account_id: int) -> List[Dict[str, Any]]:
        data = self._get(f"/players/{account_id}/heroes", timeout=15)
        if not isinstance(data, list):
            return []
        heroes = [h for h in data if (h.get("games") or 0) > 0]
        heroes.sort(key=lambda h: h.get("games", 0), reverse=True)
        return heroes


def _float_or_none(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        return round(float(value), 2)
    except (TypeError, ValueError):
        return None
