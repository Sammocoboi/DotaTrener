import os, sys, django
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DotaTrener.settings')
django.setup()
from stratz_meta.services import StratzClient
client = StratzClient()

# Try different heroes for starting items
for hero_id in [14, 1, 2, 3, 18, 55]:
    q = f'{{ heroStats {{ itemStartingPurchase(heroId: {hero_id}, bracketBasicIds: [DIVINE_IMMORTAL]) {{ itemId instance matchCount winCount winsAverage }} }} }}'
    data = client.graphql(q)
    import json
    result = data['heroStats']['itemStartingPurchase']
    if result:
        print(f"Hero {hero_id}: {json.dumps(result, indent=2)[:500]}")
    else:
        print(f"Hero {hero_id}: null")

# Try neutral items with different heroes
print("\n--- Neutral items ---")
q = '{ heroStats { itemNeutral(heroId: 67, bracketBasicIds: [DIVINE_IMMORTAL]) { itemId matchCount winCount } } }'
data = client.graphql(q)
print(json.dumps(data, indent=2)[:2000])
