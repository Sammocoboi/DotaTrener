"""
Fetch full Stratz match player stats via GraphQL introspection.
1
Usage:
  python scripts/probe_match_abilities.py MATCH_ID
  python scripts/probe_match_abilities.py MATCH_ID --out match.json
  python scripts/probe_match_abilities.py MATCH_ID --account-id STEAM_ID
  python scripts/probe_match_abilities.py MATCH_ID --verbose
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
    parent_type: str,
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
        parts.append(
            build_field_selection(name, type_info, depth, visited, type_name)
        )

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


def filter_player(match: Dict[str, Any], account_id: int) -> Dict[str, Any]:
    players = match.get("players") or []
    filtered = [
        p for p in players if int(p.get("steamAccountId") or 0) == account_id
    ]
    if not filtered:
        raise RuntimeError(
            f"Player with steamAccountId={account_id} not found in match"
        )
    return {**match, "players": filtered}


def output_json(data: Dict[str, Any], out_path: Optional[str]) -> None:
    if out_path:
        with open(out_path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
    else:
        json.dump(data, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch full Stratz match player stats (MatchPlayerType) as JSON"
    )
    parser.add_argument("match_id", type=int, help="Dota 2 match ID")
    parser.add_argument("--out", metavar="PATH", help="Write JSON to file instead of stdout")
    parser.add_argument(
        "--account-id",
        type=int,
        metavar="STEAM_ID",
        help="Keep only one player (steamAccountId)",
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


def main() -> int:
    args = parse_args()
    depth = max(1, args.depth)

    try:
        match = fetch_match(args.match_id, player_depth=depth, verbose=args.verbose)
        if args.account_id is not None:
            match = filter_player(match, args.account_id)
        output_json(match, args.out)
    except (RuntimeError, requests.RequestException) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
