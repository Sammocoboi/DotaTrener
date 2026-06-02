import os, sys, django
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DotaTrener.settings')
django.setup()
from stratz_meta.services import StratzClient
client = StratzClient()
q = '{ __type(name: "HeroAbilityTalentType") { fields { name type { name kind } } } }'
data = client.graphql(q)
import json
print(json.dumps(data, indent=2))
