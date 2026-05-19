"""Probe Stratz GraphQL schema. Run: python scripts/probe_stratz_schema.py"""
import json
import os
import sys

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


def gql(query: str) -> dict:
    r = requests.post(URL, json={"query": query}, headers=HEADERS, timeout=30)
    return r.json()


def main():
    probes = {
        "winGameVersion_field": """
        { __type(name: "HeroStatsQuery") {
          fields { name args { name type { name kind ofType { name kind ofType { name } } } } }
        } }""",
        "winGameVersion": """
        { heroStats { winGameVersion(heroIds: [1]) {
            heroId gameVersionId winCount matchCount
          } } }""",
        "HeroGuideType": """
        { __type(name: "HeroGuideType") { fields { name } } }""",
        "guide": """
        { heroStats { guide(heroId: 1, take: 2) {
            guides { itemIds title matchId }
          } } }""",
        "stats_positions": """
        { heroStats { stats(heroIds: [1], groupByPosition: true) {
            heroId position winCount matchCount
          } } }""",
        "RankBracketBasicEnum": """
        { __type(name: "RankBracketBasicEnum") { enumValues { name } } }""",
        "winDay_bracket": """
        { heroStats { winDay(heroIds: [1], bracketBasicIds: [DIVINE]) {
            heroId winCount matchCount
          } } }""",
        "winDay_batch": """
        { heroStats { winDay(heroIds: [1, 2, 3]) {
            heroId winCount matchCount
          } } }""",
        "guide2": """
        { heroStats { guide(heroId: 1, take: 5) { guides { itemIds } } } }""",
        "itemStarting": """
        { heroStats { itemStartingPurchase(heroId: 1) { itemId winCount matchCount } } }""",
        "itemBoot": """
        { heroStats { itemBootPurchase(heroId: 1) { itemId winCount matchCount } } }""",
        "winGV_bracketIds": """
        { heroStats { winGameVersion(heroIds: [1], bracketIds: [DIVINE]) {
            heroId gameVersionId winCount matchCount
          } } }""",
        "stats_bracket": """
        { heroStats { stats(heroIds: [1], groupByPosition: true, bracketBasicIds: [DIVINE_IMMORTAL]) {
            heroId position winCount matchCount
          } } }""",
        "items": """
        { constants { items { id displayName shortName } } }""",
        "HeroAbilityType": """
        { __type(name: "HeroAbilityType") { fields { name type { name kind ofType { name } } } } }""",
        "hero_abilities": """
        { constants { heroes { id abilities { abilityId slot } } } }""",
        "abilities_global": """
        { constants { abilities { id name language { displayName } } } }""",
    }
    for name, query in probes.items():
        print("=" * 60, name)
        print(json.dumps(gql(query), indent=2)[:5000])


if __name__ == "__main__":
    main()
