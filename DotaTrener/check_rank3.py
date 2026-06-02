# -*- coding: utf-8 -*-
import os, sys, django
sys.path.insert(0, '.')
os.environ['DJANGO_SETTINGS_MODULE'] = 'DotaTrener.settings'
django.setup()
from stratz_meta.services import StratzClient
client = StratzClient()

# Check RankBracket enum values
q = '{ __type(name: "RankBracket") { enumValues { name } } }'
data = client.graphql(q)
import json
print("RankBracket:", [v['name'] for v in data['__type']['enumValues']])

q2 = '{ __type(name: "RankBracketBasicEnum") { enumValues { name } } }'
data2 = client.graphql(q2)
print("RankBracketBasicEnum:", [v['name'] for v in data2['__type']['enumValues']])

# Try to get the actual seasonRank value
q3 = '{ player(steamAccountId: 1138223098) { steamAccountId steamAccount { seasonRank seasonLeaderboardRank } } }'
data3 = client.graphql(q3)
print(json.dumps(data3, indent=2, ensure_ascii=False))
