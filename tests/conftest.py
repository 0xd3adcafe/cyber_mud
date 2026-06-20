from __future__ import annotations

import pytest

from commands import register_builtin_commands
from client.connection import ServerConnection
from entities.player import Player
from persistence.world_state import default_npc_rooms
from world.clock import default_clock, load_time_config
from world.loader import default_room_items, load_world
from world.state import WorldState
from world.weather import default_weather, load_weather_config

register_builtin_commands()


def make_state(*, room_items: dict[str, list[str]] | None = None) -> WorldState:
    world = load_world()
    config = load_time_config()
    weather_config = load_weather_config()
    return WorldState(
        world=world,
        clock=default_clock(config),
        time_config=config,
        room_items=room_items if room_items is not None else default_room_items(),
        npc_rooms=default_npc_rooms(world),
        weather=default_weather(weather_config),
        tick_count=0,
    )


@pytest.fixture(autouse=True)
def _fast_client_tcp_connect(monkeypatch):
    """Avoid real TCP connect during Textual client tests (on_mount)."""

    async def _connect(self: ServerConnection) -> None:
        from tests.client_ui_helpers import _FakeReader, _FakeWriter

        self._reader = _FakeReader()
        self._writer = _FakeWriter()

    monkeypatch.setattr(ServerConnection, "connect", _connect)


def make_player(*, room_id: str = "square", locale: str = "zh", named: bool = True, name: str = "Vy", **kwargs) -> Player:
    # Production default is en (entities/player.py); tests default zh for legacy assertions.
    return Player(room_id=room_id, locale=locale, named=named, name=name, **kwargs)


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