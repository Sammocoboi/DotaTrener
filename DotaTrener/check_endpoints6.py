import os, sys, django
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DotaTrener.settings')
django.setup()
from stratz_meta.services import StratzClient
client = StratzClient()
q = '{ hero(steamId: 67) { talents { abilityId slot } } }'
data = client.graphql(q)
import json
print(json.dumps(data, indent=2)[:3000])
