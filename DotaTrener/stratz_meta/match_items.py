"""Финальный инвентарь (6 слотов) из матча и эталон endgame из меты."""
from __future__ import annotations

from typing import Any, Callable, Dict, List, Sequence

FINAL_ITEM_FIELDS = tuple(f"item{i}Id" for i in range(6))
ENDGAME_ROLE = "endgame"
MAX_FINAL_ITEMS = 6
# Покупки с time >= этого перцентиля считаем «поздней игрой»
LATE_GAME_TIME_PERCENTILE = 0.75
MIN_ENDGAME_ITEMS = 3


def extract_final_items(
    player: Dict[str, Any],
    get_item_name: Callable[[int], str],
) -> List[Dict[str, Any]]:
    """6 слотов инвентаря в конце матча (item0Id … item5Id). Пустые id пропускаются."""
    items: List[Dict[str, Any]] = []
    for slot, field in enumerate(FINAL_ITEM_FIELDS):
        raw = player.get(field)
        if raw is None:
            continue
        item_id = int(raw)
        if item_id <= 0:
            continue
        items.append(
            {
                "slot": slot,
                "id": item_id,
                "name": get_item_name(item_id),
            }
        )
    return items


def format_purchase_time(minutes: int | None) -> str:
    """Минуты Stratz → M:ss (минута матча)."""
    if minutes is None:
        return "—"
    m = int(minutes)
    return f"{m}:00"


def typical_purchase_time(
    rows: Sequence[Dict[str, Any]],
    item_id: int,
) -> int | None:
    """Типичная минута покупки: запись с макс. matchCount для этого itemId."""
    timed = [
        r
        for r in rows
        if int(r.get("itemId") or 0) == item_id and r.get("time") is not None
    ]
    if timed:
        best = max(timed, key=lambda r: int(r.get("matchCount") or 0))
        return int(best.get("time") or 0)
    return None


def build_endgame_sequence_from_purchase_rows(
    rows: Sequence[Dict[str, Any]],
    get_item_name: Callable[[int], str],
    *,
    limit: int = MAX_FINAL_ITEMS,
) -> List[Dict[str, Any]]:
    """
    Полная сборка на 6 слотов: сапоги + ранняя игра + поздняя + тайминги.

    - itemBootPurchase (без time) → слот 0, топ ботинок
    - itemFullPurchase ранняя (нижние ~50% time) → до 2 предметов
    - itemFullPurchase поздняя (верхние 25% time) → до 3 предметов
    - остальное добираем по matchCount из всех покупок
    """
    boot_rows = [
        r for r in rows if r.get("itemId") is not None and r.get("time") is None
    ]
    timed_rows = [
        r for r in rows if r.get("itemId") is not None and r.get("time") is not None
    ]

    sequence: List[Dict[str, Any]] = []
    seen: set[int] = set()

    def append_item(item_id: int) -> None:
        if item_id <= 0 or item_id in seen or len(sequence) >= limit:
            return
        seen.add(item_id)
        sequence.append(
            {
                "id": item_id,
                "name": get_item_name(item_id),
                "time": typical_purchase_time(rows, item_id),
            }
        )

    def append_top(rows_slice: Sequence[Dict[str, Any]], count: int) -> None:
        added = 0
        for item_id, _mc in sorted(
            _aggregate_match_counts(rows_slice).items(),
            key=lambda x: x[1],
            reverse=True,
        ):
            if added >= count or len(sequence) >= limit:
                break
            before = len(sequence)
            append_item(item_id)
            if len(sequence) > before:
                added += 1

    # Слот 0: сапоги
    if boot_rows:
        best_boot = max(boot_rows, key=lambda r: int(r.get("matchCount") or 0))
        append_item(int(best_boot["itemId"]))

    if timed_rows:
        times = sorted({int(r.get("time") or 0) for r in timed_rows})
        early_cutoff = times[min(len(times) // 2, len(times) - 1)]
        late_idx = max(0, int(len(times) * LATE_GAME_TIME_PERCENTILE) - 1)
        late_cutoff = times[late_idx]

        early_rows = [r for r in timed_rows if int(r.get("time") or 0) <= early_cutoff]
        late_rows = [r for r in timed_rows if int(r.get("time") or 0) >= late_cutoff]

        if not boot_rows and early_rows:
            best_early = max(early_rows, key=lambda r: int(r.get("matchCount") or 0))
            append_item(int(best_early["itemId"]))

        append_top(early_rows, count=2)
        append_top(late_rows, count=3)

    remaining = limit - len(sequence)
    if remaining > 0:
        append_top(rows, count=remaining)

    sequence.sort(key=lambda x: x.get("time") or 0)
    return sequence[:limit]


def _aggregate_match_counts(rows: Sequence[Dict[str, Any]]) -> Dict[int, int]:
    totals: Dict[int, int] = {}
    for row in rows:
        if not row.get("itemId"):
            continue
        item_id = int(row["itemId"])
        if item_id <= 0:
            continue
        totals[item_id] = totals.get(item_id, 0) + int(row.get("matchCount") or 0)
    return totals


def _top_items_by_match_count(
    rows: Sequence[Dict[str, Any]],
    get_item_name: Callable[[int], str],
    *,
    limit: int,
) -> List[Dict[str, Any]]:
    sequence: List[Dict[str, Any]] = []
    for item_id, _mc in sorted(
        _aggregate_match_counts(rows).items(), key=lambda x: x[1], reverse=True
    )[:limit]:
        sequence.append({"id": item_id, "name": get_item_name(item_id)})
    return sequence


def _sequence_len(build: Any) -> int:
    return len(getattr(build, "sequence", None) or [])


def _time_from_role(build: Any) -> int:
    role = getattr(build, "role", None) or ""
    if role.startswith("time_"):
        try:
            return int(role.split("_", 1)[1])
        except (IndexError, ValueError):
            pass
    return -1


def pick_titan_endgame_sequence(
    builds: Sequence[Any],
) -> List[Dict[str, Any]]:
    """
    Эталон endgame (до 6 предметов) из HeroBuild.

    Приоритет: endgame с 3+ предметами → любой билд с 2+ предметами →
    топ-6 одиночных популярных предметов по games.
    """
    item_builds = [b for b in builds if getattr(b, "build_type", None) == "item"]
    if not item_builds:
        return []

    for build in item_builds:
        if getattr(build, "role", None) == ENDGAME_ROLE and _sequence_len(build) >= MIN_ENDGAME_ITEMS:
            return list((build.sequence or [])[:MAX_FINAL_ITEMS])

    multi = [b for b in item_builds if _sequence_len(b) >= 2]
    if multi:
        best = max(
            multi,
            key=lambda b: (_sequence_len(b), _time_from_role(b), getattr(b, "games", 0)),
        )
        return list((best.sequence or [])[:MAX_FINAL_ITEMS])

    singles = sorted(
        [b for b in item_builds if _sequence_len(b) == 1],
        key=lambda b: getattr(b, "games", 0),
        reverse=True,
    )
    merged: List[Dict[str, Any]] = []
    seen: set[int] = set()
    for build in singles:
        seq = build.sequence or []
        if not seq:
            continue
        entry = seq[0]
        item_id = int(entry.get("id") or 0)
        if item_id <= 0 or item_id in seen:
            continue
        seen.add(item_id)
        merged.append(entry)
        if len(merged) >= MAX_FINAL_ITEMS:
            break
    return merged


SLOT_ID_FIELDS = tuple(f"item{i}_id" for i in range(MAX_FINAL_ITEMS))
SLOT_TIME_FIELDS = tuple(f"item{i}_time" for i in range(MAX_FINAL_ITEMS))


def sequence_to_slot_defaults(
    sequence: Sequence[Dict[str, Any]],
) -> Dict[str, int | None]:
    """Словарь item0_id … item5_id и item0_time … item5_time для HeroEndgameLoadout."""
    defaults: Dict[str, int | None] = {
        **{field: None for field in SLOT_ID_FIELDS},
        **{field: None for field in SLOT_TIME_FIELDS},
    }
    for idx, entry in enumerate(sequence[:MAX_FINAL_ITEMS]):
        raw = entry.get("id")
        if raw is None:
            continue
        item_id = int(raw)
        if item_id > 0:
            defaults[f"item{idx}_id"] = item_id
            time_raw = entry.get("time")
            if time_raw is not None:
                defaults[f"item{idx}_time"] = int(time_raw)
    return defaults


def loadout_to_items(
    loadout: Any,
    get_item_name: Callable[[int], str],
) -> List[Dict[str, Any]]:
    """6 слотов из таблицы HeroEndgameLoadout (id, name, time)."""
    items: List[Dict[str, Any]] = []
    for slot, id_field in enumerate(SLOT_ID_FIELDS):
        raw = getattr(loadout, id_field, None)
        if not raw:
            continue
        item_id = int(raw)
        if item_id <= 0:
            continue
        time_field = SLOT_TIME_FIELDS[slot]
        purchase_time = getattr(loadout, time_field, None)
        items.append(
            {
                "slot": slot,
                "id": item_id,
                "name": get_item_name(item_id),
                "time": int(purchase_time) if purchase_time is not None else None,
                "time_label": format_purchase_time(
                    int(purchase_time) if purchase_time is not None else None
                ),
            }
        )
    return items


def endgame_build_from_builds_data(
    builds_data: Sequence[Dict[str, Any]],
) -> tuple[List[Dict[str, Any]], int, float]:
    """sequence, games, win_rate для сохранения в HeroEndgameLoadout."""
    for row in builds_data:
        if row.get("role") == ENDGAME_ROLE and row.get("build_type") == "item":
            return (
                list(row.get("sequence") or [])[:MAX_FINAL_ITEMS],
                int(row.get("games") or 0),
                float(row.get("win_rate") or 0.0),
            )
    return [], 0, 0.0


def compare_item_sets(
    player_items: Sequence[Dict[str, Any]],
    titan_items: Sequence[Dict[str, Any]],
) -> Dict[str, Any]:
    player_ids = {int(i["id"]) for i in player_items}
    titan_ids = {int(i["id"]) for i in titan_items}
    overlap = player_ids & titan_ids
    return {
        "player_ids": player_ids,
        "titan_ids": titan_ids,
        "overlap": overlap,
        "only_player": player_ids - titan_ids,
        "only_titan": titan_ids - player_ids,
        "match_count": len(overlap),
    }
