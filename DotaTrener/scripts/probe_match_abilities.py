"""
Fetch full Stratz match player stats via GraphQL introspection.

Usage:
  python scripts/probe_match_abilities.py MATCH_ID
  python scripts/probe_match_abilities.py MATCH_ID --save
  python scripts/probe_match_abilities.py MATCH_ID --account-id 1138223098
  python scripts/probe_match_abilities.py MATCH_ID --account-id 76561199098488826
  python scripts/probe_match_abilities.py MATCH_ID --out path/to/file.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Dict, List, Optional, Set, Tuple

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DotaTrener.settings")

import django

django.setup()

import requests
from django.conf import settings

URL = settings.STRATZ_API_URL
HEADERS = {
    "Authorization": f"Bearer {settings.STRATZ_API_KEY}",
    "Content-Type": "application/json",
}

TYPE_FIELDS_QUERY = """
{
  __type(name: "%s") {
    fields(includeDeprecated: true) {
      name
      type {
        kind
        name
        ofType {
          kind
          name
          ofType {
            kind
            name
            ofType {
              kind
              name
            }
          }
        }
      }
    }
  }
}
"""

PLAYER_TYPE = "MatchPlayerType"
SELECTION_DEPTH = 2
STEAM_ID64_BASE = 76561197960265728
MATCH_EXPORT_DIR = os.path.join(BASE_DIR, "data", "matches")
# Skip nested match on player (full MatchType duplicates root query).
SKIP_FIELDS: Dict[str, Set[str]] = {
    PLAYER_TYPE: {"match"},
}
_type_fields_cache: Dict[str, List[Dict[str, Any]]] = {}


def gql(query: str) -> dict:
    response = requests.post(URL, json={"query": query}, headers=HEADERS, timeout=120)
    payload = response.json()
    if response.status_code >= 400 or payload.get("errors"):
        detail = payload.get("errors") or response.text
        raise RuntimeError(json.dumps(detail, ensure_ascii=False, indent=2))
    return payload


def unwrap_type(type_info: Dict[str, Any]) -> Tuple[str, Optional[str]]:
    """Return (kind, named_type) after peeling LIST and NON_NULL wrappers."""
    current = type_info
    while current.get("kind") in ("NON_NULL", "LIST"):
        inner = current.get("ofType")
        if not inner:
            break
        current = inner
    return current.get("kind", ""), current.get("name")


def get_type_fields(type_name: str) -> List[Dict[str, Any]]:
    if type_name in _type_fields_cache:
        return _type_fields_cache[type_name]

    result = gql(TYPE_FIELDS_QUERY % type_name)
    type_data = (result.get("data") or {}).get("__type")
    if not type_data:
        raise RuntimeError(f"GraphQL type not found: {type_name}")

    fields = type_data.get("fields") or []
    _type_fields_cache[type_name] = fields
    return fields


def build_field_selection(
    field_name: str,
    type_info: Dict[str, Any],
    depth: int,
    visited: Set[str],
) -> str:
    kind, named = unwrap_type(type_info)

    if kind in ("SCALAR", "ENUM"):
        return field_name

    if kind in ("OBJECT", "INTERFACE", "UNION") and named and depth > 0:
        if named in visited:
            return f"{field_name} {{ __typename }}"
        sub = build_selection(named, depth - 1, visited)
        if sub:
            return f"{field_name} {{ {sub} }}"
        return f"{field_name} {{ __typename }}"

    return field_name


def build_selection(type_name: str, depth: int, visited: Optional[Set[str]] = None) -> str:
    if depth <= 0:
        return ""

    visited = visited or set()
    if type_name in visited:
        return ""

    visited = visited | {type_name}
    skip = SKIP_FIELDS.get(type_name, set())
    fields = get_type_fields(type_name)
    parts: List[str] = []
    for field in fields:
        name = field.get("name")
        if not name or name.startswith("__") or name in skip:
            continue
        type_info = field.get("type") or {}
        parts.append(build_field_selection(name, type_info, depth, visited))

    return "\n      ".join(parts)


def build_match_query(match_id: int, player_depth: int) -> str:
    player_selection = build_selection(PLAYER_TYPE, player_depth)
    return f"""
{{
  match(id: {match_id}) {{
    id
    durationSeconds
    didRadiantWin
    startDateTime
    gameMode
    lobbyType
    players {{
      {player_selection}
    }}
  }}
}}
"""


def fetch_match(
    match_id: int,
    player_depth: int = SELECTION_DEPTH,
    verbose: bool = False,
) -> Dict[str, Any]:
    if verbose:
        fields = get_type_fields(PLAYER_TYPE)
        print("MatchPlayerType fields:", file=sys.stderr)
        for field in fields:
            kind, named = unwrap_type(field.get("type") or {})
            print(f"  {field['name']}: {kind} {named or ''}", file=sys.stderr)

    query = build_match_query(match_id, player_depth)
    if verbose:
        print("\nGenerated query:\n", query, file=sys.stderr)

    payload = gql(query)
    match = (payload.get("data") or {}).get("match")
    if not match:
        raise RuntimeError("No match data in response (match may not exist or is private)")
    return match


def resolve_steam_account_id(raw: int) -> int:
    """
    Stratz uses 32-bit steamAccountId (OpenDota account_id).
    Steam profile URLs use SteamID64 — convert automatically.
    """
    if raw >= STEAM_ID64_BASE:
        return raw - STEAM_ID64_BASE
    return raw


def filter_player(match: Dict[str, Any], account_id: int, raw_id: int) -> Dict[str, Any]:
    players = match.get("players") or []
    filtered = [
        p for p in players if int(p.get("steamAccountId") or 0) == account_id
    ]
    if not filtered:
        ids = sorted({int(p.get("steamAccountId") or 0) for p in players})
        hint = ""
        if raw_id >= STEAM_ID64_BASE:
            hint = (
                f" (you passed SteamID64; Stratz account id = {account_id})"
            )
        raise RuntimeError(
            f"Player not found in match (steamAccountId={account_id}{hint}). "
            f"IDs in this match: {ids}"
        )
    return {**match, "players": filtered}


def default_output_path(match_id: int, account_id: Optional[int]) -> str:
    os.makedirs(MATCH_EXPORT_DIR, exist_ok=True)
    if account_id is not None:
        name = f"match_{match_id}_player_{account_id}.json"
    else:
        name = f"match_{match_id}.json"
    return os.path.join(MATCH_EXPORT_DIR, name)


def output_json(data: Dict[str, Any], out_path: Optional[str]) -> str:
    if out_path:
        os.makedirs(os.path.dirname(os.path.abspath(out_path)) or ".", exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
        return os.path.abspath(out_path)

    json.dump(data, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return ""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch full Stratz match player stats (MatchPlayerType) as JSON"
    )
    parser.add_argument("match_id", type=int, help="Dota 2 match ID")
    parser.add_argument(
        "--out",
        nargs="?",
        const="",
        metavar="PATH",
        help=(
            "Write JSON to file. Without PATH saves to data/matches/match_<id>.json "
            "(use --save as shortcut)"
        ),
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help=f"Save JSON to {MATCH_EXPORT_DIR}/match_<id>.json (same as --out)",
    )
    parser.add_argument(
        "--account-id",
        type=int,
        metavar="ID",
        help=(
            "Keep one player: Stratz steamAccountId (e.g. 1138223098) "
            "or SteamID64 from profile (e.g. 76561199098488826)"
        ),
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print schema fields and generated query to stderr",
    )
    parser.add_argument(
        "--depth",
        type=int,
        default=SELECTION_DEPTH,
        help=f"Nested object depth for player fields (default {SELECTION_DEPTH})",
    )
    return parser.parse_args()


def resolve_out_path(
    args: argparse.Namespace, match_id: int, account_id: Optional[int]
) -> Optional[str]:
    if args.save:
        return default_output_path(match_id, account_id)
    if args.out is not None:
        if args.out == "":
            return default_output_path(match_id, account_id)
        return args.out
    return None


def main() -> int:
    args = parse_args()
    depth = max(1, args.depth)
    account_id: Optional[int] = None
    raw_account_id: Optional[int] = None

    if args.account_id is not None:
        raw_account_id = args.account_id
        account_id = resolve_steam_account_id(raw_account_id)
        if raw_account_id != account_id and args.verbose:
            print(
                f"Converted SteamID64 {raw_account_id} -> steamAccountId {account_id}",
                file=sys.stderr,
            )

    try:
        match = fetch_match(args.match_id, player_depth=depth, verbose=args.verbose)
        if account_id is not None:
            match = filter_player(match, account_id, raw_account_id)
        out_path = resolve_out_path(args, args.match_id, account_id)
        written = output_json(match, out_path)
        if written:
            print(f"Saved: {written}", file=sys.stderr)
    except (RuntimeError, requests.RequestException) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
