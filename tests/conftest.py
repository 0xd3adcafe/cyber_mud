from __future__ import annotations

import pytest

from commands import register_builtin_commands
from entities.player import Player
from world.clock import default_clock, load_time_config
from world.loader import load_world
from world.state import WorldState

register_builtin_commands()


def make_state(*, room_items: dict[str, list[str]] | None = None) -> WorldState:
    world = load_world()
    config = load_time_config()
    return WorldState(
        world=world,
        clock=default_clock(config),
        time_config=config,
        room_items=room_items if room_items is not None else {"square": ["glowstick"]},
    )


def make_player(*, room_id: str = "square", named: bool = True, name: str = "V") -> Player:
    return Player(room_id=room_id, locale="zh", named=named, name=name)


@pytest.fixture
def save_dir(tmp_path, monkeypatch):
    saves = tmp_path / "saves"
    saves.mkdir()
    monkeypatch.setattr("persistence.save.SAVE_DIR", saves)
    return saves


@pytest.fixture
def world_state_path(tmp_path, monkeypatch):
    path = tmp_path / "world_state.json"
    monkeypatch.setattr("persistence.world_state.WORLD_STATE_PATH", path)
    return path