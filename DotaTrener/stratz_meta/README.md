# Stratz meta sync

Данные загружаются командой `python manage.py sync_stratz_meta` из [Stratz GraphQL API](https://api.stratz.com/graphql).

## Ранг по умолчанию: Divine / Immortal (`DIVINE_IMMORTAL`)

По умолчанию `--rank DIVINE_IMMORTAL` — статистика высокого рейтинга (как фильтр «Божество» на stratz.com), не весь пул игроков.

### Что фильтруется этим рангом

| Таблица / поля | Stratz-запрос | Фильтр |
|----------------|---------------|--------|
| `HeroMeta`: win_rate, pick_rate, games_played, roles | `winGameVersion`, `stats`, `statsTotals` | `bracketBasicIds: [DIVINE_IMMORTAL]`; win — `bracketIds: [DIVINE]` |
| `HeroMeta`: avg_kills, avg_deaths, avg_assists, avg_gpm, avg_xpm, avg_last_hits, avg_kda, … | `statsTotals` | `DIVINE_IMMORTAL` |
| `HeroBuild`: предметы и раскачка | `itemFullPurchase`, `itemBootPurchase`, `abilityMaxLevel`, `abilityMinLevel` | `bracketBasicIds` (тот же `--rank`) |

### Исключения

- **ban_rate** — `banDay(heroId)` без брекета по рангу.
- **avg_gpm / avg_xpm** — если Stratz не отдаёт `goldPerMinute`, GPM оценивается как `networth / STRATZ_AVG_MATCH_MINUTES` (по умолчанию 35 мин) из тех же Divine/Immortal матчей.

## Другой ранг

```powershell
python manage.py sync_stratz_meta --rank ALL
python manage.py sync_stratz_meta --rank LEGEND_ANCIENT
python manage.py sync_stratz_meta --skip-builds   # только HeroMeta, без билдов
```

Допустимые значения: `DIVINE_IMMORTAL`, `ALL`, `LEGEND_ANCIENT`, `CRUSADER_ARCHON`, `HERALD_GUARDIAN`, `UNCALIBRATED`, `FILTERED`.

## Переменные окружения

- `STRATZ_API_KEY` — обязателен
- `STRATZ_AVG_MATCH_MINUTES` — для оценки GPM/XPM (default `35`)
