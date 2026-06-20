from commands.registry import dispatch
from tests.conftest import make_player, make_state


def test_pda_shows_vitals():
    player, state = make_player(), make_state()
    result = dispatch("pda", player, state, [], [])
    text = "\n".join(result.lines)
    assert result.panel == "pda"
    assert result.ui_json
    assert "PDA" in text
    assert "100/100" in text
    assert "肉體 3" in text
    assert "RAM 4/8" in text
    assert "人性  100" in text


def test_status_alias():
    player, state = make_player(), make_state()
    result = dispatch("status", player, state, [], [])
    assert any("PDA" in line for line in result.lines)


def test_pda_stats_subcommand():
    player, state = make_player(), make_state()
    result = dispatch("pda stats", player, state, [], [])
    text = "\n".join(result.lines)
    assert result.panel == "pda"
    assert "等級" in text or "Level" in text
    assert "肉體 3" in text or "Body 3" in text


def test_pda_talents_subcommand():
    player, state = make_player(), make_state()
    result = dispatch("pda talents", player, state, [], [])
    text = "\n".join(result.lines)
    assert result.panel == "pda"
    assert "天賦" in text or "Talent" in text