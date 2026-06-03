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


def _bracket_basic_frag(rank: Optional[str]) -> str:
    """bracketBasicIds for stats, item builds, skill builds."""
    basic_frag, _ = _bracket_fragments(rank)
    return basic_frag


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


STATS_PERFORMANCE_FIELDS = (
    "kills deaths assists cs dn networth xp heroDamage towerDamage "
    "kDAAverage killContributionAverage goldPerMinute"
)


def _float_or_none(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        return round(float(value), 2)
    except (TypeError, ValueError):
        return None


def _performance_from_stat_row(row: Dict[str, Any]) -> Dict[str, Any]:
    """Averages per game from heroStats.stats (HeroPositionTimeDetailType)."""
    avg_minutes = float(getattr(settings, "STRATZ_AVG_MATCH_MINUTES", 45) or 45)
    networth = _float_or_none(row.get("networth"))
    xp_total = _float_or_none(row.get("xp"))
    gpm = _float_or_none(row.get("goldPerMinute"))
    if gpm is None and networth is not None and avg_minutes > 0:
        gpm = round(networth / avg_minutes, 1)
    xpm = None
    if xp_total is not None and avg_minutes > 0:
        xpm = round(xp_total / avg_minutes, 1)
    return {
        "avg_kills": _float_or_none(row.get("kills")),
        "avg_deaths": _float_or_none(row.get("deaths")),
        "avg_assists": _float_or_none(row.get("assists")),
        "avg_gpm": gpm,
        "avg_xpm": xpm,
        "avg_last_hits": _float_or_none(row.get("cs")),
        "avg_denies": _float_or_none(row.get("dn")),
        "avg_networth": networth,
        "avg_hero_damage": _float_or_none(row.get("heroDamage")),
        "avg_tower_damage": _float_or_none(row.get("towerDamage")),
        "avg_kda": _float_or_none(row.get("kDAAverage")),
        "avg_kill_participation": _float_or_none(row.get("killContributionAverage")),
    }


def _meta_from_totals(
    win_count: int,
    match_count: int,
    roles: Optional[Dict[str, float]] = None,
    pick_rate: float = 0.0,
    ban_rate: float = 0.0,
    performance: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    meta = {
        "pick_rate": pick_rate,
        "win_rate": _win_rate(win_count, match_count),
        "ban_rate": ban_rate,
        "games_played": match_count,
        "roles": roles or {},
    }
    if performance:
        meta.update(performance)
    return meta


def _format_internal_name(name: str) -> str:
    if not name:
        return ""
    return " ".join(part.capitalize() for part in name.replace("_", " ").split())


class StratzClient:
    def __init__(self, token: Optional[str] = None):
        self.api_key = token or settings.STRATZ_API_KEY
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
        self._item_shortnames: Optional[Dict[int, str]] = None
        self._ability_names: Optional[Dict[int, str]] = None
        self._ability_shortnames: Optional[Dict[int, str]] = None

    def load_item_catalog(self) -> Dict[int, str]:
        if self._item_names is not None:
            return self._item_names
        catalog: Dict[int, str] = {}
        shortnames: Dict[int, str] = {}
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
                sn = item.get("shortName")
                if sn:
                    shortnames[int(item_id)] = sn
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
        self._item_shortnames = shortnames
        logger.info("Loaded %s item names from Stratz", len(catalog))
        return catalog

    def get_item_image_url(self, item_id: int) -> str:
        if self._item_shortnames is None:
            self.load_item_catalog()
        sn = (self._item_shortnames or {}).get(item_id, "")
        if sn:
            return f"https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/{sn}.png"
        return ""

    def load_ability_catalog(self) -> Dict[int, str]:
        if self._ability_names is not None:
            return self._ability_names
        catalog: Dict[int, str] = {}
        shortnames: Dict[int, str] = {}
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
                sn = ability.get("name")
                if sn:
                    shortnames[int(ability_id)] = sn
        self._ability_names = catalog
        self._ability_shortnames = shortnames
        logger.info("Loaded %s ability names from Stratz", len(catalog))
        return catalog

    def get_ability_image_url(self, ability_id: int) -> str:
        if self._ability_shortnames is None:
            self.load_ability_catalog()
        sn = (self._ability_shortnames or {}).get(ability_id, "")
        if sn:
            return f"https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/abilities/{sn}.png"
        return ""

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
              heroId winCount matchCount {STATS_PERFORMANCE_FIELDS}
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
            performance = _performance_from_stat_row(totals) if totals else {}
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
                    win_count,
                    match_count,
                    roles=roles,
                    pick_rate=pick_rate,
                    performance=performance,
                )
                continue

            if totals and int(totals.get("matchCount") or 0) > 0:
                result[hid] = _meta_from_totals(
                    int(totals.get("winCount") or 0),
                    int(totals.get("matchCount") or 0),
                    roles=roles,
                    pick_rate=pick_rate,
                    performance=performance,
                )
                continue

            if pos_rows:
                win_total = sum(int(p.get("winCount") or 0) for p in pos_rows)
                match_total = sum(int(p.get("matchCount") or 0) for p in pos_rows)
                if match_total:
                    result[hid] = _meta_from_totals(
                        win_total,
                        match_total,
                        roles=roles,
                        pick_rate=pick_rate,
                        performance=performance,
                    )
                    continue

            fallback = self._fetch_meta_win_day(hid, rank)
            if fallback:
                fallback["roles"] = roles or fallback.get("roles", {})
                fallback["pick_rate"] = pick_rate or fallback.get("pick_rate", 0.0)
                fallback.update(performance)
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
        rank: Optional[str] = "DIVINE_IMMORTAL",
        take: int = 100,
    ) -> List[Dict[str, Any]]:
        if build_type == "item":
            return self._fetch_item_builds(hero_id, take, rank=rank)
        return self._fetch_skill_builds(hero_id, take, rank=rank)

    def _fetch_item_builds(
        self, hero_id: int, take: int, rank: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        bracket_frag = _bracket_basic_frag(rank)
        query = f"""{{
          heroStats {{
            itemFullPurchase(heroId: {hero_id}{bracket_frag}) {{ itemId time winCount matchCount }}
            itemBootPurchase(heroId: {hero_id}{bracket_frag}) {{ itemId winCount matchCount }}
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
        endgame_seq = self._endgame_sequence_from_rows(rows)
        if endgame_seq:
            endgame_ids = {entry["id"] for entry in endgame_seq}
            endgame_rows = [
                r
                for r in rows
                if r.get("itemId") and int(r["itemId"]) in endgame_ids
            ]
            match_total = sum(int(r.get("matchCount") or 0) for r in endgame_rows)
            win_total = sum(int(r.get("winCount") or 0) for r in endgame_rows)
            builds.append(
                {
                    "build_type": "item",
                    "sequence": endgame_seq,
                    "pick_rate": 0.0,
                    "win_rate": _win_rate(win_total, match_total),
                    "games": match_total,
                    "role": "endgame",
                }
            )

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

    def _endgame_sequence_from_rows(
        self, rows: List[Dict[str, Any]], limit: int = 6
    ) -> List[Dict[str, Any]]:
        from stratz_meta.match_items import build_endgame_sequence_from_purchase_rows

        return build_endgame_sequence_from_purchase_rows(
            rows, self.get_item_name, limit=limit
        )

    def _fetch_skill_builds(
        self, hero_id: int, take: int, rank: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        bracket_frag = _bracket_basic_frag(rank)
        query = f"""{{
          heroStats {{
            abilityMaxLevel(heroId: {hero_id}{bracket_frag}) {{ abilityId level winCount matchCount }}
          }}
        }}"""
        data = self.graphql(query)
        if not data:
            return []
        hs = data.get("heroStats", {})
        rows = list(hs.get("abilityMaxLevel") or [])
        if not rows:
            return []

        by_ability: Dict[int, Dict[str, int]] = {}
        for row in rows:
            aid = row.get("abilityId")
            lvl = int(row.get("level") or 0)
            mc = int(row.get("matchCount") or 0)
            wc = int(row.get("winCount") or 0)
            if aid is None or mc <= 0 or lvl <= 0:
                continue
            aid = int(aid)
            if aid not in by_ability or mc > by_ability[aid].get("matchCount", 0):
                by_ability[aid] = {"level": lvl, "matchCount": mc, "winCount": wc}

        if not by_ability:
            return []

        ordered = sorted(by_ability.items(), key=lambda x: x[1]["level"])
        ability_ids = [int(aid) for aid, _ in ordered if aid]

        first = ability_ids[0] if len(ability_ids) > 0 else None
        second = ability_ids[1] if len(ability_ids) > 1 else None
        third = ability_ids[2] if len(ability_ids) > 2 else None
        ult = next((a for a in ability_ids[3:] if a != first and a != second and a != third), None)

        level_map = {
            1: first, 2: first, 3: second or first,
            4: first, 5: first,
            6: ult or third or first,
            7: (second or first) if (second and first) else first,
            8: (third or second or first) if (first and second) else first,
            9: (third or second or first) if (first and second) else first,
            10: (second or first) if (first and second) else first,
        }

        seq = [
            {"id": level_map[lvl], "name": self.get_ability_name(level_map[lvl])}
            for lvl in range(1, 11)
            if level_map.get(lvl)
        ]

        match_total = max(v["matchCount"] for v in by_ability.values())
        win_total = max(v["winCount"] for v in by_ability.values())
        top_build = {
            "build_type": "skill",
            "sequence": seq,
            "pick_rate": 0.0,
            "win_rate": _win_rate(win_total, match_total) if match_total else 0.0,
            "games": match_total,
            "role": "",
        }
        return [top_build]

    def fetch_hero_talents(
        self,
        hero_id: int,
        rank: Optional[str] = "DIVINE_IMMORTAL",
    ) -> List[Dict[str, Any]]:
        bracket_frag = _bracket_basic_frag(rank)
        query = f"""{{
          heroStats {{
            talent(heroId: {hero_id}{bracket_frag}) {{ abilityId matchCount winCount }}
            abilityMinLevel(heroId: {hero_id}{bracket_frag}) {{ abilityId matchCount level }}
          }}
        }}"""
        data = self.graphql(query)
        if not data:
            return []
        hs = data.get("heroStats", {})
        talents = list(hs.get("talent") or [])
        min_levels = list(hs.get("abilityMinLevel") or [])
        if not talents:
            return []

        tal_ids = [t["abilityId"] for t in talents]

        level_map: Dict[int, Tuple[int, int]] = {}
        for m in min_levels:
            aid = m.get("abilityId")
            mc = m.get("matchCount") or 0
            lvl = m.get("level") or 0
            if aid in tal_ids and mc > level_map.get(aid, (0,))[0]:
                level_map[aid] = (mc, lvl)

        sorted_tal = sorted(
            talents,
            key=lambda t: level_map.get(t["abilityId"], (0, 99))[1],
        )

        tiers = [10, 10, 15, 15, 20, 20, 25, 25]

        result: List[Dict[str, Any]] = []
        tier_games: Dict[int, int] = {}
        for i, t in enumerate(sorted_tal):
            if i >= 8:
                break
            tier = tiers[i]
            mc = int(t.get("matchCount") or 0)
            tier_games[tier] = tier_games.get(tier, 0) + mc

        for i, t in enumerate(sorted_tal):
            if i >= 8:
                break
            aid = t["abilityId"]
            tier = tiers[i]
            mc = int(t.get("matchCount") or 0)
            wc = int(t.get("winCount") or 0)
            total = tier_games.get(tier, 1)
            pick_rate = round(mc / total * 100, 1) if total else 0
            win_rate = _win_rate(wc, mc)
            slot = "left" if i % 2 == 0 else "right"
            result.append({
                "abilityId": aid,
                "tier": tier,
                "slot": slot,
                "name": self.get_ability_name(aid),
                "matchCount": mc,
                "winCount": wc,
                "win_rate": win_rate,
                "pick_rate": pick_rate,
            })

        return result

    def fetch_player_matches(
        self,
        steam_account_id: int,
        take: int = 20,
        patch_id: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        patch_frag = f", patch: {patch_id}" if patch_id else ""
        query = f"""{{
          player(steamAccountId: {steam_account_id}) {{
            steamAccountId
            winCount
            matches(request: {{ take: {take}{patch_frag} }}) {{
              id
              didRadiantWin
              startDateTime
              gameMode
              players {{
                steamAccountId
                heroId
                isRadiant
                kills
                deaths
                assists
                goldPerMinute
                experiencePerMinute
                numLastHits
                numDenies
                heroDamage
                towerDamage
                networth
              }}
            }}
          }}
        }}"""
        data = self.graphql(query)
        if not data:
            return []
        player = data.get("player") or {}
        return player.get("matches") or []

    def fetch_player_profile(
        self, steam_account_id: int
    ) -> Optional[Dict[str, Any]]:
        query = f"""{{
          player(steamAccountId: {steam_account_id}) {{
            steamAccountId
            winCount
            matchCount
          }}
        }}"""
        data = self.graphql(query)
        if not data:
            return None
        player = data.get("player") or {}
        win = int(player.get("winCount") or 0)
        total = int(player.get("matchCount") or 0)
        lose = total - win
        player["loseCount"] = lose
        player["winRate"] = round(win / total * 100, 1) if total else 0
        return player

    def fetch_player_rank(self, steam_account_id: int) -> Dict[str, Any]:
        query = f"""{{
          player(steamAccountId: {steam_account_id}) {{
            steamAccountId
            steamAccount {{
              seasonRank
              seasonLeaderboardRank
            }}
          }}
        }}"""
        data = self.graphql(query)
        if not data:
            return {"seasonRank": 0, "seasonLeaderboardRank": None}
        sa = data.get("player", {}).get("steamAccount") or {}
        return {
            "seasonRank": sa.get("seasonRank") or 0,
            "seasonLeaderboardRank": sa.get("seasonLeaderboardRank"),
        }
