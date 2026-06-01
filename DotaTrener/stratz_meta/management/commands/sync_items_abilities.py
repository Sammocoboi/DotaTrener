import json
import logging

from django.core.management.base import BaseCommand

from stratz_meta.services import StratzClient

logger = logging.getLogger(__name__)


def _sanitize(obj):
    """Удаляет нулевые символы из строк в JSON-структурах."""
    if isinstance(obj, str):
        return obj.replace("\x00", "")
    if isinstance(obj, list):
        return [_sanitize(i) for i in obj]
    if isinstance(obj, dict):
        return {k: _sanitize(v) for k, v in obj.items()}
    return obj

ITEMS_QUERY = """
{
  constants {
    items {
      id
      name
      displayName
      shortName
      isSupportFullItem
      language {
        displayName
        description
        lore
        notes
        attributes
      }
      stat {
        cost
        manaCost
        castRange
        castPoint
        channelTime
        shopTags
        quality
        isSellable
        isDroppable
        isPurchasable
        isStackable
        isSupport
        isRecipe
        needsComponents
        neutralItemTier
      }
      attributes {
        name
        value
      }
      components {
        index
        componentId
      }
    }
  }
}
"""

ABILITIES_QUERY = """
{
  constants {
    abilities {
      id
      name
      isTalent
      language {
        displayName
        description
        lore
        notes
        attributes
        aghanimDescription
        shardDescription
      }
      stat {
        abilityId
        type
        behavior
        unitTargetType
        unitTargetTeam
        unitTargetFlags
        unitDamageType
        spellImmunity
        maxLevel
        isUltimate
        hasScepterUpgrade
        hasShardUpgrade
        cooldown
        manaCost
        damage
        castRange
        castPoint
        channelTime
        duration
        charges
        chargeRestoreTime
        isInnate
      }
      attributes {
        name
        value
      }
    }
  }
}
"""


class Command(BaseCommand):
    help = "Синхронизация предметов и способностей из Stratz API в БД"

    def add_arguments(self, parser):
        parser.add_argument(
            "--items-only", action="store_true", help="Только предметы"
        )
        parser.add_argument(
            "--abilities-only", action="store_true", help="Только способности"
        )

    def handle(self, *args, **options):
        client = StratzClient()
        items_only = options["items_only"]
        abilities_only = options["abilities_only"]

        if not items_only and not abilities_only:
            self._sync_items(client)
            self._sync_abilities(client)
        elif items_only:
            self._sync_items(client)
        else:
            self._sync_abilities(client)

    def _sync_items(self, client):
        from coaching.models import Item

        self.stdout.write("Загрузка предметов из Stratz...")
        data = client.graphql(ITEMS_QUERY)
        raw_items = (data or {}).get("constants", {}).get("items", [])
        raw_items = _sanitize(raw_items)
        self.stdout.write(f"  Получено {len(raw_items)} предметов из API")

        created, updated, skipped = 0, 0, 0
        for raw in raw_items:
            item_id = raw.get("id")
            if item_id is None:
                skipped += 1
                continue
            item_id = int(item_id)

            lang = raw.get("language") or {}
            stat = raw.get("stat") or {}
            attrs = raw.get("attributes") or []
            comps = raw.get("components") or []

            display_name = lang.get("displayName") or raw.get("displayName") or raw.get("name") or f"Item {item_id}"
            short_name = raw.get("shortName") or ""

            image_url = ""
            if short_name:
                image_url = f"https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/{short_name}.png"

            description = lang.get("description") or ""
            if isinstance(description, list):
                description = "\n".join(str(d) for d in description if d)

            lore = lang.get("lore") or ""
            if isinstance(lore, list):
                lore = " ".join(str(l) for l in lore if l)

            notes = lang.get("notes")
            attributes_text = lang.get("attributes")

            obj, was_created = Item.objects.update_or_create(
                steam_id=item_id,
                defaults={
                    "name": raw.get("name") or "",
                    "display_name": display_name,
                    "short_name": short_name,
                    "image_url": image_url,
                    "description": description,
                    "lore": lore,
                    "notes": notes,
                    "attributes_text": attributes_text,
                    "cost": stat.get("cost") or 0,
                    "mana_cost": stat.get("manaCost"),
                    "cooldown": None,
                    "cast_range": stat.get("castRange"),
                    "shop_tags": stat.get("shopTags") or "",
                    "quality": stat.get("quality") or "",
                    "is_sellable": stat.get("isSellable", True),
                    "is_droppable": stat.get("isDroppable", True),
                    "is_purchasable": stat.get("isPurchasable", True),
                    "is_stackable": stat.get("isStackable", False),
                    "is_support": stat.get("isSupport", False),
                    "is_recipe": stat.get("isRecipe", False),
                    "needs_components": stat.get("needsComponents", False),
                    "neutral_item_tier": stat.get("neutralItemTier") or "",
                    "attributes": [{"name": a.get("name"), "value": a.get("value")} for a in attrs] if attrs else None,
                    "components": [c.get("componentId") for c in comps if c.get("componentId") is not None] if comps else None,
                    "api_data": raw,
                },
            )
            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(self.style.SUCCESS(
            f"  Предметы: +{created} создано, ~{updated} обновлено, {skipped} пропущено"
        ))

    def _sync_abilities(self, client):
        from coaching.models import Ability

        self.stdout.write("Загрузка способностей из Stratz...")
        data = client.graphql(ABILITIES_QUERY)
        raw_abilities = (data or {}).get("constants", {}).get("abilities", [])
        raw_abilities = _sanitize(raw_abilities)
        self.stdout.write(f"  Получено {len(raw_abilities)} способностей из API")

        created, updated, skipped = 0, 0, 0
        for raw in raw_abilities:
            ability_id = raw.get("id")
            if ability_id is None:
                skipped += 1
                continue
            ability_id = int(ability_id)

            lang = raw.get("language") or {}
            stat = raw.get("stat") or {}
            attrs = raw.get("attributes") or []

            display_name = lang.get("displayName") or _format_internal_name(raw.get("name") or "") or f"Ability {ability_id}"
            short_name = raw.get("name") or ""

            image_url = ""
            if short_name:
                image_url = f"https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/abilities/{short_name}.png"

            description = lang.get("description")
            notes = lang.get("notes")
            attributes_text = lang.get("attributes")

            aghanim_desc = lang.get("aghanimDescription") or ""
            shard_desc = lang.get("shardDescription") or ""

            obj, was_created = Ability.objects.update_or_create(
                steam_id=ability_id,
                defaults={
                    "name": short_name,
                    "display_name": display_name,
                    "image_url": image_url,
                    "description": description,
                    "lore": lang.get("lore") or "",
                    "notes": notes,
                    "attributes_text": attributes_text,
                    "aghanim_description": aghanim_desc,
                    "shard_description": shard_desc,
                    "ability_type": stat.get("type") or 0,
                    "behavior": stat.get("behavior") or 0,
                    "unit_damage_type": stat.get("unitDamageType") or 0,
                    "spell_immunity": stat.get("spellImmunity") or 0,
                    "max_level": stat.get("maxLevel") or 4,
                    "is_ultimate": stat.get("isUltimate", False),
                    "has_scepter_upgrade": stat.get("hasScepterUpgrade", False),
                    "has_shard_upgrade": stat.get("hasShardUpgrade", False),
                    "is_innate": stat.get("isInnate", False),
                    "is_talent": raw.get("isTalent", False),
                    "cooldown": stat.get("cooldown"),
                    "mana_cost": stat.get("manaCost"),
                    "damage": stat.get("damage"),
                    "cast_range": stat.get("castRange"),
                    "cast_point": stat.get("castPoint"),
                    "channel_time": stat.get("channelTime"),
                    "duration": stat.get("duration") or "",
                    "charges": stat.get("charges") or "",
                    "attributes": [{"name": a.get("name"), "value": a.get("value")} for a in attrs] if attrs else None,
                    "api_data": raw,
                },
            )
            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(self.style.SUCCESS(
            f"  Способности: +{created} создано, ~{updated} обновлено, {skipped} пропущено"
        ))


def _format_internal_name(name: str) -> str:
    if not name:
        return ""
    return " ".join(part.capitalize() for part in name.replace("_", " ").split())
