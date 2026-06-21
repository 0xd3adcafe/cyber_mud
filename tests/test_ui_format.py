from client.meta_handlers import ClientViewState
from client.meta_handlers import SidebarPanel
from client.ui_format import (
    format_hint_markup,
    format_hotkey_bar,
    format_info_bar,
    format_sidebar_header,
    format_sidebar_markup,
    format_ui_sections,
    panel_header,
)


def test_panel_header_labels_en():
    assert "PDA" in panel_header("pda", locale="en")
    assert "F1" in panel_header("pda", locale="en")
    assert "F3" in panel_header("map", locale="en")
    assert "Gigs" in panel_header("gigs", locale="en")
    assert "F5" in panel_header("gigs", locale="en")


def test_panel_header_labels_zh():
    assert "委託" in panel_header("gigs", locale="zh")
    assert "地圖" in panel_header("map", locale="zh")


def test_format_hotkey_bar_en():
    text = format_hotkey_bar(locale="en")
    assert "Hotkeys" in text
    assert "Tab" in text
    assert "history" in text
    assert "F1" in text
    assert "F11" in text
    assert "/reconnect" in text
    net_text = format_hotkey_bar(locale="en", net_shell=True)
    assert "F12" in net_text


def test_format_hotkey_bar_zh():
    text = format_hotkey_bar(locale="zh")
    assert "快捷鍵" in text
    assert "說明" in text
    assert "↑↓" in text


def test_format_info_bar_reconnecting_zh():
    state = ClientViewState(room="廣場", locale="zh")
    text = format_info_bar(state, host="127.0.0.1", port=4000, reconnecting=True)
    assert "重連中" in text


def test_format_info_bar_reconnecting_en():
    state = ClientViewState(room="Square", locale="en")
    text = format_info_bar(state, host="127.0.0.1", port=4000, reconnecting=True)
    assert "Reconnecting" in text


def test_format_hint_combat_priority():
    state = ClientViewState(combat_log="你擊中目標", hint="任務", in_combat=True, combat_player_cd=30)
    state.combat_cd_synced_at = __import__("time").monotonic()
    text = format_hint_markup(state, spinner_frame=0)
    assert "你擊中目標" in text
    assert "P:30s" in text
    assert "任務" in text


def test_format_info_bar_omits_hint_rows():
    state = ClientViewState(hint="任務中", room="廣場")
    text = format_info_bar(state, host="127.0.0.1", port=4000)
    assert "廣場" in text
    assert "任務中" not in text


def test_format_sidebar_row_markup():
    state = ClientViewState(sidebar_stack=["pda"], sidebar_open=True)
    state.sidebar_panels["pda"] = SidebarPanel(
        ui={"title": "PDA", "sections": [{"kind": "row", "label": "HP", "value": "100/100"}]},
    )
    text = format_sidebar_markup(state)
    assert "100/100" in text
    assert "HP" in text


def test_format_sidebar_header_stacked_zh():
    state = ClientViewState(sidebar_stack=["map", "pda"], locale="zh")
    text = format_sidebar_header(state)
    assert "PDA" in text
    assert "地圖" in text


def test_format_sidebar_header_stacked_en():
    state = ClientViewState(sidebar_stack=["map", "pda"], locale="en")
    text = format_sidebar_header(state)
    assert "PDA" in text
    assert "Map" in text


def test_format_ui_sections():
    text = format_ui_sections({"sections": [{"kind": "row", "label": "RAM", "value": "8/8"}]})
    assert "RAM" in text
    assert "8/8" in text