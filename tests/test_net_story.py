from __future__ import annotations

from commands.registry import dispatch
from tests.conftest import make_player, make_state
from world.loader import load_world
from world.quests import accept_quest, quest_is_done


def test_crypt_and_vault_net_nodes():
    world = load_world()
    assert "crypt_node" in world.net_nodes
    assert "vault_core" in world.net_nodes
    assert world.net_nodes["crypt_node"].room_id == "crypt"
    assert world.net_nodes["vault_core"].room_id == "data_vault"
    assert world.net_nodes["terminal"].room_id == "square"


def test_hack_core_quest_advances_on_terminal_hack():
    state = make_state()
    player = make_player(locale="en", room_id="square", name="Vy")
    player.quest_flags["broker_rumor"] = "done"
    accept_lines = accept_quest(player, state, "hack_core", "en")
    assert accept_lines
    assert player.active_quest == "hack_core"

    dispatch("take glowstick", player, state, [], [])
    assert player.quest_flags["hack_core"] == "stage_1"

    dispatch("talk broker", player, state, [], [])
    assert player.quest_flags["hack_core"] == "stage_2"

    player.net_shell = True
    result = dispatch("hack terminal", player, state, [], [])
    assert any("hack" in line.lower() or "terminal" in line.lower() for line in result.lines)
    assert player.quest_flags["hack_core"] == "ready"

    dispatch("talk broker", player, state, [], [])
    assert quest_is_done(player, "hack_core")