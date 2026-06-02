import os, sys, django
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DotaTrener.settings')
django.setup()
from stratz_meta.services import StratzClient
client = StratzClient()
# Check all query args for something with HeroTalentType
q = '{ __schema { types { name fields { name type { name } args { name type { name } } } } } }'
data = client.graphql(q)
for t in data.get('__schema', {}).get('types', []):
    if t.get('name') in ['DotaQuery', 'HeroStatsQuery']:
        print(f"\n--- {t['name']} ---")
        for f in t.get('fields', []):
            if 'talent' in f['name'].lower() or 'talents' in f['name'].lower():
                print(f['name'], f['type']['name'])
