from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml

from entities.npc import NPC
from world.content import load_shops

SCHEDULE_PATH = Path(__file__).resolve().parent.parent / "data" / "schedule.yaml"


@lru_cache(maxsize=1)
def _load_schedule() -> dict:
    if not SCHEDULE_PATH.exists():
        return {}
    with SCHEDULE_PATH.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def clear_schedule_cache() -> None:
    _load_schedule.cache_clear()


def _shop_hours(shop_id: str) -> tuple[int, int] | None:
    shops = _load_schedule().get("shops") or {}
    shop = shops.get(shop_id)
    if shop:
        return int(shop.get("open_hour", 0)), int(shop.get("close_hour", 24))
    for loaded in load_shops().values():
        if loaded.id == shop_id:
            return loaded.open_hour, loaded.close_hour
    return None


def shop_is_open(shop_id: str, hour: int) -> bool:
    if not shop_id:
        return True
    hours = _shop_hours(shop_id)
    if hours is None:
        return True
    open_hour, close_hour = hours
    if open_hour <= close_hour:
        return open_hour <= hour < close_hour
    return hour >= open_hour or hour < close_hour


def npc_scheduled_room(npc: NPC, period_id: str, fallback: str) -> str:
    if npc.schedule and period_id in npc.schedule:
        return npc.schedule[period_id]
    return fallback