# stratz_meta/management/commands/test_stratz_api.py
import json
import requests
from django.core.management.base import BaseCommand
from django.conf import settings

STRATZ_GRAPHQL_URL = "https://api.stratz.com/graphql"
STRATZ_API_KEY = getattr(settings, "STRATZ_API_KEY", None)

HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "STRATZ_API",
    "Authorization": f"Bearer {STRATZ_API_KEY}" if STRATZ_API_KEY else "",
}

class Command(BaseCommand):
    help = "Тестовый запрос к Stratz GraphQL API для отладки"

    def add_arguments(self, parser):
        parser.add_argument('--query', type=str, default='simple',
                            choices=['simple', 'stats', 'full', 'discover'],
                            help="Тип запроса: simple, stats (heroStats), full, discover (интроспекция схемы)")
        parser.add_argument('--patch', type=str, default='7.41c', help="Версия патча")
        parser.add_argument('--field', type=str, default='heroStats', 
                            help="Имя корневого поля (heroStats, meta, heroes и т.д.)")
        parser.add_argument('--raw', action='store_true', help="Вывести полный сырой ответ")
        parser.add_argument('--limit', type=int, default=3, help="Лимит героев в запросе")

    def handle(self, *args, **kwargs):
        query_type = kwargs['query']
        patch_id = kwargs['patch']
        field_name = kwargs['field']
        show_raw = kwargs['raw']
        limit = kwargs['limit']

        self.stdout.write(f"🔌 Тест подключения к {STRATZ_GRAPHQL_URL}")
        self.stdout.write(f"🔑 API Key: {'✓ Указан' if STRATZ_API_KEY else '✗ Не указан'}")
        self.stdout.write(f"📦 Тип запроса: {query_type} | Поле: {field_name}")
        if query_type != 'simple':
            self.stdout.write(f"🔄 Патч: {patch_id} | Лимит: {limit}")
        self.stdout.write("-" * 60)

        # 🔥 Выбираем запрос
        if query_type == 'simple':
            query = "{ __schema { queryType { name } } }"
            variables = {}
        
        elif query_type == 'discover':
            # Интроспекция: покажет все доступные поля на корне
            query = """
            {
              __type(name: "DotaQuery") {
                name
                fields {
                  name
                  description
                  args {
                    name
                    type { name kind }
                  }
                  type { name kind }
                }
              }
            }
            """
            variables = {}
        
        elif query_type == 'stats':
            query = f"""
            query TestStats($patchId: String, $limit: Int) {{
              {field_name}(patchId: $patchId, limit: $limit) {{
                heroId
                pickRate
                winRate
                banRate
                games
              }}
            }}
            """
            variables = {"patchId": patch_id, "limit": limit}
        
        else:  # full
            query = f"""
            query TestFull($patchId: String, $limit: Int) {{
              {field_name}(patchId: $patchId, limit: $limit) {{
                heroId
                pickRate
                winRate
                banRate
                games
                roles
                itemBuilds(limit: $limit) {{
                  items
                  pickRate
                  winRate
                  games
                  role
                }}
                skillBuilds(limit: $limit) {{
                  skills
                  pickRate
                  winRate
                  games
                  role
                }}
              }}
            }}
            """
            variables = {"patchId": patch_id, "limit": limit}

        # Выполняем запрос
        payload = {"query": query.strip(), "variables": variables if variables else None}
        
        self.stdout.write(f"\n📤 Отправка запроса...")
        try:
            response = requests.post(
                STRATZ_GRAPHQL_URL,
                json=payload,
                headers=HEADERS,
                timeout=30
            )
        except requests.exceptions.RequestException as e:
            self.stderr.write(self.style.ERROR(f"❌ Ошибка сети: {e}"))
            return

        # Вывод базовой информации
        self.stdout.write(f"📥 Status Code: {response.status_code}")
        self.stdout.write(f"📥 Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        
        # Парсим ответ
        try:
            data = response.json()
        except json.JSONDecodeError:
            self.stderr.write(self.style.ERROR(f"❌ Не удалось распарсить JSON. Сырой ответ:"))
            self.stderr.write(response.text[:500])
            return

        # 👇 ПОКАЗЫВАЕМ ОШИБКИ GRAPHQL (исправлено: in data)
        if 'errors' in data:
            self.stderr.write(self.style.ERROR(f"\n❌ GraphQL Errors:"))
            for err in data['errors']:
                self.stderr.write(f"   • {err.get('message', 'No message')}")
                if err.get('locations'):
                    self.stderr.write(f"     Location: {err['locations']}")
                if err.get('path'):
                    self.stderr.write(f"     Path: {err['path']}")
                if 'suggestions' in err:
                    self.stdout.write(self.style.WARNING(f"   💡 Подсказка: {err['suggestions']}"))
        
        # 👇 ПОКАЗЫВАЕМ ДАННЫЕ (исправлено: in data)
        if 'data' in data:
            self.stdout.write(self.style.SUCCESS(f"\n✅ Данные получены:"))
            if query_type == 'simple':
                schema_name = data['data']['__schema']['queryType']['name']
                self.stdout.write(f"   Query type: {schema_name}")
            
            elif query_type == 'discover':
                fields = data['data']['__type']['fields'] or []
                self.stdout.write(f"   Доступные поля в DotaQuery ({len(fields)}):")
                hero_fields = [f for f in fields if any(k in f['name'].lower() for k in ['hero', 'meta', 'stat', 'pick', 'win'])]
                for f in hero_fields[:10]:
                    args = [a['name'] for a in (f.get('args') or [])]
                    self.stdout.write(f"   • {f['name']}(args: {args})")
            
            elif query_type in ['stats', 'full']:
                heroes = data['data'].get(field_name, [])
                if isinstance(heroes, list):
                    self.stdout.write(f"   Найдено героев: {len(heroes)}")
                    for h in heroes[:limit]:
                        wr = h.get('winRate', 'N/A')
                        pr = h.get('pickRate', 'N/A')
                        self.stdout.write(f"   • Hero ID {h.get('heroId')}: WR={wr}%, PR={pr}%")
                else:
                    self.stdout.write(f"   ⚠️ Ответ не является списком. Тип: {type(heroes)}")
                    if isinstance(heroes, dict):
                        self.stdout.write(f"   🔍 Первые ключи: {list(heroes.keys())[:5]}")
        
        # Сырой вывод для глубокой отладки
        if show_raw:
            self.stdout.write(f"\n🔍 RAW RESPONSE (first 1500 chars):")
            self.stdout.write(json.dumps(data, indent=2, ensure_ascii=False)[:1500])

        # 👇 ИТОГ (исправлено: not in data)
        self.stdout.write("\n" + "=" * 60)
        if response.status_code == 200 and 'errors' not in data:
            self.stdout.write(self.style.SUCCESS("✅ Тест ПРОЙДЕН. Запрос работает корректно."))
            if query_type in ['stats', 'full']:
                self.stdout.write(self.style.SUCCESS(f"💡 Используйте поле '{field_name}' в основном парсере."))
        elif response.status_code == 401:
            self.stderr.write(self.style.ERROR("❌ 401 Unauthorized: Проверьте STRATZ_API_KEY"))
        elif response.status_code == 400:
            self.stderr.write(self.style.ERROR("❌ 400 Bad Request: Проверьте имя поля и аргументы"))
        elif response.status_code == 404:
            self.stderr.write(self.style.ERROR("❌ 404 Not Found: Неверный URL эндпоинта"))
        elif response.status_code == 429:
            self.stderr.write(self.style.ERROR("❌ 429 Too Many Requests: Превышен лимит"))
        else:
            self.stderr.write(self.style.ERROR(f"❌ Неизвестная ошибка"))