from __future__ import annotations

from commands.registry import dispatch
from tests.conftest import make_player, make_state
from world.quests import accept_quest, advance_quest_on_defeat, quest_is_done


def _setup_npcs(state):
    state.npc_rooms["broker"] = "square"
    state.npc_rooms["thug"] = "alley"


def test_gigs_accept_and_abandon():
    player = make_player(room_id="square")
    state = make_state()
    _setup_npcs(state)

    result = dispatch("gigs accept broker_rumor", player, state, [], [])
    assert player.active_quest == "broker_rumor"
    assert any("已接取" in line for line in result.lines)

    result = dispatch("gigs abandon", player, state, [], [])
    assert not player.active_quest
    assert any("放棄" in line for line in result.lines)


def test_gigs_accept_respects_street_cred():
    player = make_player(room_id="square", street_cred=2)
    state = make_state()
    _setup_npcs(state)

    result = dispatch("gigs accept dock_watch", player, state, [], [])
    assert not player.active_quest
    assert any("聲望不足" in line for line in result.lines)


def test_gigs_accept_requires_prerequisite():
    player = make_player(room_id="square", street_cred=10)
    state = make_state()
    _setup_npcs(state)

    result = dispatch("gigs accept alley_clearance", player, state, [], [])
    assert not player.active_quest
    assert any("需先完成" in line for line in result.lines)


def test_thug_does_not_auto_start_quest():
    player = make_player(room_id="alley")
    state = make_state()
    _setup_npcs(state)

    dispatch("talk thug", player, state, [], [])
    assert not player.active_quest


def test_defeat_npc_advances_quest():
    player = make_player(room_id="alley")
    player.active_quest = "alley_clearance"
    player.quest_flags["alley_clearance"] = "started"
    state = make_state()
    _setup_npcs(state)

    lines = advance_quest_on_defeat(player, state, "thug", "zh")
    assert player.quest_flags["alley_clearance"] == "ready"
    assert any("委託目標達成" in line for line in lines)


def test_gigs_journal_lists_active():
    player = make_player()
    player.active_quest = "broker_rumor"
    player.quest_flags["broker_rumor"] = "started"
    state = make_state()

    result = dispatch("gigs journal", player, state, [], [])
    assert result.panel == "gigs"
    text = "\n".join(result.lines)
    assert "進行中" in text
    assert "經紀人的傳聞" in text


def test_alley_clearance_reward_item_on_complete():
    player = make_player(room_id="square", street_cred=10)
    player.quest_flags["broker_rumor"] = "done"
    state = make_state()
    _setup_npcs(state)

    lines = accept_quest(player, state, "alley_clearance", "zh")
    assert lines
    player.quest_flags["alley_clearance"] = "ready"
    result = dispatch("talk broker", player, state, [], [])
    assert quest_is_done(player, "alley_clearance")
    assert "med_stim" in player.inventory
    assert any("委託完成" in line for line in result.lines)