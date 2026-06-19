from commands.registry import dispatch, player_meta, CommandContext
from tests.conftest import make_player, make_state


def _ctx():
    player = make_player(room_id="square")
    state = make_state()
    state.npc_rooms["broker"] = "square"
    return player, state


def test_talk_broker_starts_quest():
    player, state = _ctx()
    result = dispatch("talk 情報經紀人", player, state, [], [])
    assert player.active_quest == "broker_rumor"
    assert player.quest_flags.get("broker_rumor") == "started"
    assert any("經紀人" in line or "任務" in line for line in result.lines)
    meta = player_meta(CommandContext(player, state, ""))
    assert meta.get("quest")
    assert meta.get("hint")


def test_talk_missing_npc():
    player, state = _ctx()
    state.npc_rooms["broker"] = "alley"
    result = dispatch("talk broker", player, state, [], [])
    assert not player.active_quest
    assert any("沒有" in line for line in result.lines)