from __future__ import annotations

from client.animated_log import AnimatedLogBuffer
from client.log_classifier import classify_log_line
from client.mature_format import (
    format_mature_line,
    has_paired_action_markers,
    is_mature_marker_line,
    is_sfx_line,
)
from client.meta_handlers import ClientViewState, apply_meta
from client.themes import mature_palette_for_theme
from client.ui_format import format_status_markup


def _fmt(line: str, *, theme_id: str = "night_city") -> str:
    return format_mature_line(line, theme_id=theme_id)


def test_action_segments_italic():
    palette = mature_palette_for_theme("night_city")
    out = _fmt("*Their hand brushes yours* over synth-glass.")
    assert palette.action in out
    assert "italic" in out
    assert "*Their hand brushes yours*" in out or "Their hand brushes yours" in out


def test_dialogue_segments_colored():
    palette = mature_palette_for_theme("night_city")
    out = _fmt('The host murmurs "invite only VIP guests hear."')
    assert palette.dialogue in out
    assert "invite only VIP guests hear." in out


def test_env_narrator_block():
    palette = mature_palette_for_theme("night_city")
    out = _fmt("> Frosted fields blur silhouettes in the booths.")
    assert palette.env_marker in out
    assert palette.env in out
    assert "Frosted fields blur silhouettes" in out


def test_sfx_line_palette():
    palette = mature_palette_for_theme("night_city")
    out = _fmt("*slurp* *ahh~*")
    assert palette.sfx in out
    assert "italic" in out


def test_mature_prefix_stripped():
    out = _fmt("[M· *A privacy field hums shut.*")
    assert "[M·" not in out
    assert "privacy field hums shut" in out


def test_classify_mature_markers():
    assert classify_log_line("*fade to black*") == "mature"
    assert classify_log_line("> The booth dims behind frosted glass.") == "mature"
    assert classify_log_line("[M· *chrome catches neon*") == "mature"
    assert classify_log_line("*slurp*") == "mature"
    assert classify_log_line("> look", kind="echo") == "echo"


def test_classify_echo_not_mature():
    assert classify_log_line("> look") == "text"
    assert not is_mature_marker_line("> look")


def test_has_paired_action_markers():
    assert has_paired_action_markers("*touch*")
    assert not has_paired_action_markers("no markers here")


def test_is_sfx_line():
    assert is_sfx_line("~ drip…")
    assert is_sfx_line("*slurp*")
    assert not is_sfx_line("You gain 15 XP.")


def test_animated_log_applies_mature_format_on_render():
    buf = AnimatedLogBuffer(theme_id="night_city")
    palette = mature_palette_for_theme("night_city")
    buf.append("*chrome catches neon*", kind="text")
    assert buf.entries[-1].kind == "mature"
    rendered = buf.render()[-1]
    assert palette.action in rendered or palette.body in rendered


def test_apply_meta_mature_voice_chip():
    state = ClientViewState(content_rating="teen")
    apply_meta(state, "mature_voice", "noir")
    assert state.mature_voice == "noir"
    teen_text = format_status_markup(state, host="127.0.0.1", port=4000)
    assert "Noir" not in teen_text
    apply_meta(state, "content_rating", "mature")
    mature_text = format_status_markup(state, host="127.0.0.1", port=4000)
    assert "Noir" in mature_text
    apply_meta(state, "mature_voice", "lewd")
    lewd_text = format_status_markup(state, host="127.0.0.1", port=4000)
    assert "Lewd" in lewd_text