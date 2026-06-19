from __future__ import annotations

import json
from pathlib import Path

from world.clock import TimeConfig, WorldClock, default_clock
from world.state import WorldState
from world.world import World

WORLD_STATE_PATH = Path(__file__).resolve().parent.parent / "data" / "world_state.json"

DEFAULT_ROOM_ITEMS = {"square": ["glowstick"]}


def save_world_state(state: WorldState) -> Path:
    WORLD_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "clock": state.clock.to_dict(),
        "room_items": {rid: list(items) for rid, items in state.room_items.items()},
    }
    WORLD_STATE_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return WORLD_STATE_PATH


def load_world_state(world: World, config: TimeConfig) -> WorldState:
    if not WORLD_STATE_PATH.exists():
        return WorldState(
            world=world,
            clock=default_clock(config),
            time_config=config,
            room_items=dict(DEFAULT_ROOM_ITEMS),
        )
    data = json.loads(WORLD_STATE_PATH.read_text(encoding="utf-8"))
    clock = WorldClock.from_dict(data.get("clock") or {})
    room_items = {str(k): list(v) for k, v in (data.get("room_items") or DEFAULT_ROOM_ITEMS).items()}
    return WorldState(world=world, clock=clock, time_config=config, room_items=room_items)