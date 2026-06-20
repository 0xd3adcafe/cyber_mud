from __future__ import annotations

import asyncio

from server.game import ClientSession, Game
from server.heartbeat import format_heartbeat
from tests.conftest import make_player, make_state


def test_format_heartbeat_includes_world_stats():
    state = make_state()
    state.tick_count = 7
    state.encounters["x"] = object()  # type: ignore[assignment]
    state.corpses["c"] = object()  # type: ignore[assignment]
    state.npc_respawns["thug"] = 99
    game = Game(state=state)
    game.sessions.append(ClientSession(writer=object(), player=make_player(name="V")))

    line = format_heartbeat(game, started_at=0.0, dev=True, locale="en")

    assert "tick=7" in line
    assert "conn 1/1" in line
    assert "combat 1" in line
    assert "corpses 1" in line
    assert "respawn 1" in line
    assert "DEV" in line


def test_notify_dev_reload_logs_data(capsys):
    game = Game(state=make_state())
    asyncio.run(game.notify_dev_reload("data"))
    out = capsys.readouterr().out
    assert "World data reloaded" in out
    assert "rooms" in out


def test_notify_dev_reload_logs_code_failures(capsys):
    game = Game(state=make_state())
    asyncio.run(game.notify_dev_reload("code", failures=[("commands.foo", "boom")]))
    out = capsys.readouterr().out
    assert "Code reload" in out
    assert "commands.foo" in out
    assert "boom" in out