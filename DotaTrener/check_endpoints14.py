import os, sys, django
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DotaTrener.settings')
django.setup()
from stratz_meta.services import StratzClient
client = StratzClient()

# Try with stratzApi wrapper
q = '{ stratzApi { heroStats { itemStartingPurchase(heroId: 67, bracketBasicIds: [DIVINE_IMMORTAL]) { itemId instance matchCount winCount } } } }'
data = client.graphql(q)
import json
print("stratzApi wrapper:")
print(json.dumps(data, indent=2)[:2000])
