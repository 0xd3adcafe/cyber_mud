from __future__ import annotations

from client.animated_log import AnimatedLogBuffer, _needs_block_separator
from client.animated_log import LogEntry
from client.log_classifier import classify_log_line
from client.log_styles import format_log_line
from shared.protocol import ERR_PREFIX, SYS_PREFIX


def test_classify_protocol_and_explicit_kinds():
    assert classify_log_line(f"{SYS_PREFIX}ready", kind="sys") == "sys"
    assert classify_log_line(f"{ERR_PREFIX}fail", kind="err") == "err"
    assert classify_log_line("> look", kind="echo") == "echo"
    assert classify_log_line(f"{SYS_PREFIX}ready") == "sys"
    assert classify_log_line(f"{ERR_PREFIX}boom") == "err"


def test_classify_env_and_move():
    assert classify_log_line("◈ Neon Square") == "env"
    assert classify_log_line("Exits: north, south") == "env"
    assert classify_log_line("You go north.") == "env_move"


def test_classify_combat_quest_progression():
    assert classify_log_line("You punch thug for 5 damage (enemy HP 10).") == "combat"
    assert classify_log_line("◈ Gig complete: alley_clearance") == "quest"
    assert classify_log_line("You gain 15 XP.") == "progression"
    assert classify_log_line("◈ Level up! Level 2 (perk points 1, attribute points 1)") == "progression"


def test_classify_social_and_ambient():
    assert classify_log_line("V says: hello") == "social"
    assert classify_log_line("Runner enters.") == "social"
    assert classify_log_line("Acid rain hisses on the pavement; fixers watch from the shadows.") == "ambient"


def test_format_log_line_uses_channel_glyphs():
    combat = format_log_line("You slash thug for 3 damage.", kind="combat")
    assert "⚔" in combat or "⌗" in combat
    quest = format_log_line("◈ Objective complete: dock_watch", kind="quest")
    assert "◆" in quest or "◈" in quest
    ambient = format_log_line("Distant gunfire stutters.", kind="ambient")
    assert "dim italic" in ambient


def test_animated_log_inserts_env_separator():
    buf = AnimatedLogBuffer()
    buf.append("You go north.", kind="env_move")
    buf.append("◈ Neon Square", kind="env")
    rendered = buf.render()
    assert any("───" in line for line in rendered)


def test_cooldown_lines_classified_as_combat():
    buf = AnimatedLogBuffer()
    buf.append("Action on cooldown (3s).", kind="text")
    assert buf.entries[-1].kind == "combat"


def test_block_separator_between_combat_rounds():
    prev = LogEntry("You punch thug.", kind="text")
    entry = LogEntry("You drop thug!", kind="combat")
    assert _needs_block_separator(prev, entry)