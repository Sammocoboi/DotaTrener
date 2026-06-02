import os, sys, django
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DotaTrener.settings')
django.setup()
from stratz_meta.services import StratzClient
client = StratzClient()
q = '{ __schema { queryType { fields { name type { name } args { name type { name kind } } } } } }'
data = client.graphql(q)
import json
for f in data['__schema']['queryType']['fields']:
    args = [a['name'] for a in f.get('args', [])]
    if 'hero' in f['name'].lower():
        print(f['name'], f['type']['name'], args)
