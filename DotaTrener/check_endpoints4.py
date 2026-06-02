import os, sys, django
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DotaTrener.settings')
django.setup()
from stratz_meta.services import StratzClient
client = StratzClient()
q = '{ __schema { queryType { fields { name type { name kind } } } } }'
data = client.graphql(q)
import json
# Find heroStats type
for f in data['__schema']['queryType']['fields']:
    if f['name'] == 'heroStats':
        print(json.dumps(f, indent=2))
        break
