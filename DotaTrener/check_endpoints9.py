import os, sys, django
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DotaTrener.settings')
django.setup()
from stratz_meta.services import StratzClient
client = StratzClient()
q = '{ __type(name: "HeroAbilityMinLevelType") { fields { name type { name kind } } } }'
data = client.graphql(q)
import json
print(json.dumps(data, indent=2))
q2 = '{ heroStats { abilityMinLevel(heroId: 67) { abilityId matchCount winCount level } } }'
data2 = client.graphql(q2)
print(json.dumps(data2, indent=2)[:3000])
