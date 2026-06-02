# -*- coding: utf-8 -*-
import os, sys, django
sys.path.insert(0, '.')
os.environ['DJANGO_SETTINGS_MODULE'] = 'DotaTrener.settings'
django.setup()
from stratz_meta.services import StratzClient
client = StratzClient()

# Check the ranks type
q = '{ __type(name: "PlayerRankType") { fields { name type { name kind } } } }'
data = client.graphql(q)
import json
print("PlayerRankType fields:", json.dumps(data, indent=2, ensure_ascii=False))

# Check if there's a rank endpoint
q2 = '{ __type(name: "PlayerQuery") { fields { name type { name kind } } } }'
data2 = client.graphql(q2)
for f in data2['__type']['fields']:
    print(f['name'], '-', f['type']['name'])
