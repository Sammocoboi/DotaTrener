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
MID = 8814904651


def gql(query: str) -> dict:
    r = requests.post(URL, json={"query": query}, headers=HEADERS, timeout=30)
    return r.json()


# MatchPlayerType fields related to builds
intro = gql(
    """
{
  __type(name: "MatchPlayerType") {
    fields {
      name
    }
  }
}
"""
)
print("MatchPlayerType fields:")
for f in intro["data"]["__type"]["fields"]:
    n = f["name"].lower()
    if any(x in n for x in ("abilit", "skill", "talent", "build", "item", "playback", "stats")):
        print(" ", f["name"])

# Probe abilities subfields
intro2 = gql(
    """
{
  __type(name: "MatchPlayerAbilityType") {
    fields { name type { name kind ofType { name } } }
  }
}
"""
)
print("\nMatchPlayerAbilityType fields:")
data2 = intro2.get("data")
if data2 and data2.get("__type"):
    for f in data2["__type"]["fields"]:
        print(" ", f["name"], f["type"])
else:
    print(json.dumps(intro2, indent=2)[:500])

# Actual match query - Slardar heroId 28? User had Slardar - hero 28 is slardar
match_q = f"""
{
  
    match(id: 8814904651) {
      id
      durationSeconds
      players {
        steamAccountId
        heroId
        level
        kills
        deaths
        assists
        networth
        goldPerMinute
        experiencePerMinute
        item0Id
        item1Id
        item2Id
        item3Id
        item4Id
        item5Id
        abilities {
          abilityId
          level
          time
        }
        stats {
          lastHits
          denies
        }
        playbackData {
          roshanKills
        }
      }
    
  }
}
"""
print("\nMatch abilities sample:")
res = gql(match_q)
print(json.dumps(res, indent=2)[:3000])
