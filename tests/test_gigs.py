from commands.registry import dispatch
from tests.conftest import make_player, make_state


def test_gigs_opens_sidebar_panel():
    player, state = make_player(), make_state()
    result = dispatch("gigs", player, state, [], [])
    assert result.panel == "gigs"
    assert result.ui_json
    text = "\n".join(result.lines)
    assert "經紀人的傳聞" in text
    assert "街頭聲望" in text


def test_gigs_list_shows_full_board_in_log():
    player, state = make_player(), make_state()
    result = dispatch("gigs list", player, state, [], [])
    assert not result.panel
    assert "經紀人的傳聞" in "\n".join(result.lines)


def test_journal_alias_opens_gigs_panel():
    player, state = make_player(), make_state()
    result = dispatch("journal", player, state, [], [])
    assert result.panel == "gigs"


def test_quest_complete_flow():
    player = make_player(room_id="square")
    state = make_state()
    state.npc_rooms["broker"] = "square"
    state.npc_rooms["thug"] = "alley"

    dispatch("talk broker", player, state, [], [])
    assert player.active_quest == "broker_rumor"

    player.room_id = "alley"
    result = dispatch("talk thug", player, state, [], [])
    assert player.quest_flags["broker_rumor"] == "ready"
    assert any("委託目標達成" in line for line in result.lines)

    player.room_id = "square"
    before_gold = player.gold
    result = dispatch("talk broker", player, state, [], [])
    assert player.quest_flags["broker_rumor"] == "done"
    assert not player.active_quest
    assert player.gold == before_gold + 50
    assert player.street_cred == 10
    assert player.xp == 25
    assert any("委託完成" in line for line in result.lines)