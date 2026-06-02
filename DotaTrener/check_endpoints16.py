import os, sys, django
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DotaTrener.settings')
django.setup()
from collections import defaultdict
from stratz_meta.services import StratzClient
client = StratzClient()

# Get talents for Spectre (67)
talent_q = '{ heroStats { talent(heroId: 67) { abilityId matchCount winCount } } }'
talent_data = client.graphql(talent_q)
abilities = [t['abilityId'] for t in talent_data['heroStats']['talent']]
print(f"Talent ability IDs: {abilities}")

# Get abilityMinLevel for these abilities
min_level_q = f'{{ heroStats {{ abilityMinLevel(heroId: 67) {{ abilityId matchCount winCount level }} }} }}'
min_level_data = client.graphql(min_level_q)

# Map ability -> most common level
ability_levels = defaultdict(list)
for entry in min_level_data['heroStats']['abilityMinLevel']:
    aid = entry['abilityId']
    if aid in abilities:
        ability_levels[aid].append((entry['matchCount'], entry['level']))

print("\nTalent level mapping (most common level):")
for aid in abilities:
    if aid in ability_levels:
        entries = sorted(ability_levels[aid], key=lambda x: -x[0])
        common_level = entries[0][1]
        total_games = sum(e[0] for e in entries)
        print(f"  {aid}: most common level = {common_level} (games: {total_games})")
    else:
        print(f"  {aid}: no abilityMinLevel data")
