#!/usr/bin/env python3
"""Выводит СЫРЫЕ ответы API для анализа структуры"""
import os, requests, json
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('STRATZ_API_KEY')
GQL_URL = "https://api.stratz.com/graphql"
REST_URL = "https://api.stratz.com/api/v1"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
    "User-Agent": "STRATZ_API"
}

def print_section(title):
    print(f"\n{'='*70}\n{title}\n{'='*70}")

# 1️⃣ GraphQL: минимальный запрос к heroes
print_section("1️⃣ GraphQL: constants { heroes { id } }")
r1 = requests.post(GQL_URL, json={"query": "{ constants { heroes { id } } }"}, headers=HEADERS)
print(f"Status: {r1.status_code}")
if r1.status_code == 200:
    data = r1.json()
    heroes = data.get("data", {}).get("constants", {}).get("heroes", [])
    print(f"Тип ответа: {type(heroes)}")
    print(f"Количество: {len(heroes) if isinstance(heroes, (list, tuple)) else 'N/A'}")
    if isinstance(heroes, list) and heroes:
        print(f"Пример элемента: {json.dumps(heroes[0], indent=2)}")

# 2️⃣ GraphQL: пробуем добавить ОДНО поле за раз
print_section("2️⃣ GraphQL: пробуем поля по одному")
fields_to_test = ["name", "displayName", "primaryAttr", "stats"]
base_hero = "{ constants { heroes { id FIELD } } }"

for field in fields_to_test:
    query = base_hero.replace("FIELD", field)
    r = requests.post(GQL_URL, json={"query": query}, headers=HEADERS)
    status = "✅" if r.status_code == 200 and not r.json().get("errors") else "❌"
    error_msg = ""
    if r.status_code != 200 or r.json().get("errors"):
        error_msg = r.json().get("errors", [{}])[0].get("message", "")[:80]
    print(f"  {status} {field:15} {error_msg}")

# 3️⃣ GraphQL: интроспекция HeroStatType (что внутри stats?)
print_section("3️⃣ GraphQL: поля HeroStatType")
intro = requests.post(GQL_URL, json={
    "query": '{ __type(name: "HeroStatType") { fields { name type { name ofType { name } } } } }'
}, headers=HEADERS)
if intro.status_code == 200 and not intro.json().get("errors"):
    fields = intro.json()["data"]["__type"]["fields"]
    for f in fields:
        print(f"  • {f['name']}: {f['type']}")
else:
    print("  ❌ Не удалось получить интроспекцию")

# 4️⃣ REST: /hero — сырой ответ
print_section("4️⃣ REST: GET /hero (сырой ответ)")
r4 = requests.get(f"{REST_URL}/hero", headers=HEADERS)
print(f"Status: {r4.status_code}")
if r4.status_code == 200:
    data = r4.json()
    print(f"Тип корневого объекта: {type(data)}")
    if isinstance(data, dict):
        print(f"Ключи: {list(data.keys())[:10]}")
        # Если это словарь с героями по ключам
        sample_key = next(iter(data.keys()), None)
        if sample_key:
            print(f"Пример по ключу '{sample_key}': {json.dumps(data[sample_key], indent=2)[:500]}")
    elif isinstance(data, list):
        print(f"Это список из {len(data)} элементов")
        if data:
            print(f"Пример элемента: {json.dumps(data[0], indent=2)[:500]}")

# 5️⃣ REST: /hero/stats — сырой ответ
print_section("5️⃣ REST: GET /hero/stats (сырой ответ)")
r5 = requests.get(f"{REST_URL}/hero/stats", headers=HEADERS)
print(f"Status: {r5.status_code}")
if r5.status_code == 200:
    data = r5.json()
    print(f"Тип корневого объекта: {type(data)}")
    if isinstance(data, dict):
        print(f"Ключи: {list(data.keys())[:10]}")
        sample_key = next(iter(data.keys()), None)
        if sample_key and isinstance(data[sample_key], dict):
            print(f"Пример значения: {json.dumps(data[sample_key], indent=2)[:500]}")
    elif isinstance(data, list):
        print(f"Это список из {len(data)} элементов")
        if data:
            print(f"Пример: {json.dumps(data[0], indent=2)[:500]}")
else:
    print(f"❌ Ошибка: {r5.text[:300]}")

print_section("🎯 ИНСТРУКЦИЯ")
print("Скопируй вывод выше и отправь мне — я напишу 100% рабочий парсер")
print("ИЛИ посмотри сам:")
print("  • Если REST /hero возвращает {'1': {...}, '2': {...}} — это словарь по ID")
print("  • Если GraphQL stats не принимает pickRate — возможно поле называется иначе")