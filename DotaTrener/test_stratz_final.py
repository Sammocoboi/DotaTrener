# test_stratz_final.py
import os, sys, django, requests, json

# Минимальная инициализация для доступа к settings
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dotatrener.settings')

# Пробуем настроить Django, но если не выйдет — используем fallback
try:
    django.setup()
    from django.conf import settings
    API_KEY = settings.STRATZ_API_KEY
except:
    # Fallback: читаем из .env вручную
    import dotenv
    dotenv.load_dotenv()
    API_KEY = os.getenv('STRATZ_API_KEY')

url = "https://api.stratz.com/graphql"
headers = {
    "Content-Type": "application/json",
    "User-Agent": "STRATZ_API",
    "Authorization": f"Bearer {API_KEY}" if API_KEY else ""
}

print("🔍 Тест А: Inline fragment (... on HeroWinDayType)")
query_a = """
{
  heroStats {
    winDay(heroIds: [1]) {
      ... on HeroWinDayType {
        __typename
      }
    }
  }
}
"""
r = requests.post(url, json={"query": query_a}, headers=headers, timeout=15)
print(f"Status: {r.status_code}")
print(json.dumps(r.json(), indent=2)[:800])

print("\n" + "="*60)
print("🔍 Тест Б: Запрос без полей (только __typename) — смотрим структуру")
query_b = """
{
  heroStats {
    winDay(heroIds: [1])
  }
}
"""
r = requests.post(url, json={"query": query_b}, headers=headers, timeout=15)
print(f"Status: {r.status_code}")
print("Raw response:")
print(r.text[:1000])

print("\n" + "="*60)
print("🔍 Тест В: Пробуем универсальные 'скрытые' поля")
# Некоторые API используют специальные поля для доступа к данным
query_c = """
{
  heroStats {
    winDay(heroIds: [1]) {
      __typename
      _value
      _data
      result
      payload
      stats
      metric
      measure
    }
  }
}
"""
r = requests.post(url, json={"query": query_c}, headers=headers, timeout=15)
print(f"Status: {r.status_code}")
data = r.json()
if "errors" in data:
    print("❌ Ошибки:")
    for e in data["errors"]:
        print(f"   • {e.get('message', '')[:100]}")
else:
    print("✅ Успех! Данные:")
    print(json.dumps(data, indent=2)[:1000])