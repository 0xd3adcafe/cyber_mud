import json

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
    assert "肉體 3" in text or "Body 3" in text
    assert "RAM 4/8" in text
    assert "人性  100" in text or "Humanity 100" in text


def test_pda_integrates_growth_and_talents():
    player, state = make_player(), make_state()
    result = dispatch("pda", player, state, [], [])
    text = "\n".join(result.lines)
    assert "熟練" in text or "Proficienc" in text
    assert "天賦" in text or "Talent" in text
    assert "需等級" in text or "requires level" in text or "可學" in text or "available" in text


def test_pda_sidebar_ui_includes_growth_sections():
    player, state = make_player(), make_state()
    result = dispatch("pda", player, state, [], [])
    ui = json.loads(result.ui_json)
    titles = [section.get("title", "") for section in ui.get("sections", [])]
    assert any("熟練" in title or "Proficienc" in title for title in titles)
    assert any("天賦" in title or "Talent" in title for title in titles)
    row_labels = [section.get("label", "") for section in ui.get("sections", []) if section.get("kind") == "row"]
    assert any("成長" in label or "Growth" in label for label in row_labels)


def test_status_alias():
    player, state = make_player(), make_state()
    result = dispatch("status", player, state, [], [])
    assert any("PDA" in line for line in result.lines)