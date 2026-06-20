from client.login_motd import (
    banner_text,
    default_tips,
    format_login_banner,
    is_motd_separator,
    merge_tips,
    parse_motd_line,
)


def test_is_motd_separator():
    assert is_motd_separator("═══════════════════════════════════════")
    assert is_motd_separator("---")
    assert not is_motd_separator("登入後輸入 look 探索。")


def test_parse_motd_line_skips_decorations():
    assert parse_motd_line("══════") is None
    assert parse_motd_line("◈ 夜城神經連結", title="◈ 夜城神經連結") is None
    assert parse_motd_line("登入後輸入 look 探索。") == "登入後輸入 look 探索。"


def test_default_tips_loads_locale():
    tips = default_tips("zh")
    assert len(tips) >= 4
    assert any("look" in tip for tip in tips)


def test_merge_tips_dedupes():
    merged = merge_tips(["a", "b"], ["b", "c"])
    assert merged == ["a", "b", "c"]


def test_format_login_banner_has_spinner_and_tip():
    text = format_login_banner("◈ Title", "SUB", "tip line", frame=1)
    assert "◈ Title" in text
    assert "tip line" in text
    assert "⠙" in text


def test_banner_text_uses_locale_title():
    text = banner_text(locale="zh", tips=["測試提示"], tip_index=0, frame=0)
    assert "夜城神經連結" in text
    assert "測試提示" in text