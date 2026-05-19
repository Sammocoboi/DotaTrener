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

q = """
{
  __type(name: "HeroStatsQuery") {
    fields {
      name
      args { name }
    }
  }
}
"""
r = requests.post(
    settings.STRATZ_API_URL,
    json={"query": q},
    headers={
        "Authorization": f"Bearer {settings.STRATZ_API_KEY}",
        "Content-Type": "application/json",
    },
    timeout=30,
).json()
for f in r["data"]["__type"]["fields"]:
    if "ability" in f["name"].lower():
        print(f["name"], f.get("args", []))
