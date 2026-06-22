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

    def fetch_item_popularity(self, hero_id: int) -> Dict[str, Any]:
        data = self._get(f"/heroes/{hero_id}/itemPopularity", timeout=30)
        return data if isinstance(data, dict) else {}

    def fetch_hero_constants(self) -> Dict[str, Any]:
        data = self._get("/constants", timeout=30)
        return data if isinstance(data, dict) else {}

    BOOT_NAMES = frozenset({
        "boots of speed", "power treads", "phase boots", "arcane boots",
        "tranquil boots", "boots of travel", "guardian greaves",
    })

    TRASH_NAMES = frozenset({
        "tango", "healing salve", "clarity", "enchanted mango", "faerie fire",
        "iron branch", "gauntlets", "slippers", "mantle", "circlet",
        "belt of strength", "blade of alacrity", "staff of wizardry",
        "robe of the magi", "gloves of haste", "chainmail", "helm of iron will",
        "broadsword", "claymore", "quarterstaff", "void stone", "ring of health",
        "ring of protection", "ring of regen", "sages mask", "sobi mask",
        "orb of venom", "blight stone", "infused raindrops",
        "quelling blade", "recipe", "observer ward", "sentry ward",
        "dust of appearance", "smoke of deceit", "gem of true sight",
        "town portal scroll", "bottle",
    })

    def _is_core_item(self, name: str, cost: int) -> bool:
        lower = name.lower()
        if cost < 500:
            return False
        if lower in self.BOOT_NAMES:
            return False
        for trash in self.TRASH_NAMES:
            if trash in lower:
                return False
        return True

    def build_item_builds_from_popularity(self, hero_id: int, take: int = 20) -> List[Dict[str, Any]]:
        pop = self.fetch_item_popularity(hero_id)
        if not pop:
            return []

        constants = self.fetch_hero_constants()
        item_names: Dict[str, str] = {}
        item_costs: Dict[str, int] = {}
        if constants:
            items_const = constants.get("item_ids") or {}
            for iid, val in items_const.items():
                if isinstance(val, str):
                    item_names[iid] = val
                elif isinstance(val, dict):
                    item_names[iid] = val.get("dname", val.get("name", f"Item {iid}"))
                    item_costs[iid] = int(val.get("cost", 0) if val.get("cost") else 0)

        stages = [
            ("mid_game_items", "mid"),
            ("late_game_items", "late"),
        ]
        builds = []
        for stage_key, stage_label in stages:
            items = pop.get(stage_key, {})
            if not items:
                continue
            sorted_items = sorted(
                items.items(),
                key=lambda x: int(x[1].get("times", 0) if isinstance(x[1], dict) else 0),
                reverse=True,
            )
            seq = []
            total_times = 0
            total_wins = 0
            for item_id_str, stats in sorted_items:
                if not isinstance(stats, dict):
                    continue
                times = int(stats.get("times", 0))
                if times == 0:
                    continue
                name = item_names.get(str(item_id_str), f"Item {item_id_str}")
                cost = item_costs.get(str(item_id_str), 0)
                if not self._is_core_item(name, cost):
                    continue
                wins = int(stats.get("wins", 0))
                total_times += times
                total_wins += wins
                seq.append({
                    "id": int(item_id_str),
                    "name": name,
                    "time": stage_label,
                })
            if seq:
                builds.append({
                    "build_type": "item",
                    "sequence": seq[:10],
                    "win_rate": round(total_wins / total_times * 100, 2) if total_times else 0,
                    "games": total_times,
                    "role": stage_label,
                })
        return builds[:take]

    def build_skill_build_from_hero_abilities(self, hero_id: int, take: int = 10) -> List[Dict[str, Any]]:
        constants = self.fetch_hero_constants()
        if not constants:
            return []
        hero_abilities = constants.get("hero_abilities", {})
        hero_key = f"npc_dota_hero_{hero_id}"
        hero_ability_data = hero_abilities.get(hero_key) or hero_abilities.get(str(hero_id))
        if not hero_ability_data:
            return []

        all_abilities = constants.get("abilities", {})
        abilities_data = hero_ability_data.get("abilities") or hero_ability_data.get("skills") or []
        talent_tree = hero_ability_data.get("talents") or []

        ability_ids = []
        for ab in abilities_data:
            if isinstance(ab, dict):
                aid = ab.get("id") or ab.get("ability_id")
                slot = ab.get("slot") or 0
                if aid and slot <= 3:
                    ability_ids.append((slot, int(aid)))
            elif isinstance(ab, (int, str)):
                aid = int(ab)
                if aid > 0 and len(ability_ids) < 4:
                    ability_ids.append((len(ability_ids), aid))

        ability_ids.sort(key=lambda x: x[0])
        abilities = [aid for _, aid in ability_ids]

        if len(abilities) < 3:
            return []

        q, w, e = abilities[0], abilities[1], abilities[2]
        ult = abilities[3] if len(abilities) > 3 else None

        ult_order = [6, 12, 18] if ult else []

        def _name_for(aid):
            ab = all_abilities.get(str(aid))
            if isinstance(ab, dict):
                return ab.get("dname") or ab.get("name") or f"Ability {aid}"
            return f"Ability {aid}"

        phase1 = [1, 3, 5]
        phase2 = [2, 4, 7]
        phase3 = [8, 9, 10]
        order_map = {}
        lid = 1
        for p in phase1:
            order_map.setdefault(p, []).append(q)
        for p in phase2:
            order_map.setdefault(p, []).append(w)
        for p in phase3:
            order_map.setdefault(p, []).append(e)
        for u in ult_order:
            if ult:
                order_map.setdefault(u, []).append(ult)

        seq = []
        seen = set()
        for lvl in range(1, 19):
            for aid in order_map.get(lvl, []):
                if (aid, lvl) not in seen:
                    seq.append({"id": aid, "name": _name_for(aid)})
                    seen.add((aid, lvl))
            if not order_map.get(lvl) and lvl <= 10:
                remaining = [a for a in [q, w, e] if a not in seen]
                if remaining:
                    seq.append({"id": remaining[0], "name": _name_for(remaining[0])})
                    seen.add(remaining[0])

        talents = []
        if not talent_tree:
            for tier, slot in [(10, "left"), (10, "right"), (15, "left"), (15, "right"),
                                (20, "left"), (20, "right"), (25, "left"), (25, "right")]:
                talents.append({
                    "abilityId": 0, "tier": tier, "slot": slot,
                    "name": "", "matchCount": 0, "win_rate": 0, "pick_rate": 0,
                })
        else:
            for i, t in enumerate(talent_tree[:8]):
                if isinstance(t, dict):
                    aid = t.get("id") or t.get("ability_id") or 0
                    tier = [10, 10, 15, 15, 20, 20, 25, 25][i] if i < 8 else 0
                    slot = "left" if i % 2 == 0 else "right"
                    talents.append({
                        "abilityId": int(aid),
                        "tier": tier,
                        "slot": slot,
                        "name": _name_for(aid),
                        "matchCount": 0,
                        "win_rate": 0,
                        "pick_rate": 0,
                    })

        return [{
            "build_type": "skill",
            "sequence": seq,
            "pick_rate": 0,
            "win_rate": 0,
            "games": 0,
            "role": "",
        }]


def _float_or_none(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        return round(float(value), 2)
    except (TypeError, ValueError):
        return None
