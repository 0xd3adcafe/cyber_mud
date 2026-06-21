import json

from commands.registry import dispatch
from shared.protocol import UI_PREFIX, meta_line, ui_line
from tests.conftest import make_player, make_state


def test_mesh_panel_with_discovered_links():
    player = make_player(
        locale="en",
        discovered_net_links=["docks_grid_node<->watson_grid_node"],
    )
    state = make_state()
    result = dispatch("mesh", player, state, [], [])
    assert result.panel == "mesh"
    assert result.ui_json
    assert result.lines == []

    ui = json.loads(result.ui_json)
    assert ui["panel"] == "mesh"
    assert "ctOS mesh" in ui["title"]
    section_lines = ui["sections"][0]["lines"]
    assert section_lines
    assert "↔" in section_lines[0]


def test_mesh_panel_empty_shows_probe_hint():
    player = make_player(locale="en", discovered_net_links=[])
    state = make_state()
    result = dispatch("mesh", player, state, [], [])
    assert result.panel == "mesh"

    ui = json.loads(result.ui_json)
    assert ui["panel"] == "mesh"
    hint = ui["sections"][0]["lines"][0]
    assert "probe" in hint.lower()
    assert "NETRUN" in hint


def test_mesh_panel_meta_protocol():
    player = make_player(
        locale="zh",
        discovered_net_links=["docks_grid_node<->watson_grid_node"],
    )
    state = make_state()
    result = dispatch("mesh", player, state, [], [])

    protocol = [
        meta_line("ui_panel", result.panel),
        ui_line(result.ui_json),
        meta_line("ui_panel_end", "1"),
    ]
    assert protocol[0] == "@meta ui_panel=mesh"
    assert protocol[1].startswith(UI_PREFIX)
    assert protocol[-1] == "@meta ui_panel_end=1"
    assert result.meta.get("locale") == "zh"
    assert result.meta.get("auth") == "1"