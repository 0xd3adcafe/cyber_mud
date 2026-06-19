from client.animated_log import AnimatedLogBuffer
from client.cd_display import (
    format_combat_cd_label,
    format_cooldown_line,
    parse_combat_cd_meta,
    parse_cooldown_line,
    remaining_seconds,
)
from client.output_prefix import SPINNER_FRAMES, spinner_char


def test_spinner_char_cycles():
    assert spinner_char(0) == SPINNER_FRAMES[0]
    assert spinner_char(len(SPINNER_FRAMES)) == SPINNER_FRAMES[0]


def test_parse_cooldown_line_zh():
    parsed = parse_cooldown_line("行動冷卻中（60s）。")
    assert parsed == ("行動冷卻中", 60)


def test_parse_combat_cd_meta():
    assert parse_combat_cd_meta("P:60 N:30") == (60, 30)


def test_remaining_seconds_counts_down():
    assert remaining_seconds(10, 100.0, now=105.0) == 5
    assert remaining_seconds(10, 100.0, now=112.0) == 0


def test_format_combat_cd_label():
    assert format_combat_cd_label(45, 0) == "P:45s"
    assert format_combat_cd_label(0, 12) == "N:12s"


def test_animated_log_pending_only_on_command_line():
    buf = AnimatedLogBuffer()
    buf.append("> look", kind="echo")
    buf.mark_last_pending()
    buf.frame = 3
    pending_line = buf.render()[0]
    assert SPINNER_FRAMES[3] in pending_line
    buf.append("◈ 霓虹廣場", kind="text")
    buf.complete_pending()
    done_echo = buf.render()[0]
    assert "❯" in done_echo
    assert SPINNER_FRAMES[3] not in done_echo
    assert "›" in buf.render()[1]


def test_animated_log_render_entry_matches_render_tail():
    buf = AnimatedLogBuffer()
    buf.append("第一行", kind="text")
    buf.append("第二行", kind="sys")
    assert buf.render_entry() == buf.render()[-1]
    assert buf.render_entry(0) == buf.render()[0]


def test_animated_log_cooldown_tick():
    buf = AnimatedLogBuffer()
    buf.append("行動冷卻中（3s）。", kind="text")
    entry = buf.entries[0]
    entry.cd_started_at -= 2.0
    assert buf.tick_cooldowns()
    rendered = buf.render()[0]
    assert "1s" in rendered