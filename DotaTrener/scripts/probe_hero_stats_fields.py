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


def gql(q):
    return requests.post(URL, json={"query": q}, headers=HEADERS, timeout=30).json()


for type_name in [
    "HeroStatsType",
    "HeroPositionStatsType",
    "HeroStatsResponseType",
    "HeroStatType",
]:
    r = gql(
        f'{{ __type(name: "{type_name}") {{ name fields {{ name }} }} }}'
    )
    t = (r.get("data") or {}).get("__type")
    if t:
        print("===", type_name, "===")
        print([f["name"] for f in t.get("fields", [])])

# sample stats query with many fields
sample = gql(
    """
{
  heroStats {
    stats(heroIds: [12], bracketBasicIds: [DIVINE_IMMORTAL]) {
      heroId
      matchCount
      winCount
    }
  }
}
"""
)
print("\n=== minimal stats ===")
print(json.dumps(sample, indent=2)[:2000])

r = gql('{ __type(name: "HeroPositionTimeDetailType") { fields { name } } }')
print("=== HeroPositionTimeDetailType ===")
print([f["name"] for f in r["data"]["__type"]["fields"]])

candidates = [
    "goldPerMinute", "experiencePerMinute", "kills", "deaths", "assists",
    "lastHits", "denies", "heroDamage", "towerDamage", "heroHealing",
    "networth", "gpm", "xpm", "killParticipation", "cs", "level",
]
for field in candidates:
    q = (
        "{ heroStats { stats(heroIds:[12], bracketBasicIds:[DIVINE_IMMORTAL]) "
        "{ heroId matchCount %s } } }" % field
    )
    res = gql(q)
    if res.get("errors"):
        print(field, "ERR")
    else:
        print(field, res["data"]["heroStats"]["stats"][0].get(field))

extended = gql("""
{
  heroStats {
    statsTotals: stats(heroIds: [12], bracketBasicIds: [DIVINE_IMMORTAL]) {
      heroId matchCount winCount
      goldPerMinute xp kills deaths assists
      cs dn networth heroDamage towerDamage
      kDAAverage killContributionAverage
    }
    statsByPos: stats(heroIds: [12], groupByPosition: true, bracketBasicIds: [DIVINE_IMMORTAL]) {
      heroId position matchCount
      goldPerMinute xp kills deaths assists cs dn
    }
  }
}
""")
print("\n=== extended ===")
print(json.dumps(extended, indent=2)[:2500])
