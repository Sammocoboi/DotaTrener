# -*- coding: utf-8 -*-
import os, sys, django
sys.path.insert(0, '.')
os.environ['DJANGO_SETTINGS_MODULE'] = 'DotaTrener.settings'
django.setup()
from stratz_meta.services import StratzClient
client = StratzClient()

q = '{ __schema { types { name } } }'
data = client.graphql(q)
for t in data['__schema']['types']:
    name = t.get('name', '')
    if 'Rank' in name or 'rank' in name:
        print(name)
