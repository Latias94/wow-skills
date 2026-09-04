#!/usr/bin/env python3
"""Create a compact, comparison-friendly summary from common WCL JSON exports."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def nested_values(value: Any, key: str) -> Iterable[Any]:
    """Yield values for a key anywhere in a JSON-like object."""
    if isinstance(value, dict):
        if key in value:
            yield value[key]
        for child in value.values():
            yield from nested_values(child, key)
    elif isinstance(value, list):
        for child in value:
            yield from nested_values(child, key)


def extract_events(payload: Any) -> List[Dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]

    for candidate in nested_values(payload, "events"):
        if isinstance(candidate, list):
            return [item for item in candidate if isinstance(item, dict)]
        if isinstance(candidate, dict) and isinstance(candidate.get("data"), list):
            return [item for item in candidate["data"] if isinstance(item, dict)]

    for candidate in nested_values(payload, "data"):
        if isinstance(candidate, list) and candidate and all(isinstance(item, dict) for item in candidate):
            if any("timestamp" in item for item in candidate):
                return candidate
    return []


def extract_entries(payload: Any) -> List[Dict[str, Any]]:
    for candidate in nested_values(payload, "entries"):
        if isinstance(candidate, list):
            return [item for item in candidate if isinstance(item, dict)]
    return []


def ability_name(event: Dict[str, Any]) -> str:
    ability = event.get("ability")
    if isinstance(ability, dict):
        name = ability.get("name")
        if name:
            return str(name)
        guid = ability.get("guid") or ability.get("gameID")
        if guid is not None:
            return f"spell-{guid}"
    for key in ("abilityName", "name"):
        if event.get(key):
            return str(event[key])
    guid = event.get("abilityGameID") or event.get("abilityID")
    return f"spell-{guid}" if guid is not None else "未知技能"


def integer(value: Any) -> Optional[int]:
    try:
        if value is None or isinstance(value, bool):
            return None
        return int(value)
    except (TypeError, ValueError):
        return None


def number(value: Any) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def source_id(event: Dict[str, Any], key: str = "sourceID") -> Optional[int]:
    return integer(event.get(key))


def target_id(event: Dict[str, Any]) -> Optional[int]:
    return integer(event.get("targetID"))


def find_fight_metadata(payloads: Sequence[Any], fight_id: Optional[int]) -> Optional[Dict[str, Any]]:
    candidates: List[Dict[str, Any]] = []
    for payload in payloads:
        for value in nested_values(payload, "fights"):
            if isinstance(value, list):
                candidates.extend(item for item in value if isinstance(item, dict))
    unique: Dict[int, Dict[str, Any]] = {}
    for fight in candidates:
        key = integer(fight.get("id"))
        if key is not None:
            unique.setdefault(key, fight)
    candidates = list(unique.values()) or candidates
    if fight_id is not None:
        for fight in candidates:
            if integer(fight.get("id")) == fight_id:
                return fight
    return candidates[0] if len(candidates) == 1 else None


def event_fight_id(event: Dict[str, Any]) -> Optional[int]:
    return integer(event.get("fight") or event.get("fightID"))


def choose_bounds(
    events: Sequence[Dict[str, Any]],
    metadata: Optional[Dict[str, Any]],
    start_ms: Optional[int],
    end_ms: Optional[int],
) -> Tuple[Optional[int], Optional[int], List[str]]:
    warnings: List[str] = []
    metadata_start = integer(metadata.get("startTime")) if metadata else None
    metadata_end = integer(metadata.get("endTime")) if metadata else None
    start = start_ms if start_ms is not None else metadata_start
    end = end_ms if end_ms is not None else metadata_end
    timestamps = [integer(event.get("timestamp")) for event in events]
    timestamps = [stamp for stamp in timestamps if stamp is not None]
    if start is None and timestamps:
        start = min(timestamps)
        warnings.append("未提供战斗元数据，起点按事件最早时间推断。")
    if end is None and timestamps:
        end = max(timestamps)
        warnings.append("未提供战斗元数据，终点按事件最晚时间推断；复活或战斗结束后的事件可能使时长偏长。")
    if start is not None and end is not None and end <= start:
        warnings.append("战斗起止时间无效，DPS 和覆盖率无法可靠计算。")
    return start, end, warnings


def relative_seconds(timestamp: Any, start_ms: Optional[int]) -> Optional[float]:
    stamp = integer(timestamp)
    if stamp is None or start_ms is None:
        return None
    return round((stamp - start_ms) / 1000.0, 3)


def parse_source_ids(raw: str) -> List[int]:
    result: List[int] = []
    for part in raw.split(","):
        value = integer(part.strip())
        if value is not None:
            result.append(value)
    return list(dict.fromkeys(result))


def entry_has_actor(entry: Any, actor_ids: Sequence[int]) -> bool:
    actor_set = set(actor_ids)
    if isinstance(entry, dict):
        if integer(entry.get("actor")) in actor_set:
            return True
        return any(entry_has_actor(child, actor_ids) for child in entry.values())
    if isinstance(entry, list):
        return any(entry_has_actor(child, actor_ids) for child in entry)
    return False


def entry_has_actor_field(entry: Any) -> bool:
    if isinstance(entry, dict):
        if "actor" in entry:
            return True
        return any(entry_has_actor_field(child) for child in entry.values())
    if isinstance(entry, list):
        return any(entry_has_actor_field(child) for child in entry)
    return False


def table_entry_summary(entry: Dict[str, Any]) -> Dict[str, Any]:
    total = number(entry.get("total"))
    targets: Dict[str, float] = {}
    for target in entry.get("targets") or []:
        if not isinstance(target, dict):
            continue
        name = str(target.get("name") or target.get("id") or "未知目标")
        targets[name] = round(number(target.get("total")), 3)
    result: Dict[str, Any] = {
        "name": str(entry.get("name") or ability_name(entry)),
        "total": round(total, 3),
        "uses": integer(entry.get("uses")),
        "hit_count": integer(entry.get("hitCount")),
    }
    if targets:
        result["targets"] = targets
    return result


def associated_actor_ids(events: Sequence[Dict[str, Any]], actor_id: int) -> List[int]:
    """Include pets, ancestors, and other actors summoned by the player."""
    associated = {actor_id}
    changed = True
    while changed:
        changed = False
        for event in events:
            if event.get("type") != "summon":
                continue
            if integer(event.get("sourceID")) in associated:
                summoned = integer(event.get("targetID"))
                if summoned is not None and summoned not in associated:
                    associated.add(summoned)
                    changed = True
    return sorted(associated)


def table_for_source(
    entries: Sequence[Dict[str, Any]], actor_ids: Sequence[int], source_scoped: bool = False
) -> List[Dict[str, Any]]:
    """Keep top-level table rows for a player, including composite rows."""
    if source_scoped:
        return list(entries)
    selected: List[Dict[str, Any]] = []
    any_actor_match = any(entry_has_actor(entry, actor_ids) for entry in entries)
    for entry in entries:
        if entry_has_actor(entry, actor_ids):
            selected.append(entry)
            continue
        # A source-scoped table often omits actor IDs on composite rows such as pets or copies.
        if any_actor_match and not entry_has_actor_field(entry):
            selected.append(entry)
    return selected


def gear_summary(combatant: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not combatant:
        return {}
    gear = combatant.get("gear") or []
    levels: List[int] = []
    for index, item in enumerate(gear):
        if not isinstance(item, dict) or index == 3:  # WCL 的 shirt 槽常被编码为 1 级物品。
            continue
        level = integer(item.get("itemLevel"))
        if level and level > 1 and integer(item.get("id")) != 0:
            levels.append(level)
    sets = [item for item in gear if isinstance(item, dict) and item.get("setID")]
    raw_stats = combatant.get("stats") if isinstance(combatant.get("stats"), dict) else {}
    if not raw_stats:
        aliases = {
            "strength": ("strength",),
            "agility": ("agility",),
            "intellect": ("intellect",),
            "stamina": ("stamina",),
            "crit": ("critSpell", "critRanged", "critMelee", "crit"),
            "haste": ("hasteSpell", "hasteRanged", "hasteMelee", "haste"),
            "mastery": ("mastery",),
            "versatility": ("versatilityDamageDone", "versatility"),
        }
        raw_stats = {
            name: combatant[key]
            for name, keys in aliases.items()
            for key in keys
            if combatant.get(key) is not None
        }
    return {
        "item_level_average": round(sum(levels) / len(levels), 2) if levels else None,
        "item_level_min": min(levels) if levels else None,
        "item_level_max": max(levels) if levels else None,
        "non_empty_slots": len(levels),
        "set_pieces": len(sets),
        "set_ids": sorted({integer(item.get("setID")) for item in sets if integer(item.get("setID")) is not None}),
        "stats": raw_stats or None,
    }


def buff_summary(events: Sequence[Dict[str, Any]], actor_id: int, start: Optional[int], end: Optional[int]) -> Dict[str, Any]:
    if start is None or end is None or end <= start:
        return {}
    active: Dict[str, int] = {}
    applications: Counter[str] = Counter()
    uptime: Counter[str] = Counter()
    ordered = sorted((event for event in events if integer(event.get("timestamp")) is not None), key=lambda item: integer(item["timestamp"]))
    for event in ordered:
        if target_id(event) != actor_id:
            continue
        event_type = str(event.get("type") or "")
        if event_type not in {"applybuff", "applybuffstack", "refreshbuff", "removebuff", "removebuffstack"}:
            continue
        name = ability_name(event)
        timestamp = integer(event.get("timestamp"))
        if timestamp is None:
            continue
        if event_type in {"applybuff", "applybuffstack"}:
            applications[name] += 1
            active.setdefault(name, max(timestamp, start))
        elif event_type == "refreshbuff":
            if name not in active:
                active[name] = max(timestamp, start)
        elif event_type == "removebuff":
            begin = active.pop(name, None)
            if begin is not None:
                uptime[name] += max(0, min(timestamp, end) - begin)
        # A stack removal is intentionally not treated as a full aura removal.
    for name, begin in active.items():
        uptime[name] += max(0, end - begin)
    result: Dict[str, Any] = {}
    for name in sorted(set(applications) | set(uptime)):
        result[name] = {
            "applications": applications[name],
            "uptime_ms": uptime[name],
            "uptime_pct": round(uptime[name] / (end - start) * 100, 2),
            "active_at_end": name in active,
        }
    return result


def combatant_for_source(events: Sequence[Dict[str, Any]], actor_id: int) -> Optional[Dict[str, Any]]:
    for event in events:
        if event.get("type") == "combatantinfo" and source_id(event) == actor_id:
            return event
    return None


def infer_source_name(entries: Sequence[Dict[str, Any]], actor_id: int) -> Optional[str]:
    """Infer a player name from actor/actorName/source rows when combatant info omits it."""
    found: List[str] = []

    def visit(value: Any) -> None:
        if isinstance(value, dict):
            if integer(value.get("actor")) == actor_id:
                for key in ("actorName", "sourceName", "name"):
                    if value.get(key) and str(value[key]) not in {"Ancestor", "Primal Storm Elemental", "Primal Fire Elemental"}:
                        found.append(str(value[key]))
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    for entry in entries:
        visit(entry)
    return found[0] if found else None


def longest_cast_gaps(cast_times: Sequence[float], limit: int = 10) -> List[float]:
    gaps = [round(cast_times[index] - cast_times[index - 1], 3) for index in range(1, len(cast_times))]
    return sorted((gap for gap in gaps if gap >= 2.0), reverse=True)[:limit]


def resource_summary(events: Sequence[Dict[str, Any]], actor_id: int) -> Dict[str, Any]:
    changes: Counter[str] = Counter()
    positive = 0.0
    negative = 0.0
    waste = 0.0
    for event in events:
        if source_id(event) != actor_id or event.get("type") not in {"resourcechange", "energize", "drain"}:
            continue
        amount = number(event.get("resourceChange"))
        if amount >= 0:
            positive += amount
        else:
            negative += abs(amount)
        waste += max(0.0, number(event.get("waste")))
        resource_type = event.get("resourceChangeType")
        key = str(resource_type) if resource_type is not None else "unknown"
        changes[key] += 1
    return {
        "event_count": sum(changes.values()),
        "positive_change": round(positive, 3),
        "negative_change": round(negative, 3),
        "waste": round(waste, 3),
        "by_resource_type": dict(changes),
    }


def source_summary(
    events: Sequence[Dict[str, Any]],
    entries: Sequence[Dict[str, Any]],
    actor_id: int,
    start: Optional[int],
    end: Optional[int],
    table_source_scoped: bool = False,
) -> Dict[str, Any]:
    duration_ms = max(0, (end - start) if start is not None and end is not None else 0)
    duration_min = duration_ms / 60000 if duration_ms else 0
    casts: Counter[str] = Counter()
    cast_times_by_ability: Dict[str, List[float]] = defaultdict(list)
    all_cast_times: List[float] = []
    begin_casts: Counter[str] = Counter()
    direct_damage: Counter[str] = Counter()
    direct_damage_total = 0.0

    relevant_events = [event for event in events if source_id(event) == actor_id]
    for event in relevant_events:
        event_type = str(event.get("type") or "")
        name = ability_name(event)
        rel = relative_seconds(event.get("timestamp"), start)
        if event_type == "cast":
            casts[name] += 1
            if rel is not None:
                cast_times_by_ability[name].append(rel)
                all_cast_times.append(rel)
        elif event_type == "begincast":
            begin_casts[name] += 1
        elif event_type == "damage":
            amount = number(event.get("amount"))
            direct_damage[name] += amount
            direct_damage_total += amount

    actor_ids = associated_actor_ids(events, actor_id)
    table_rows = [table_entry_summary(entry) for entry in table_for_source(entries, actor_ids, table_source_scoped)]
    table_rows.sort(key=lambda row: row["total"], reverse=True)
    table_total = sum(row["total"] for row in table_rows)
    damage_total = table_total if table_rows else direct_damage_total
    first_death: Optional[Dict[str, Any]] = None
    for event in events:
        if event.get("type") != "death" or target_id(event) != actor_id:
            continue
        timestamp = integer(event.get("timestamp"))
        if timestamp is None:
            continue
        candidate = {
            "time": relative_seconds(timestamp, start),
            "ability": ability_name(event),
            "timestamp": timestamp,
        }
        if first_death is None or timestamp < first_death["timestamp"]:
            first_death = candidate

    combatant = combatant_for_source(events, actor_id)
    alive_ms = duration_ms
    if first_death and first_death.get("timestamp") is not None and start is not None:
        alive_ms = max(0, min(duration_ms, first_death["timestamp"] - start))
    target_rows: Dict[str, float] = defaultdict(float)
    for row in table_rows:
        for target, amount in (row.get("targets") or {}).items():
            target_rows[target] += number(amount)

    abilities_cast = {
        name: {
            "casts": count,
            "casts_per_min": round(count / duration_min, 3) if duration_min else None,
            "times": [round(value, 3) for value in sorted(cast_times_by_ability[name])],
        }
        for name, count in casts.most_common()
    }
    damage_breakdown = []
    for row in table_rows:
        item = dict(row)
        item["share_pct"] = round(row["total"] / damage_total * 100, 2) if damage_total else 0
        damage_breakdown.append(item)

    return {
        "source_id": actor_id,
        "name": (combatant.get("sourceName") or combatant.get("name") if combatant else None) or infer_source_name(entries, actor_id),
        "spec": (combatant.get("spec") or combatant.get("specName") if combatant else None),
        "spec_id": integer(combatant.get("specID")) if combatant else None,
        "role": combatant.get("role") if combatant else None,
        "gear": gear_summary(combatant),
        "duration_ms": duration_ms,
        "alive_ms": alive_ms,
        "alive_pct": round(alive_ms / duration_ms * 100, 2) if duration_ms else None,
        "damage_total": round(damage_total, 3),
        "dps": round(damage_total / (duration_ms / 1000), 3) if duration_ms else None,
        "encounter_dps": round(damage_total / (duration_ms / 1000), 3) if duration_ms else None,
        "alive_dps": round(damage_total / (alive_ms / 1000), 3) if alive_ms else None,
        "direct_event_damage_total": round(direct_damage_total, 3),
        "casts_total": sum(casts.values()),
        "casts_per_min": round(sum(casts.values()) / duration_min, 3) if duration_min else None,
        "begincast_total": sum(begin_casts.values()),
        "abilities_cast": abilities_cast,
        "damage_breakdown": damage_breakdown,
        "target_damage": {name: round(amount, 3) for name, amount in sorted(target_rows.items(), key=lambda item: item[1], reverse=True)},
        "direct_event_damage_by_ability": {name: round(amount, 3) for name, amount in direct_damage.most_common()},
        "cast_gap_candidates_seconds": longest_cast_gaps(sorted(all_cast_times)),
        "buffs": buff_summary(events, actor_id, start, end),
        "resource": resource_summary(events, actor_id),
        "death": first_death,
        "event_count": len(relevant_events),
    }


def compare_sources(summaries: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if len(summaries) < 2:
        return []
    baseline = summaries[0]
    baseline_casts = {name: value["casts"] for name, value in baseline.get("abilities_cast", {}).items()}
    baseline_damage = {row["name"]: row["total"] for row in baseline.get("damage_breakdown", [])}
    comparisons: List[Dict[str, Any]] = []
    for current in summaries[1:]:
        current_casts = {name: value["casts"] for name, value in current.get("abilities_cast", {}).items()}
        current_damage = {row["name"]: row["total"] for row in current.get("damage_breakdown", [])}
        cast_delta = {
            name: current_casts.get(name, 0) - baseline_casts.get(name, 0)
            for name in sorted(set(current_casts) | set(baseline_casts))
        }
        damage_delta = {
            name: round(current_damage.get(name, 0) - baseline_damage.get(name, 0), 3)
            for name in sorted(set(current_damage) | set(baseline_damage))
        }
        comparisons.append(
            {
                "baseline_source_id": baseline["source_id"],
                "source_id": current["source_id"],
                "dps_delta": round(number(current.get("dps")) - number(baseline.get("dps")), 3),
                "casts_per_min_delta": round(number(current.get("casts_per_min")) - number(baseline.get("casts_per_min")), 3),
                "cast_count_delta": cast_delta,
                "damage_delta": damage_delta,
                "target_damage_delta": {
                    name: round(number(current.get("target_damage", {}).get(name)) - number(baseline.get("target_damage", {}).get(name)), 3)
                    for name in sorted(set(current.get("target_damage", {})) | set(baseline.get("target_damage", {})))
                },
            }
        )
    return comparisons


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="把 WCL 事件和伤害表 JSON 整理成可比较摘要。")
    parser.add_argument("--events", type=Path, action="append", help="事件 JSON 文件；可重复传入多个分页或玩家文件")
    parser.add_argument("--table", type=Path, help="伤害表 JSON 文件")
    parser.add_argument("--source-ids", required=True, help="要分析的 sourceID，多个 ID 用逗号分隔")
    parser.add_argument("--fight-id", type=int, help="按 fight 字段过滤战斗")
    parser.add_argument("--table-source-scoped", action="store_true", help="声明伤害表只属于指定 source（常见于带 source 参数的 WCL 导出）")
    parser.add_argument("--start-ms", type=int, help="覆盖战斗开始时间戳")
    parser.add_argument("--end-ms", type=int, help="覆盖战斗结束时间戳")
    parser.add_argument("--output", type=Path, help="输出 JSON 文件；省略则输出到标准输出")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.events and not args.table:
        print("至少需要 --events 或 --table。", file=sys.stderr)
        return 2

    event_payloads = [load_json(path) for path in (args.events or [])]
    table_payload = load_json(args.table) if args.table else {}
    all_events: List[Dict[str, Any]] = []
    seen_events = set()
    for payload in event_payloads:
        for event in extract_events(payload):
            key = (
                event.get("timestamp"),
                event.get("type"),
                event.get("sourceID"),
                event.get("targetID"),
                ability_name(event),
                event.get("amount"),
                event.get("fight") or event.get("fightID"),
            )
            if key not in seen_events:
                seen_events.add(key)
                all_events.append(event)
    if args.fight_id is not None:
        all_events = [event for event in all_events if event_fight_id(event) == args.fight_id]
    entries = extract_entries(table_payload)
    source_ids = parse_source_ids(args.source_ids)
    if not source_ids:
        print("--source-ids 没有可用的整数 ID。", file=sys.stderr)
        return 2

    metadata = find_fight_metadata([*event_payloads, table_payload], args.fight_id)
    start, end, warnings = choose_bounds(all_events, metadata, args.start_ms, args.end_ms)
    if (start is None or end is None) and isinstance(table_payload, dict):
        table_duration = integer(table_payload.get("totalTime"))
        if table_duration and start is None and end is None:
            start, end = 0, table_duration
            warnings.append("事件文件没有可用时间戳，时长使用伤害表的 totalTime。")
    table_source_scoped = bool(args.table_source_scoped)
    if table_source_scoped and len(source_ids) > 1:
        warnings.append("伤害表被声明为单一 source，但提供了多个 source ID；表格伤害会对每个 source 重复使用。")
    if entries and not all_events and not table_source_scoped:
        warnings.append("只有伤害表而没有事件；如该表来自单一 source，请加 --table-source-scoped，否则宠物/复制体伤害可能无法归属。")
    summaries = [source_summary(all_events, entries, actor_id, start, end, table_source_scoped) for actor_id in source_ids]
    result = {
        "schema_version": 1,
        "fight": {
            "id": args.fight_id,
            "name": metadata.get("name") if metadata else None,
            "difficulty": metadata.get("difficulty") if metadata else None,
            "kill": metadata.get("kill") if metadata else None,
            "start_ms": start,
            "end_ms": end,
            "duration_ms": max(0, end - start) if start is not None and end is not None else None,
        },
        "sources": summaries,
        "comparisons": compare_sources(summaries),
        "warnings": warnings,
        "input": {
            "events_file": [str(path) for path in (args.events or [])] or None,
            "table_file": str(args.table) if args.table else None,
            "event_count": len(all_events),
            "table_entry_count": len(entries),
        },
    }
    serialized = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(serialized + "\n", encoding="utf-8")
    else:
        print(serialized)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
