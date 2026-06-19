from __future__ import annotations

from client.env_format import format_environment_line, reset_environment_state
from client.themes import env_palette_for_theme


def _fmt(
    line: str,
    state: dict[str, str] | None = None,
    *,
    theme_id: str = "night_city",
) -> str:
    state = state if state is not None else {}
    return format_environment_line(line, state, theme_id=theme_id)


def test_room_header_and_description():
    state: dict[str, str] = {}
    palette = env_palette_for_theme("night_city")
    header = _fmt("◈ 霓虹廣場", state)
    assert palette.header in header
    assert state["phase"] == "desc"

    desc = _fmt("全息廣告在酸雨後的積水上閃爍。", state)
    assert palette.desc in desc
    assert "italic" in desc


def test_exits_items_npcs_colors():
    state: dict[str, str] = {}
    palette = env_palette_for_theme("night_city")
    exits = _fmt("出口：北 (north)、南 (south)", state)
    assert palette.exits in exits

    items = _fmt("地上：螢光棒 (Glowstick)、戰術折刀 (Tactical Knife)", state)
    assert palette.items in items
    assert "Glowstick" in items

    npcs = _fmt("這裡有：情報經紀人 (Info Broker)", state)
    assert palette.npcs in npcs


def test_scan_header_and_hidden():
    state: dict[str, str] = {}
    palette = env_palette_for_theme("night_city")
    scan = _fmt("◈ 掃描 — 霓虹廣場", state)
    assert palette.scan in scan

    hidden = _fmt("◈ 隱藏線索：牆縫裡似乎藏著密碼。", state)
    assert palette.hint in hidden


def test_movement_line_resets_phase():
    state: dict[str, str] = {"phase": "desc"}
    palette = env_palette_for_theme("night_city")
    move = _fmt("你前往 north。", state)
    assert palette.move_dir in move
    assert state["phase"] == "idle"


def test_theme_changes_environment_colors():
    state: dict[str, str] = {}
    night = env_palette_for_theme("night_city")
    matrix = env_palette_for_theme("matrix")

    night_header = _fmt("◈ 霓虹廣場", state, theme_id="night_city")
    matrix_header = _fmt("◈ 霓虹廣場", {}, theme_id="matrix")

    assert night.header in night_header
    assert matrix.header in matrix_header
    assert night.header != matrix.header


def test_animated_log_applies_environment_on_render():
    from client.animated_log import AnimatedLogBuffer

    buf = AnimatedLogBuffer(theme_id="night_city")
    palette = env_palette_for_theme("night_city")
    buf.append("look", kind="echo")
    buf.append("◈ 霓虹廣場", kind="text")
    buf.append("出口：北 (north)、東 (east)", kind="text")
    rendered = buf.render()
    assert any(palette.header in line for line in rendered)
    assert any(palette.exits in line for line in rendered)


def test_animated_log_theme_switch_updates_colors():
    from client.animated_log import AnimatedLogBuffer

    buf = AnimatedLogBuffer(theme_id="night_city")
    buf.append("look", kind="echo")
    buf.append("◈ 霓虹廣場", kind="text")

    night_palette = env_palette_for_theme("night_city")
    matrix_palette = env_palette_for_theme("matrix")
    before = buf.render()[-1]
    assert night_palette.header in before

    buf.set_theme_id("matrix")
    after = buf.render()[-1]
    assert matrix_palette.header in after
    assert night_palette.header not in after


def test_reset_on_echo():
    state: dict[str, str] = {"phase": "desc"}
    reset_environment_state(state)
    assert state["phase"] == "idle"