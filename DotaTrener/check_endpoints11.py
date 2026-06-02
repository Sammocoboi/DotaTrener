import os, sys, django
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DotaTrener.settings')
django.setup()
from stratz_meta.services import StratzClient
client = StratzClient()

# Try itemStartingPurchase with filters
queries = [
    '{ heroStats { itemStartingPurchase(heroId: 94, bracketBasicIds: [IMMORTAL], position: POSITION_4) { itemId instance matchCount winCount winsAverage } } }',
    '{ heroStats { itemStartingPurchase(heroId: 94, bracketBasicIds: [IMMORTAL], position: POSITION_5) { itemId instance matchCount winCount winsAverage } } }',
    '{ heroStats { itemStartingPurchase(heroId: 94, bracketBasicIds: [DIVINE_IMMORTAL]) { itemId instance matchCount winCount winsAverage } } }',
    '{ heroStats { itemStartingPurchase(heroId: 96, bracketBasicIds: [DIVINE_IMMORTAL]) { itemId instance matchCount winCount winsAverage } } }',
]

for i, q in enumerate(queries):
    data = client.graphql(q)
    import json
    print(f"\n--- Query {i+1} ---")
    print(json.dumps(data, indent=2)[:1000])
