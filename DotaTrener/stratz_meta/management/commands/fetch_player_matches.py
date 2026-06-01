from django.core.management.base import BaseCommand
from stratz_meta.services import StratzClient


class Command(BaseCommand):
    help = "Показать историю матчей игрока из Stratz"

    def add_arguments(self, parser):
        parser.add_argument("steam_id", type=int, help="Steam Account ID игрока")
        parser.add_argument("--limit", type=int, default=10, help="Количество матчей")
        parser.add_argument("--patch", type=str, help="Фильтр по патчу (например 7.41c)")

    def handle(self, *args, **options):
        client = StratzClient()
        steam_id = options["steam_id"]
        limit = options["limit"]

        self.stdout.write(f"Fetching profile for {steam_id}...")
        profile = client.fetch_player_profile(steam_id)
        if profile:
            wins = profile.get("winCount") or 0
            losses = profile.get("loseCount") or 0
            wr = profile.get("winRate") or 0
            self.stdout.write(f"  Record: {wins}W / {losses}L ({wr:.1f}%)\n")

        game_version_id = None
        if options.get("patch"):
            game_version_id = client.resolve_game_version_id(options["patch"])
            if game_version_id is None:
                self.stdout.write(self.style.WARNING(f"Patch '{options['patch']}' not found, fetching all"))

        self.stdout.write(f"Fetching {limit} matches...")
        matches = client.fetch_player_matches(
            steam_id, take=limit, patch_id=game_version_id
        )

        if not matches:
            self.stdout.write(self.style.WARNING("No matches found"))
            return

        self.stdout.write(f"\n{'='*60}")

        for i, match in enumerate(matches):
            match_id = match.get("id", "?")
            radiant_won = match.get("didRadiantWin", False)
            duration_s = match.get("duration", 0)
            mins, secs = divmod(duration_s, 60)
            players = match.get("players", [])

            if players:
                p = players[0]
                hero_id = p.get("heroId", "?")
                is_radiant = p.get("isRadiant", False)
                won = p.get("win", False)
                result = "WIN" if won else "LOSS"
                result_color = self.style.SUCCESS if won else self.style.ERROR

                k = p.get("kills", 0)
                d = p.get("deaths", 0)
                a = p.get("assists", 0)
                gpm = p.get("goldPerMinute", 0)
                xpm = p.get("experiencePerMinute", 0)
                hd = p.get("heroDamage", 0)
                td = p.get("towerDamage", 0)
                lh = p.get("numLastHits", 0)
                dn = p.get("numDenies", 0)

                side = "Radiant" if is_radiant else "Dire"

                self.stdout.write(
                    result_color(
                        f"  [{i+1}] Match {match_id} | {result} ({side}) | "
                        f"{mins}:{secs:02d} | Hero {hero_id}"
                    )
                )
                self.stdout.write(
                    f"       {k}/{d}/{a} | GPM {gpm} | XPM {xpm} | "
                    f"DMG {hd} | TD {td} | LH/DN {lh}/{dn}"
                )

                items = [p.get(f"item{j}Id") for j in range(6)]
                item_names = [client.get_item_name(i) for i in items if i]
                if item_names:
                    self.stdout.write(f"       Items: {', '.join(item_names)}")

                abilities = p.get("abilityUpgrades") or []
                if abilities:
                    abil_ids = [str(a.get("abilityId", "?")) for a in abilities[:10]]
                    self.stdout.write(f"       Abilities: {' -> '.join(abil_ids)}")
            else:
                self.stdout.write(f"  [{i+1}] Match {match_id} | {mins}:{secs:02d}")

            self.stdout.write("")
