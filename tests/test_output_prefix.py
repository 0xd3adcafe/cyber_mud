from client.output_prefix import classify_output_line, format_output_line
from shared.protocol import ERR_PREFIX, MOTD_PREFIX, SYS_PREFIX


def test_classify_output_line():
    assert classify_output_line(f"{SYS_PREFIX}ok") == "sys"
    assert classify_output_line(f"{ERR_PREFIX}fail") == "err"
    assert classify_output_line(f"{MOTD_PREFIX}welcome") == "env"
    assert classify_output_line("◈ Neon Square") == "env"


def test_format_output_line_static_by_default():
    line = format_output_line("hello")
    assert "hello" in line
    assert "›" in line


def test_format_output_line_animate_echo():
    line = format_output_line("> look", kind="echo", frame=1, animate=True)
    assert "⠙" in line
    done = format_output_line("> look", kind="echo", animate=False)
    assert "❯" in done