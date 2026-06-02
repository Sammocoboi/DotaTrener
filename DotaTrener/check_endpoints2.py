import os, sys, django
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DotaTrener.settings')
django.setup()
from coaching.models import Ability
ids = [6148, 5993, 6901, 6900, 8040, 6902, 730, 6903]
abilities = Ability.objects.filter(steam_id__in=ids).values('steam_id', 'name', 'display_name')
for a in abilities:
    print(f"{a['steam_id']}: {a['name']} ({a['display_name']})")
from stratz_meta.services import StratzClient
client = StratzClient()
print("\n--- Starting items ---")
q = '{ heroStats { itemStartingPurchase(heroId: 67) { itemId instance matchCount winCount winsAverage } } }'
data = client.graphql(q)
import json
print(json.dumps(data, indent=2)[:5000])
print("\n--- Neutral items ---")
q2 = '{ heroStats { itemNeutral(heroId: 67) { itemId matchCount winCount } } }'
data2 = client.graphql(q2)
print(json.dumps(data2, indent=2)[:3000])
