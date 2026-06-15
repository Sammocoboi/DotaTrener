HERO_POSITIONS: dict[int, list[int]] = {
    1: [1],       # Anti-Mage
    2: [3],       # Axe
    3: [5],       # Bane
    4: [1],       # Bloodseeker
    5: [5],       # Crystal Maiden
    6: [5],       # Dazzle
    7: [4],       # Earthshaker
    8: [1],       # Juggernaut
    9: [2],       # Mirana
    10: [1],      # Morphling
    11: [2],      # Shadow Fiend
    12: [1],      # Phantom Lancer
    13: [2],      # Puck
    14: [3],      # Sand King
    15: [2],      # Storm Spirit
    16: [1],      # Sven
    17: [3],      # Tiny
    18: [2],      # Void Spirit
    19: [1],      # Weaver
    20: [3],      # Nature's Prophet
    21: [2],      # Lina
    22: [1],      # Lifestealer
    23: [3],      # Dark Seer
    24: [1],      # Clinkz
    25: [5],      # Omniknight
    26: [4],      # Enchantress
    27: [5],      # Witch Doctor
    28: [5],      # Lich
    29: [4],      # Shadow Shaman
    31: [4],      # Jakiro
    32: [1],      # Chaos Knight
    33: [5],      # Treant Protector
    34: [2],      # Invoker
    35: [1],      # Ursa
    36: [1],      # Gyrocopter
    37: [5],      # Warlock
    38: [3],      # Beastmaster
    39: [2],      # Queen of Pain
    40: [3],      # Venomancer
    41: [1],      # Faceless Void
    42: [1],      # Wraith King
    43: [2],      # Death Prophet
    44: [1],      # Phantom Assassin
    45: [2],      # Pugna
    46: [2],      # Templar Assassin
    47: [1],      # Naga Siren
    49: [4],      # Spirit Breaker
    50: [2],      # Broodmother
    51: [5],      # Chen
    52: [1],      # Spectre
    53: [5],      # Ancient Apparition
    54: [3],      # Doom
    55: [4],      # Dark Willow
    56: [4],      # Clockwerk
    57: [2],      # Huskar
    58: [5],      # Shadow Demon
    59: [5],      # Keeper of the Light
    60: [5],      # Io
    61: [3],      # Slardar
    62: [2],      # Tinker
    64: [2],      # Sniper
    65: [2],      # Necrophos
    66: [1],      # Slark
    67: [1],      # Medusa
    68: [1],      # Troll Warlord
    69: [3],      # Centaur Warrunner
    71: [1],      # Lone Druid
    73: [4],      # Rubick
    75: [1],      # Luna
    76: [2],      # Ember Spirit
    77: [4],      # Earth Spirit
    78: [3],      # Underlord
    79: [3],      # Timbersaw
    80: [4],      # Bounty Hunter
    81: [5],      # Skywrath Mage
    82: [2],      # Outworld Destroyer
    83: [3],      # Elder Titan
    84: [3],      # Legion Commander
    85: [4],      # Techies
    86: [1],      # Terrorblade
    87: [5],      # Phoenix
    88: [5],      # Oracle
    89: [5],      # Winter Wyvern
    90: [1],      # Arc Warden
    91: [1],      # Monkey King
    92: [3],      # Pangolier
    93: [4],      # Dark Willow (dup)
    94: [3],      # Mars
    95: [2],      # Void Spirit (dup)
    96: [4],      # Snapfire
    97: [5],      # Grimstroke
    98: [4],      # Hoodwink
    99: [3],      # Dawnbreaker
    100: [4],     # Marci
    101: [3],     # Primal Beast
    102: [1],     # Muerta
    103: [4],     # Ringmaster
    104: [4],     # Batrider
    105: [5],     # Abaddon
    106: [1],     # Alchemist
    111: [3],     # Brewmaster
    112: [3],     # Bristleback
    121: [2],     # Dragon Knight
    129: [4],     # Io (dup)
    135: [2],     # Kunkka
    136: [2],     # Leshrac
    142: [1],     # Lycan
    143: [3],     # Magnus
    149: [3],     # Night Stalker
    151: [5],     # Ogre Magi
    158: [1],     # Razor
    159: [4],     # Riki
    164: [5],     # Silencer
    176: [3],     # Tidehunter
    183: [4],     # Tusk
    186: [5],     # Vengeful Spirit
    188: [5],     # Viper
    191: [1],     # Wraith King (dup)
    194: [1],     # Drow Ranger
    198: [3],     # Legion Commander (dup)
    200: [5],     # Phoenix (dup)
    220: [3],     # Brewmaster (dup)
    221: [3],     # Bristleback (dup)
    224: [2],     # Dragon Knight (dup)
    226: [4],     # Earth Spirit (dup)
    228: [4],     # Enchantress (dup)
    232: [1],     # Juggernaut (dup)
    234: [2],     # Leshrac (dup)
    238: [1],     # Lycan (dup)
    239: [3],     # Magnus (dup)
    244: [3],     # Night Stalker (dup)
    246: [5],     # Ogre Magi (dup)
    251: [1],     # Razor (dup)
    252: [4],     # Riki (dup)
    265: [3],     # Tidehunter (dup)
    271: [4],     # Tusk (dup)
    274: [5],     # Vengeful Spirit (dup)
    276: [5],     # Viper (dup)
    282: [1],     # Drow Ranger (dup)
}


def get_hero_positions(hero_id: int) -> list[int]:
    return HERO_POSITIONS.get(hero_id, [3])
