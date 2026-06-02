import os, sys
sys.path.insert(0, 'D:/Documents/GitHub/DotaTrener/DotaTrener')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DotaTrener.settings')
import django
django.setup()
from stratz_meta.services import StratzClient
from abilities.models import Ability
client = StratzClient()
# Check ability names for these talent IDs
ids = [6148, 5993, 6901, 6900, 8040, 6902, 730, 6903]
abilities = Ability.objects.filter(stratz_id__in=ids).values('stratz_id', 'name', 'language_display_name')
for a in abilities:
    print(f"{a['stratz_id']}: {a['name']} ({a['language_display_name']})")
# Test starting items
print("\n--- Starting items ---")
q = '{ heroStats { itemStartingPurchase(heroId: 67) { itemId instance matchCount winCount winsAverage } } }'
data = client.graphql(q)
import json
print(json.dumps(data, indent=2)[:5000])
print("\n--- Neutral items ---")
q2 = '{ heroStats { itemNeutral(heroId: 67) { itemId matchCount winCount } } }'
data2 = client.graphql(q2)
print(json.dumps(data2, indent=2)[:5000])
