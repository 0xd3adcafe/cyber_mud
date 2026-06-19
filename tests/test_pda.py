from commands.registry import dispatch
from tests.conftest import make_player, make_state


def test_pda_shows_vitals():
    player, state = make_player(), make_state()
    result = dispatch("pda", player, state, [], [])
    text = "\n".join(result.lines)
    assert "PDA" in text
    assert "100/100" in text
    assert "肉體 3" in text
    assert "RAM 4/8" in text
    assert "人性  100" in text


def test_status_alias():
    player, state = make_player(), make_state()
    result = dispatch("status", player, state, [], [])
    assert any("PDA" in line for line in result.lines)