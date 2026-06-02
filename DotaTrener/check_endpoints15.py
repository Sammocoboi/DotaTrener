import os, sys, django
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DotaTrener.settings')
django.setup()
from stratz_meta.services import StratzClient
client = StratzClient()

# Check stratz field
q = '{ __type(name: "StratzQuery") { fields { name type { name } } } }'
data = client.graphql(q)
import json
for f in data['__type']['fields']:
    print(f['name'], '-', f['type']['name'])
