from __future__ import annotations

from commands.registry import dispatch
from tests.conftest import make_player, make_state


def test_wintr_whisper_requires_net_shell():
    player = make_player(locale="en", room_id="watson_1_0", content_rating="mature")
    state = make_state()
    state.npc_rooms["net_wintr_proxy"] = "watson_1_0"
    denied = dispatch("whisper net_wintr_proxy hello", player, state, [], [])
    assert any("net" in line.lower() for line in denied.lines)

    player.net_shell = True
    player.ram = 4
    allowed = dispatch("whisper net_wintr_proxy trace climbing", player, state, [], [])
    assert allowed.lines
    assert "trace" in "\n".join(allowed.lines).lower() or "proxy" in "\n".join(allowed.lines).lower()


def test_wintr_net_node_exists():
    state = make_state()
    node = state.world.net_node("net_wintr_proxy")
    assert node is not None
    assert node.room_id == "watson_1_0"