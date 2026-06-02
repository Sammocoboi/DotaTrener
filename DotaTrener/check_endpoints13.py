import os, sys, django
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DotaTrener.settings')
django.setup()
from stratz_meta.services import StratzClient
client = StratzClient()

# Check guide endpoint
q = '{ heroStats { guide(heroId: 67) { ... } } }'
# First check the type
q2 = '{ __type(name: "HeroGuideType") { fields { name type { name } } } }'
data = client.graphql(q2)
import json
print("HeroGuideType fields:")
print(json.dumps(data, indent=2)[:2000])
