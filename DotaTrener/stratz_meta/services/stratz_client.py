import logging
import time
from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

HEROES_QUERY = """
{
  constants {
    heroes {
      id
      name
      displayName
      shortName
    }
  }
}
"""

PATCHES_QUERY = """
{
  constants {
    gameVersions {
      id
      name
    }
  }
}
"""

HERO_STATS_QUERY = """
{
  constants {
    heroes {
      id
      stats {
        primaryAttribute
      }
    }
  }
}
"""

ITEMS_QUERY = """
{
  constants {
    items {
      id
      displayName
      shortName
    }
  }
}
"""

ABILITIES_QUERY = """
{
  constants {
    abilities {
      id
      name
      language {
        displayName
      }
    }
  }
}
"""

ATTR_MAP = {
    "STRENGTH": "str",
    "AGILITY": "agi",
    "INTELLIGENCE": "int",
    "ALL": "uni",
    "UNIVERSAL": "uni",
}

POSITION_LABELS = {
    "POSITION_1": "Carry",
    "POSITION_2": "Mid",
    "POSITION_3": "Offlane",
    "POSITION_4": "Support",
    "POSITION_5": "Hard Support",
}


def _bracket_fragments(rank: Optional[str]) -> Tuple[str, str]:
    """Returns (bracketBasicIds fragment for stats, bracketIds fragment for winGameVersion)."""
    if not rank:
        return "", ""
    basic = rank.upper()
    if basic not in {
        "UNCALIBRATED",
        "HERALD_GUARDIAN",
        "CRUSADER_ARCHON",
        "LEGEND_ANCIENT",
        "DIVINE_IMMORTAL",
        "FILTERED",
        "ALL",
    }:
        basic = "DIVINE_IMMORTAL"
    bracket_id = "DIVINE" if basic == "DIVINE_IMMORTAL" else basic.split("_")[0]
    return f", bracketBasicIds: [{basic}]", f", bracketIds: [{bracket_id}]"


def _win_rate(win_count: int, match_count: int) -> float:
    if not match_count:
        return 0.0
    return round(win_count / match_count * 100, 2)


def _roles_from_position_rows(pos_rows: List[Dict[str, Any]]) -> Dict[str, float]:
    roles: Dict[str, float] = {}
    total_pos = sum(int(p.get("matchCount") or 0) for p in pos_rows)
    if not total_pos:
        return roles
    for row in pos_rows:
        pos = row.get("position")
        if not pos:
            continue
        label = POSITION_LABELS.get(pos, pos)
        roles[label] = round(int(row.get("matchCount") or 0) / total_pos * 100, 2)
    return roles


def _meta_from_totals(
    win_count: int,
    match_count: int,
    roles: Optional[Dict[str, float]] = None,
    pick_rate: float = 0.0,
    ban_rate: float = 0.0,
) -> Dict[str, Any]:
    return {
        "pick_rate": pick_rate,
        "win_rate": _win_rate(win_count, match_count),
        "ban_rate": ban_rate,
        "games_played": match_count,
        "roles": roles or {},
    }


def _format_internal_name(name: str) -> str:
    if not name:
        return ""
    return " ".join(part.capitalize() for part in name.replace("_", " ").split())


class StratzClient:
    def __init__(self):
        self.api_key = settings.STRATZ_API_KEY
        if not self.api_key:
            raise ValueError("STRATZ_API_KEY is not set")
        self.graphql_url = settings.STRATZ_API_URL
        self.rest_url = settings.STRATZ_REST_URL
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "STRATZ_API/1.0",
            }
        )
        self._version_name_to_id: Optional[Dict[str, int]] = None
        self._item_names: Optional[Dict[int, str]] = None
        self._ability_names: Optional[Dict[int, str]] = None

    def load_item_catalog(self) -> Dict[int, str]:
        if self._item_names is not None:
            return self._item_names
        catalog: Dict[int, str] = {}
        data = self.graphql(ITEMS_QUERY)
        if data:
            for item in data.get("constants", {}).get("items", []):
                item_id = item.get("id")
                if item_id is None:
                    continue
                label = (
                    item.get("displayName")
                    or item.get("shortName")
                    or f"Item {item_id}"
                )
                catalog[int(item_id)] = str(label)[:100]
        if not catalog:
            rest_items = self.rest_list("item")
            for item in rest_items:
                item_id = item.get("id")
                if item_id is None:
                    continue
                label = (
                    item.get("displayName")
                    or item.get("dname")
                    or item.get("name")
                    or f"Item {item_id}"
                )
                catalog[int(item_id)] = str(label)[:100]
        self._item_names = catalog
        logger.info("Loaded %s item names from Stratz", len(catalog))
        return catalog

    def load_ability_catalog(self) -> Dict[int, str]:
        if self._ability_names is not None:
            return self._ability_names
        catalog: Dict[int, str] = {}
        data = self.graphql(ABILITIES_QUERY)
        if data:
            for ability in data.get("constants", {}).get("abilities", []):
                ability_id = ability.get("id")
                if ability_id is None:
                    continue
                lang = ability.get("language") or {}
                label = lang.get("displayName") or _format_internal_name(
                    ability.get("name") or ""
                )
                if not label:
                    label = f"Ability {ability_id}"
                catalog[int(ability_id)] = str(label)[:100]
        self._ability_names = catalog
        logger.info("Loaded %s ability names from Stratz", len(catalog))
        return catalog

    def get_item_name(self, item_id: int) -> str:
        catalog = self.load_item_catalog()
        return catalog.get(int(item_id), f"Item {item_id}")

    def get_ability_name(self, ability_id: int, level: Optional[int] = None) -> str:
        catalog = self.load_ability_catalog()
        base = catalog.get(int(ability_id), f"Ability {ability_id}")
        if level is not None:
            return f"{base} L{level}"
        return base

    def enrich_sequence_entry(
        self, entry: Dict[str, Any], build_type: str
    ) -> Dict[str, Any]:
        entry_id = entry.get("id")
        if entry_id is None:
            return entry
        enriched = dict(entry)
        if build_type == "item":
            enriched["name"] = self.get_item_name(int(entry_id))
        else:
            level = None
            name = entry.get("name") or ""
            if isinstance(name, str) and name.startswith("L") and name[1:].isdigit():
                level = int(name[1:])
            enriched["name"] = self.get_ability_name(int(entry_id), level=level)
        return enriched

    def graphql(self, query: str, retries: int = 3) -> Optional[Dict[str, Any]]:
        for _ in range(retries):
            try:
                resp = self.session.post(
                    self.graphql_url,
                    json={"query": query.strip()},
                    timeout=30,
                )
                if resp.status_code == 429:
                    time.sleep(int(resp.headers.get("Retry-After", 2)))
                    continue
                if resp.status_code != 200:
                    logger.error("Stratz HTTP %s: %s", resp.status_code, resp.text[:200])
                    return None
                data = resp.json()
                if data.get("errors"):
                    logger.warning("Stratz GraphQL: %s", data["errors"][0].get("message", ""))
                    return None
                return data.get("data")
            except requests.RequestException as exc:
                logger.error("Stratz request failed: %s", exc)
                time.sleep(1)
        return None

    def get_version_map(self) -> Dict[str, int]:
        if self._version_name_to_id is not None:
            return self._version_name_to_id
        patches = self.fetch_patches()
        self._version_name_to_id = {
            (p.get("name") or str(p.get("id", ""))): int(p["id"])
            for p in patches
            if p.get("id") is not None
        }
        return self._version_name_to_id

    def resolve_game_version_id(self, patch_version: str) -> Optional[int]:
        version_map = self.get_version_map()
        if patch_version in version_map:
            return version_map[patch_version]
        for name, vid in version_map.items():
            if name.startswith(patch_version) or patch_version.startswith(name):
                return vid
        return None

    def rest_list(self, endpoint: str) -> List[Dict[str, Any]]:
        try:
            resp = self.session.get(f"{self.rest_url}/{endpoint}", timeout=20)
            resp.raise_for_status()
            data = resp.json()
            if isinstance(data, dict):
                result = []
                for key, value in data.items():
                    if isinstance(value, dict):
                        value = dict(value)
                        value["id"] = int(key)
                        result.append(value)
                return result
            return data if isinstance(data, list) else []
        except requests.RequestException as exc:
            logger.warning("Stratz REST %s failed: %s", endpoint, exc)
            return []

    def fetch_heroes(self) -> List[Dict[str, Any]]:
        data = self.graphql(HEROES_QUERY)
        if data:
            heroes = data.get("constants", {}).get("heroes", [])
            if heroes:
                return heroes
        return self.rest_list("hero")

    def fetch_patches(self) -> List[Dict[str, Any]]:
        data = self.graphql(PATCHES_QUERY)
        if not data:
            return []
        return data.get("constants", {}).get("gameVersions", [])

    def fetch_hero_primary_attrs(self) -> Dict[int, str]:
        data = self.graphql(HERO_STATS_QUERY)
        if not data:
            return {}
        result = {}
        for hero in data.get("constants", {}).get("heroes", []):
            hero_id = hero.get("id")
            attr = (hero.get("stats") or {}).get("primaryAttribute")
            if hero_id and attr:
                result[int(hero_id)] = ATTR_MAP.get(str(attr).upper(), "str")
        return result

    def fetch_meta_batch(
        self,
        hero_ids: List[int],
        game_version_id: int,
        rank: Optional[str] = None,
    ) -> Dict[int, Dict[str, Any]]:
        if not hero_ids:
            return {}
        ids_csv = ", ".join(str(i) for i in hero_ids)
        basic_frag, bracket_frag = _bracket_fragments(rank)
        query = f"""{{
          heroStats {{
            winGameVersion(heroIds: [{ids_csv}]{bracket_frag}) {{
              heroId gameVersionId winCount matchCount
            }}
            stats(heroIds: [{ids_csv}], groupByPosition: true{basic_frag}) {{
              heroId position winCount matchCount
            }}
            statsTotals: stats(heroIds: [{ids_csv}]{basic_frag}) {{
              heroId winCount matchCount
            }}
          }}
        }}"""
        data = self.graphql(query)
        if not data:
            return {}

        hs = data.get("heroStats", {})
        win_rows = hs.get("winGameVersion") or []
        stat_rows = hs.get("stats") or []
        total_rows = hs.get("statsTotals") or []

        positions: Dict[int, List[Dict[str, Any]]] = defaultdict(list)
        for row in stat_rows:
            hid = row.get("heroId")
            if hid is not None:
                positions[int(hid)].append(row)

        totals_by_hero: Dict[int, Dict[str, Any]] = {}
        batch_match_total = 0
        for row in total_rows:
            hid = int(row["heroId"])
            totals_by_hero[hid] = row
            batch_match_total += int(row.get("matchCount") or 0)

        best_version_row: Dict[int, Dict[str, Any]] = {}
        patch_row: Dict[int, Dict[str, Any]] = {}
        for row in win_rows:
            hid = int(row["heroId"])
            match_count = int(row.get("matchCount") or 0)
            if int(row.get("gameVersionId", -1)) == int(game_version_id):
                patch_row[hid] = row
            current_best = best_version_row.get(hid)
            if not current_best or match_count > int(current_best.get("matchCount") or 0):
                best_version_row[hid] = row

        result: Dict[int, Dict[str, Any]] = {}
        for hid in hero_ids:
            pos_rows = positions.get(hid, [])
            roles = _roles_from_position_rows(pos_rows)
            totals = totals_by_hero.get(hid)
            pick_rate = 0.0
            if totals and batch_match_total:
                pick_rate = round(
                    int(totals.get("matchCount") or 0) / batch_match_total * 100, 2
                )

            source = patch_row.get(hid) or best_version_row.get(hid)
            if source:
                win_count = int(source.get("winCount") or 0)
                match_count = int(source.get("matchCount") or 0)
                result[hid] = _meta_from_totals(
                    win_count, match_count, roles=roles, pick_rate=pick_rate
                )
                continue

            if totals and int(totals.get("matchCount") or 0) > 0:
                result[hid] = _meta_from_totals(
                    int(totals.get("winCount") or 0),
                    int(totals.get("matchCount") or 0),
                    roles=roles,
                    pick_rate=pick_rate,
                )
                continue

            if pos_rows:
                win_total = sum(int(p.get("winCount") or 0) for p in pos_rows)
                match_total = sum(int(p.get("matchCount") or 0) for p in pos_rows)
                if match_total:
                    result[hid] = _meta_from_totals(
                        win_total, match_total, roles=roles, pick_rate=pick_rate
                    )
                    continue

            fallback = self._fetch_meta_win_day(hid, rank)
            if fallback:
                fallback["roles"] = roles or fallback.get("roles", {})
                fallback["pick_rate"] = pick_rate or fallback.get("pick_rate", 0.0)
                result[hid] = fallback

        for hid, meta in result.items():
            games = meta.get("games_played") or 0
            if games:
                meta["ban_rate"] = self._fetch_ban_rate(hid, games)

        return result

    def _fetch_meta_win_day(self, hero_id: int, rank: Optional[str]) -> Optional[Dict[str, Any]]:
        bracket_frag = ""
        if rank:
            bracket_id = "DIVINE" if rank.upper() == "DIVINE_IMMORTAL" else rank.upper()
            bracket_frag = f", bracketIds: [{bracket_id}]"
        query = f"""{{
          heroStats {{
            winDay(heroIds: [{hero_id}]{bracket_frag}) {{
              heroId winCount matchCount
            }}
          }}
        }}"""
        data = self.graphql(query)
        rows = (data or {}).get("heroStats", {}).get("winDay") or []
        win_total = sum(int(r.get("winCount") or 0) for r in rows)
        match_total = sum(int(r.get("matchCount") or 0) for r in rows)
        if not match_total:
            return None
        return {
            "pick_rate": 0.0,
            "win_rate": _win_rate(win_total, match_total),
            "ban_rate": 0.0,
            "games_played": match_total,
            "roles": {},
        }

    def _fetch_ban_rate(self, hero_id: int, games_played: int) -> float:
        query = f"""{{ heroStats {{ banDay(heroId: {hero_id}) {{ matchCount }} }} }}"""
        data = self.graphql(query)
        rows = (data or {}).get("heroStats", {}).get("banDay") or []
        ban_total = sum(int(r.get("matchCount") or 0) for r in rows)
        if not ban_total or not games_played:
            return 0.0
        return round(min(100.0, ban_total / games_played * 100), 2)

    def fetch_hero_overview(
        self,
        hero_id: int,
        patch_id: Optional[str] = None,
        rank: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        version_map = self.get_version_map()
        game_version_id = version_map.get(patch_id or "") if patch_id else None
        if game_version_id is None and patch_id:
            game_version_id = self.resolve_game_version_id(patch_id)
        if game_version_id is None:
            patches = self.fetch_patches()
            if patches:
                game_version_id = int(patches[0]["id"])
        if game_version_id is None:
            return self._fetch_meta_win_day(hero_id, rank)
        batch = self.fetch_meta_batch([hero_id], int(game_version_id), rank)
        return batch.get(hero_id)

    def fetch_hero_builds(
        self,
        hero_id: int,
        build_type: str,
        patch_id: Optional[str] = None,
        rank: Optional[str] = None,
        take: int = 100,
    ) -> List[Dict[str, Any]]:
        if build_type == "item":
            return self._fetch_item_builds(hero_id, take)
        return self._fetch_skill_builds(hero_id, take)

    def _fetch_item_builds(self, hero_id: int, take: int) -> List[Dict[str, Any]]:
        query = f"""{{
          heroStats {{
            itemFullPurchase(heroId: {hero_id}) {{ itemId time winCount matchCount }}
            itemBootPurchase(heroId: {hero_id}) {{ itemId winCount matchCount }}
          }}
        }}"""
        data = self.graphql(query)
        if not data:
            return []
        hs = data.get("heroStats", {})
        rows = list(hs.get("itemFullPurchase") or []) + list(hs.get("itemBootPurchase") or [])
        if not rows:
            return []

        by_time: Dict[int, List[Dict[str, Any]]] = defaultdict(list)
        for row in rows:
            t = int(row.get("time") or 0)
            by_time[t].append(row)

        builds: List[Dict[str, Any]] = []
        for time_key in sorted(by_time.keys()):
            group = sorted(
                by_time[time_key],
                key=lambda r: int(r.get("matchCount") or 0),
                reverse=True,
            )
            seq = [
                {
                    "id": int(r["itemId"]),
                    "name": self.get_item_name(int(r["itemId"])),
                }
                for r in group
                if r.get("itemId")
            ]
            if not seq:
                continue
            match_total = sum(int(r.get("matchCount") or 0) for r in group)
            win_total = sum(int(r.get("winCount") or 0) for r in group)
            builds.append(
                {
                    "build_type": "item",
                    "sequence": seq,
                    "pick_rate": 0.0,
                    "win_rate": _win_rate(win_total, match_total),
                    "games": match_total,
                    "role": f"time_{time_key}",
                }
            )

        builds.sort(key=lambda b: b["games"], reverse=True)
        if len(builds) < take:
            seen = {tuple(i["id"] for i in b["sequence"]) for b in builds}
            for row in sorted(rows, key=lambda r: int(r.get("matchCount") or 0), reverse=True):
                item_id = row.get("itemId")
                if not item_id:
                    continue
                seq = (int(item_id),)
                if seq in seen:
                    continue
                seen.add(seq)
                mc = int(row.get("matchCount") or 0)
                wc = int(row.get("winCount") or 0)
                builds.append(
                    {
                        "build_type": "item",
                        "sequence": [
                            {
                                "id": int(item_id),
                                "name": self.get_item_name(int(item_id)),
                            }
                        ],
                        "pick_rate": 0.0,
                        "win_rate": _win_rate(wc, mc),
                        "games": mc,
                        "role": "",
                    }
                )
                if len(builds) >= take:
                    break
        return builds[:take]

    def _fetch_skill_builds(self, hero_id: int, take: int) -> List[Dict[str, Any]]:
        query = f"""{{
          heroStats {{
            abilityMaxLevel(heroId: {hero_id}) {{ abilityId level winCount matchCount }}
            abilityMinLevel(heroId: {hero_id}) {{ abilityId level winCount matchCount }}
          }}
        }}"""
        data = self.graphql(query)
        if not data:
            return []
        hs = data.get("heroStats", {})
        rows = list(hs.get("abilityMaxLevel") or []) + list(hs.get("abilityMinLevel") or [])
        rows.sort(key=lambda r: (int(r.get("level") or 0), -int(r.get("matchCount") or 0)))

        by_level: Dict[int, Dict[str, Any]] = {}
        for row in rows:
            level = int(row.get("level") or 0)
            if level not in by_level or int(row.get("matchCount") or 0) > int(
                by_level[level].get("matchCount") or 0
            ):
                by_level[level] = row

        if by_level:
            seq = [
                {
                    "id": int(by_level[lvl]["abilityId"]),
                    "name": self.get_ability_name(
                        int(by_level[lvl]["abilityId"]), level=lvl
                    ),
                }
                for lvl in sorted(by_level.keys())
                if by_level[lvl].get("abilityId")
            ]
            if seq:
                match_total = max(int(r.get("matchCount") or 0) for r in by_level.values())
                win_total = max(int(r.get("winCount") or 0) for r in by_level.values())
                top_build = {
                    "build_type": "skill",
                    "sequence": seq,
                    "pick_rate": 0.0,
                    "win_rate": _win_rate(win_total, match_total),
                    "games": match_total,
                    "role": "",
                }
                extra = []
                for row in sorted(rows, key=lambda r: int(r.get("matchCount") or 0), reverse=True)[
                    : take - 1
                ]:
                    aid = row.get("abilityId")
                    if not aid:
                        continue
                    level = int(row.get("level") or 0)
                    mc = int(row.get("matchCount") or 0)
                    wc = int(row.get("winCount") or 0)
                    extra.append(
                        {
                            "build_type": "skill",
                            "sequence": [
                                {
                                    "id": int(aid),
                                    "name": self.get_ability_name(
                                        int(aid), level=level
                                    ),
                                }
                            ],
                            "pick_rate": 0.0,
                            "win_rate": _win_rate(wc, mc),
                            "games": mc,
                            "role": "",
                        }
                    )
                return [top_build] + extra

        builds = []
        for row in sorted(rows, key=lambda r: int(r.get("matchCount") or 0), reverse=True)[:take]:
            aid = row.get("abilityId")
            if not aid:
                continue
            level = int(row.get("level") or 0)
            mc = int(row.get("matchCount") or 0)
            wc = int(row.get("winCount") or 0)
            builds.append(
                {
                    "build_type": "skill",
                    "sequence": [
                        {
                            "id": int(aid),
                            "name": self.get_ability_name(int(aid), level=level),
                        }
                    ],
                    "pick_rate": 0.0,
                    "win_rate": _win_rate(wc, mc),
                    "games": mc,
                    "role": "",
                }
            )
        return builds
