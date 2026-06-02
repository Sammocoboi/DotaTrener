# -*- coding: utf-8 -*-
import os, sys, django
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DotaTrener.settings')
django.setup()
from stratz_meta.services import StratzClient
from collections import defaultdict
client = StratzClient()

# For multiple heroes, test the rank-split approach
hero_ids = [67, 94, 14, 1, 2, 8]

for hero_id in hero_ids:
    q = f'{{ heroStats {{ talent(heroId: {hero_id}) {{ abilityId matchCount winCount }} abilityMinLevel(heroId: {hero_id}) {{ abilityId matchCount level }} }} }}'
    data = client.graphql(q)
    if not data:
        print(f"Hero {hero_id}: no data")
        continue

    hs = data.get('heroStats', {})
    talents = hs.get('talent') or []
    min_levels = hs.get('abilityMinLevel') or []

    tal_ids = [t['abilityId'] for t in talents]

    # Build level map for talents
    level_map = {}
    for m in min_levels:
        aid = m['abilityId']
        if aid in tal_ids:
            mc = m.get('matchCount') or 0
            lvl = m.get('level') or 0
            if aid not in level_map or mc > level_map[aid][0]:
                level_map[aid] = (mc, lvl)

    # Sort talents by most common level
    sorted_tal = sorted(talents, key=lambda t: level_map.get(t['abilityId'], (0, 99))[1])

    tiers = {0: 10, 1: 10, 2: 15, 3: 15, 4: 20, 5: 20, 6: 25, 7: 25}

    print(f"Hero {hero_id}:")
    for i, t in enumerate(sorted_tal):
        aid = t['abilityId']
        lvl = level_map.get(aid, (0, '?'))[1]
        tier = tiers.get(i, '?')
        print(f"  {aid}: lvl={lvl} -> tier {tier} (idx={i})")
