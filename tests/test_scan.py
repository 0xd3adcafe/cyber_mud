from commands.registry import dispatch
from tests.conftest import make_player, make_state


def test_scan_square():
    player, state = make_player(), make_state()
    result = dispatch("scan", player, state, [], [])
    text = "\n".join(result.lines)
    assert "掃描" in text
    assert "螢光棒" in text or "戰術折刀" in text


def test_scan_hidden_in_alley():
    player, state = make_player(room_id="alley"), make_state(room_items={"alley": []})
    result = dispatch("scan", player, state, [], [])
    text = "\n".join(result.lines)
    assert "隱藏" in text


def test_sc_alias():
    player, state = make_player(), make_state()
    result = dispatch("sc", player, state, [], [])
    assert any("掃描" in line for line in result.lines)