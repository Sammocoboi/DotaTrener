# debug_stratz_schema.py
"""
Парсер Stratz Meta для DotaTrener
Исправлен поиск героев: умный кэш + фоллбэк в БД + обработка префиксов
"""

import os
import time
import logging
from datetime import date
from typing import Optional, List, Dict, Any

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("stratz_parser.log", encoding="utf-8", mode="a"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# =============================================================================
# НАСТРОЙКИ
# =============================================================================
API_TOKEN = os.getenv("STRATZ_API_KEY")
if not API_TOKEN:
    raise ValueError("❌ Не найден STRATZ_API_KEY в .env")

BASE_URL = os.getenv("STRATZ_API_URL", "https://api.stratz.com/graphql")
CURRENT_PATCH = os.getenv("STRATZ_PATCH_VERSION", "7.38")
REQUEST_DELAY = float(os.getenv("STRATZ_REQUEST_DELAY", "0.4"))

import cloudscraper
scraper = cloudscraper.create_scraper(browser={"browser": "chrome", "platform": "windows", "desktop": True})

# =============================================================================
# DJANGO INIT
# =============================================================================
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DotaTrener.settings")
import django
django.setup()

from stratz_meta.models import StratzPatch, HeroMeta, HeroBuild
from coaching.models import Hero

# =============================================================================
# КЭШ ГЕРОЕВ (УМНЫЙ ПОИСК)
# =============================================================================
HERO_DB_CACHE = {}

def load_hero_cache():
    """Создаёт словарь всех вариаций имени героя для быстрого поиска"""
    global HERO_DB_CACHE
    HERO_DB_CACHE = {}
    
    for h in Hero.objects.iterator():
        keys = set()
        
        # Обработка поля name
        if h.name:
            n = h.name.strip().lower()
            keys.add(n)
            # Убираем npc_dota_hero_ и меняем _ на - или пробел
            if n.startswith("npc_dota_hero_"):
                clean = n.replace("npc_dota_hero_", "")
                keys.add(clean.replace("_", "-"))
                keys.add(clean.replace("_", " "))
                keys.add(clean)  # просто antimage
                
        # Обработка localized_name
        if h.localized_name:
            ln = h.localized_name.strip().lower()
            keys.add(ln)
            keys.add(ln.replace("-", " "))
            
        for k in keys:
            if k:
                HERO_DB_CACHE[k] = h
                
    logger.info(f"📂 Кэш героев: {len(HERO_DB_CACHE)} ключей")
    if HERO_DB_CACHE:
        logger.debug(f"Примеры ключей кэша: {list(HERO_DB_CACHE.keys())[:3]}")


def get_hero_from_db(api_hero: Dict) -> Optional[Hero]:
    """Ищет героя в кэше, при неудаче -> запрос в БД"""
    if not HERO_DB_CACHE:
        load_hero_cache()
        
    api_name = (api_hero.get("name") or "").strip().lower()
    api_display = (api_hero.get("displayName") or "").strip().lower()
    
    # 1. Прямое совпадение в кэше
    hero = HERO_DB_CACHE.get(api_name) or HERO_DB_CACHE.get(api_display)
    
    # 2. Очистка префикса API имени и повторный поиск
    if not hero and api_name.startswith("npc_dota_hero_"):
        clean_api = api_name.replace("npc_dota_hero_", "").replace("_", "-")
        hero = HERO_DB_CACHE.get(clean_api) or HERO_DB_CACHE.get(clean_api.replace("-", " "))
        
    # 3. Фоллбэк: запрос в БД (медленнее, но надёжно)
    if not hero:
        hero = Hero.objects.filter(localized_name__iexact=api_display).first()
        if not hero:
            hero = Hero.objects.filter(name__iexact=api_name).first()
        # Последний шанс: поиск по вхождению
        if not hero and len(api_display) > 3:
            hero = Hero.objects.filter(localized_name__icontains=api_display).first()
            
    return hero


# =============================================================================
# API ФУНКЦИИ
# =============================================================================

def make_request(query: str, retries: int = 3) -> Optional[Dict]:
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "STRATZ_API/1.0"
    }
    for _ in range(retries):
        try:
            resp = scraper.post(BASE_URL, json={"query": query.strip()}, headers=headers, timeout=30)
            if resp.status_code == 429:
                time.sleep(int(resp.headers.get("Retry-After", 2)))
                continue
            if resp.status_code == 200:
                data = resp.json()
                if "errors" in data:
                    logger.warning(f"⚠️ GraphQL: {data['errors'][0]['message']}")
                    return None
                return data.get("data")
            logger.error(f"❌ HTTP {resp.status_code}: {resp.text[:200]}")
            return None
        except Exception as e:
            logger.error(f"⚠️ Request: {e}")
            time.sleep(1)
    return None


def get_current_patch() -> Dict[str, Any]:
    logger.info(f"📦 Используем патч: {CURRENT_PATCH} (fallback)")
    return {"version": CURRENT_PATCH, "release_date": date.today().isoformat(), "is_current": True}


def get_all_heroes() -> List[Dict[str, Any]]:
    query = "{ constants { heroes { id name displayName } } }"
    data = make_request(query)
    if data and data.get("constants", {}).get("heroes"):
        return data["constants"]["heroes"]
    logger.error("❌ Не удалось получить героев")
    return []


def fetch_hero_meta(hero_id: int, patch_id: Optional[str] = None, rank: Optional[str] = None) -> Optional[Dict]:
    bracket = f', bracketBasicIds: [{rank}]' if rank else ""
    patch = f', patchId: "{patch_id}"' if patch_id else ""
    query = f"""{{ heroStats {{ overview(heroId: {hero_id}{patch}{bracket}) {{ pickDay winDay banDay gamesPlayed roles {{ role percentage }} }} }} }}"""
    data = make_request(query)
    if data and data.get("heroStats", {}).get("overview"):
        o = data["heroStats"]["overview"]
        roles = {r["role"]: round(r["percentage"], 2) for r in o.get("roles", []) if r.get("role")}
        return {
            "pick_rate": round(o.get("pickDay") or 0.0, 2),
            "win_rate": round(o.get("winDay") or 0.0, 2),
            "ban_rate": round(o.get("banDay") or 0.0, 2),
            "games_played": o.get("gamesPlayed") or 0,
            "roles": roles
        }
    return None


def fetch_hero_builds(hero_id: int, build_type: str, patch_id: Optional[str] = None, rank: Optional[str] = None, limit: int = 4) -> List[Dict]:
    bracket = f', bracketBasicIds: [{rank}]' if rank else ""
    patch = f', patchId: "{patch_id}"' if patch_id else ""
    type_val = "ITEM" if build_type == "item" else "ABILITY"
    seq_field = "items { id name }" if build_type == "item" else "abilities { id name abbrev }"
    res_field = "itemBuilds" if build_type == "item" else "abilityBuilds"
    
    query = f"""{{ heroStats {{ builds(heroId: {hero_id}, type: {type_val}, take: {limit}{patch}{bracket}) {{ {res_field} {{ sequence {{ {seq_field} }} pickDay winDay gamesPlayed role }} }} }} }}"""
    data = make_request(query)
    builds = []
    if data and data.get("heroStats", {}).get("builds", {}).get(res_field):
        for b in data["heroStats"]["builds"][res_field]:
            seq = [{"id": i["id"], "name": i.get("name")} for i in b.get("sequence", []) if i.get("id")] if build_type == "item" else [{"id": a.get("id"), "name": a.get("abbrev") or a.get("name")} for a in b.get("sequence", []) if a]
            builds.append({
                "build_type": build_type,
                "sequence": seq,
                "pick_rate": round((b.get("pickDay") or 0.0), 2),
                "win_rate": round((b.get("winDay") or 0.0), 2),
                "games": b.get("gamesPlayed") or 0,
                "role": b.get("role") or ""
            })
    return builds


# =============================================================================
# БД ФУНКЦИИ
# =============================================================================

def save_to_db(meta_data: Dict, hero_obj: Hero, patch_obj: StratzPatch, builds_data: List[Dict]) -> int:
    meta, _ = HeroMeta.objects.update_or_create(
        hero=hero_obj, patch=patch_obj,
        defaults={
            "pick_rate": meta_data["pick_rate"],
            "win_rate": meta_data["win_rate"],
            "ban_rate": meta_data["ban_rate"],
            "games_played": meta_data["games_played"],
            "roles": meta_data.get("roles", {})
        }
    )
    HeroBuild.objects.filter(hero_meta=meta).delete()
    if builds_data:
        objs = [HeroBuild(
            hero_meta=meta, build_type=b["build_type"], sequence=b["sequence"],
            pick_rate=b["pick_rate"], win_rate=b["win_rate"], games=b["games"],
            role=b["role"] or None
        ) for b in builds_data]
        HeroBuild.objects.bulk_create(objs)
    return len(builds_data)


# =============================================================================
# MAIN
# =============================================================================

def main(limit_heroes: Optional[int] = 10, test_mode: bool = True, hero_ids: Optional[List[int]] = None, ranks: Optional[List[str]] = None):
    logger.info("🚀 Запуск Stratz Parser")
    
    # 1. Патч
    patch_info = get_current_patch()
    StratzPatch.objects.filter(is_current=True).update(is_current=False)
    patch_obj, _ = StratzPatch.objects.update_or_create(
        version=patch_info["version"],
        defaults={"release_date": patch_info["release_date"], "is_current": True}
    )
    logger.info(f"✅ Патч: {patch_obj.version}")

    # 2. Кэш героев
    load_hero_cache()

    # 3. Герои из API
    heroes = get_all_heroes()
    if not heroes:
        return

    if hero_ids:
        heroes = [h for h in heroes if h["id"] in hero_ids]
    elif test_mode or limit_heroes:
        heroes = heroes[:limit_heroes]
        logger.info(f"🧪 Тест: первые {len(heroes)} героев")

    target_ranks = ranks or ["DIVINE_IMMORTAL"]
    stats = {"total": len(heroes), "success": 0, "failed": 0, "builds": 0}
    t0 = time.time()

    for i, h in enumerate(heroes, 1):
        name = h.get("displayName") or h.get("name")
        logger.info(f"[{i}/{stats['total']}] 🦸 {name} (ID:{h['id']})")

        hero_obj = get_hero_from_db(h)
        if not hero_obj:
            logger.warning(f"  ⚠️ Герой не найден в БД (API: name='{h.get('name')}', display='{h.get('displayName')}')")
            stats["failed"] += 1
            time.sleep(REQUEST_DELAY)
            continue

        meta = fetch_hero_meta(h["id"], patch_id=patch_obj.version, rank=target_ranks[0])
        if not meta:
            logger.warning("  ⚠️ Нет мета-данных от API")
            stats["failed"] += 1
            time.sleep(REQUEST_DELAY)
            continue

        builds = []
        for bt in ["item", "skill"]:
            builds.extend(fetch_hero_builds(h["id"], bt, patch_id=patch_obj.version, limit=4))

        try:
            cnt = save_to_db(meta, hero_obj, patch_obj, builds)
            stats["success"] += 1
            stats["builds"] += cnt
            logger.info(f"  ✅ WR:{meta['win_rate']}% | Games:{meta['games_played']} | Builds:{cnt}")
        except Exception as e:
            logger.error(f"  ❌ Ошибка сохранения: {e}")
            stats["failed"] += 1

        if i < stats["total"]:
            time.sleep(REQUEST_DELAY)

    logger.info(f"\n🎉 Готово! Успешно: {stats['success']}/{stats['total']} | Сборки: {stats['builds']} | Время: {time.time()-t0:.1f}с")
    
    if stats['success'] == 0 and stats['failed'] > 0:
        logger.warning("💡 Совет: проверьте, как записаны имена героев в БД:")
        logger.warning("   python manage.py shell")
        logger.warning("   >>> from coaching.models import Hero")
        logger.warning("   >>> print(Hero.objects.values('name', 'localized_name')[:2])")
        
    return stats


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=10)
    ap.add_argument("--test", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()

    main(
        limit_heroes=None if args.full else args.limit,
        test_mode=args.test or not args.full
    )