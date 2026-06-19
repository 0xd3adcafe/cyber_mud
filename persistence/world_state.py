from __future__ import annotations

import json
from pathlib import Path

from entities.corpse import Corpse
from world.clock import TimeConfig, WorldClock, default_clock
from world.loader import default_room_items
from world.state import WorldState
from world.weather import default_weather, load_weather_config
from world.world import World

WORLD_STATE_PATH = Path(__file__).resolve().parent.parent / "data" / "world_state.json"

DEFAULT_ROOM_ITEMS = default_room_items()


def default_npc_rooms(world: World) -> dict[str, str]:
    return {
        npc_id: npc.room_id
        for npc_id, npc in world.npcs.items()
        if npc.room_id
    }


def save_world_state(state: WorldState) -> Path:
    WORLD_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "clock": state.clock.to_dict(),
        "room_items": {rid: list(items) for rid, items in state.room_items.items()},
        "npc_rooms": dict(state.npc_rooms),
        "corpses": {cid: corpse.to_dict() for cid, corpse in state.corpses.items()},
        "npc_respawns": {str(k): int(v) for k, v in state.npc_respawns.items()},
        "weather": dict(state.weather),
        "tick_count": state.tick_count,
    }
    WORLD_STATE_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return WORLD_STATE_PATH


def load_world_state(world: World, config: TimeConfig) -> WorldState:
    weather_config = load_weather_config()
    if not WORLD_STATE_PATH.exists():
        return WorldState(
            world=world,
            clock=default_clock(config),
            time_config=config,
            room_items=dict(DEFAULT_ROOM_ITEMS),
            npc_rooms=default_npc_rooms(world),
            weather=default_weather(weather_config),
            tick_count=0,
        )
    data = json.loads(WORLD_STATE_PATH.read_text(encoding="utf-8"))
    clock = WorldClock.from_dict(data.get("clock") or {})
    room_items = {str(k): list(v) for k, v in (data.get("room_items") or DEFAULT_ROOM_ITEMS).items()}
    npc_rooms = {str(k): str(v) for k, v in (data.get("npc_rooms") or default_npc_rooms(world)).items()}
    corpses = {
        str(cid): Corpse.from_dict(cdata)
        for cid, cdata in (data.get("corpses") or {}).items()
    }
    npc_respawns = {str(k): int(v) for k, v in (data.get("npc_respawns") or {}).items()}
    weather = {str(k): str(v) for k, v in (data.get("weather") or default_weather(weather_config)).items()}
    tick_count = int(data.get("tick_count", 0))
    return WorldState(
        world=world,
        clock=clock,
        time_config=config,
        room_items=room_items,
        npc_rooms=npc_rooms,
        corpses=corpses,
        npc_respawns=npc_respawns,
        weather=weather,
        tick_count=tick_count,
    )