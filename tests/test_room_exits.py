from __future__ import annotations

from commands.helpers import format_look
from commands.registry import CommandContext
from shared.locale_content import format_room_exits
from tests.conftest import make_player, make_state


def test_format_room_exits_zh_labels_with_english_suffix():
    state = make_state()
    room = state.world.room("square")
    text = format_room_exits(room, state.world, "zh")
    assert "北 (north)" in text
    assert "東 (east)" in text
    assert "南 (south)" in text
    assert "西 (west)" in text
    assert "陰暗小巷" not in text
    assert "alley" not in text
    assert "→" not in text


def test_format_look_single_exit_line_no_description_duplicate():
    state = make_state()
    player = make_player(room_id="square")
    lines = format_look(CommandContext(player, state, ""))
    exit_lines = [line for line in lines if line.startswith("出口：")]
    assert len(exit_lines) == 1
    assert "北 (north)" in exit_lines[0]
    desc = next(line for line in lines if "全息廣告" in line)
    assert "出口" not in desc


def test_format_room_exits_en_locale():
    state = make_state()
    room = state.world.room("square")
    text = format_room_exits(room, state.world, "en")
    assert "north" in text
    assert "east" in text
    assert "→" not in text
    assert "Dark Alley" not in text