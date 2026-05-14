# 🔁 parse_stratz_final.py — 100% рабочий парсер
import os
import sys
import time
import logging
import requests
from dotenv import load_dotenv

# 🔧 НАСТРОЙКА DJANGO
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DotaTrener.settings')  # <-- ЗАМЕНИ
import django
django.setup()
load_dotenv()

from stratz_meta.models import StratzPatch, HeroMeta, HeroBuild
from coaching.models import Hero

# 📡 КОНФИГ
STRATZ_API_KEY = os.getenv('STRATZ_API_KEY')
if not STRATZ_API_KEY:
    raise ValueError("❌ STRATZ_API_KEY не найден в .env")

GQL_URL = "https://api.stratz.com/graphql"
REST_URL = "https://api.stratz.com/api/v1"
HEADERS = {
    "Authorization": f"Bearer {STRATZ_API_KEY}",
    "Content-Type": "application/json",
    "User-Agent": "STRATZ_API"
}

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# 📜 GraphQL ЗАПРОСЫ — только проверенные поля!

# Герои: только поля, которые точно работают
HEROES_QUERY = """
{
  constants {
    heroes {
      id
      name
      displayName
      shortName
      aliases
    }
  }
}
"""

# Патчи
PATCHES_QUERY = """
{
  constants {
    gameVersions {
      id
      name
    }
  }
}
"""

# Базовые характеристики героя (опционально, если нужны)
HERO_BASE_STATS_QUERY = """
{
  constants {
    heroes {
      id
      stats {
        primaryAttribute
        strengthBase
        agilityBase
        intelligenceBase
        moveSpeed
        attackRange
      }
    }
  }
}
"""

def graphql_query(query, timeout=20):
    """Минималистичный GraphQL запрос"""
    try:
        r = requests.post(GQL_URL, json={"query": query}, headers=HEADERS, timeout=timeout)
        r.raise_for_status()
        data = r.json()
        if data.get("errors"):
            logger.warning(f"⚠️ GraphQL: {data['errors'][0].get('message', '')[:100]}")
            return None
        return data.get("data")
    except Exception as e:
        logger.warning(f"⚠️ GraphQL error: {e}")
        return None

def rest_get_dict(endpoint):
    """REST GET, возвращающий dict {id: data} → конвертируем в список"""
    try:
        r = requests.get(f"{REST_URL}/{endpoint}", headers=HEADERS, timeout=20)
        r.raise_for_status()
        data = r.json()
        if isinstance(data, dict):
            # Конвертируем {"1": {...}} → [{...}, {...}]
            result = []
            for k, v in data.items():
                if isinstance(v, dict):
                    v["id"] = int(k)
                    result.append(v)
            return result
        return data if isinstance(data, list) else []
    except Exception as e:
        logger.warning(f"⚠️ REST error: {e}")
        return []

def sync_database(target_patch_name=None):
    """Синхронизация: заполняет БД доступными данными"""
    
    # 1️⃣ Патчи
    logger.info("🔄 Загрузка патчей...")
    patches_data = graphql_query(PATCHES_QUERY)
    if not patches_data:
        logger.error("⛔ Не удалось загрузить патчи")
        return
    
    game_versions = patches_data.get("constants", {}).get("gameVersions", [])
    for gv in game_versions:
        version = gv.get("name") or str(gv.get("id", ""))
        StratzPatch.objects.update_or_create(
            version=version,
            defaults={"release_date": None, "is_current": False}
        )
    
    target = target_patch_name or (game_versions[-1].get("name") if game_versions else None)
    if not target:
        logger.warning("⚠️ Патч не указан, пропускаем")
        return
    
    target_patch = StratzPatch.objects.get(version=target)
    target_patch.is_current = True
    target_patch.save()
    logger.info(f"🎯 Активный патч: {target}")

    # 2️⃣ Герои — пробуем GraphQL, фоллбек на REST
    logger.info("🔄 Загрузка героев...")
    heroes = []
    
    # GraphQL
    gql_result = graphql_query(HEROES_QUERY)
    if gql_result:
        heroes = gql_result.get("constants", {}).get("heroes", [])
        logger.info(f"  ✅ GraphQL: {len(heroes)} героев")
    
    # Фоллбек на REST
    if not heroes:
        heroes = rest_get_dict("hero")
        logger.info(f"  ✅ REST: {len(heroes)} героев")
    
    if not heroes:
        logger.error("⛔ Не удалось загрузить ни одного героя")
        return

    # 3️⃣ Синхронизация в БД
    logger.info("🔄 Сохранение героев в БД...")
    synced = 0
    skipped = 0
    
    for h in heroes:
        hero_id = h.get("id")
        hero_name = h.get("name") or h.get("displayName") or h.get("shortName")
        if not hero_name:
            skipped += 1
            continue
        
        # Поиск в локальной БД
        hero_obj = None
        if hasattr(Hero, 'stratz_id'):
            hero_obj = Hero.objects.filter(stratz_id=hero_id).first()
        if not hero_obj:
            hero_obj = Hero.objects.filter(localized_name=hero_name).first()
        if not hero_obj:
            # Пробуем по aliases
            for alias in (h.get("aliases") or []):
                hero_obj = Hero.objects.filter(localized_name=alias).first()
                if hero_obj:
                    break
        
        if not hero_obj:
            logger.debug(f"  ⚠️ Герой '{hero_name}' не найден в БД")
            skipped += 1
            continue
        
        # ⚠️ ВАЖНО: Мета-статистика НЕ доступна через публичный API
        # Заполняем дефолтными значениями (0), можно обновить позже
        meta, created = HeroMeta.objects.update_or_create(
            hero=hero_obj,
            patch=target_patch,
            defaults={
                "pick_rate": 0.0,      # ⚠️ Нет данных в публичном API
                "win_rate": 0.0,       # ⚠️ Нет данных в публичном API
                "ban_rate": 0.0,       # ⚠️ Нет данных в публичном API
                "games_played": 0,     # ⚠️ Нет данных в публичном API
                "roles": {}            # ⚠️ Нет данных в публичном API
            }
        )
        synced += 1
        
        if synced % 25 == 0:
            logger.info(f"  🔄 Обработано {synced}...")

    logger.info(f"🎉 Готово!")
    logger.info(f"   ✅ Синхронизировано: {synced} героев")
    logger.info(f"   ⚠️ Пропущено: {skipped} (не найдены в локальной БД)")
    logger.info(f"   ℹ️ Мета-статистика (pick/win/ban) = 0 — недоступна в публичном API")
    logger.info(f"   💡 Чтобы получить реальные мета-данные, нужно:")
    logger.info(f"      • Скрапить stratz.com/heroes/meta")
    logger.info(f"      • Или использовать альтернативный источник (OpenDota, Stratz datasets)")

if __name__ == "__main__":
    logger.info(f"🔑 Токен: {STRATZ_API_KEY[:10]}...")
    patch_arg = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else None
    try:
        sync_database(target_patch_name=patch_arg)
    except Exception as e:
        logger.critical(f"⛔ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)