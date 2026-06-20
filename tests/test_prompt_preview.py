from client.meta_handlers import ClientViewState
from client.prompt_preview import (
    detect_prompt_edit,
    expand_prompt_from_view,
    format_prompt_preview,
    format_prompt_show_lines,
)
from shared.prompt_tokens import CP2077_TEMPLATES


def _view(**kwargs) -> ClientViewState:
    state = ClientViewState()
    for key, value in kwargs.items():
        setattr(state, key, value)
    return state


def test_detect_prompt_edit_set_local():
    ctx = detect_prompt_edit("/prompt set [%h] %n>")
    assert ctx is not None
    assert ctx.template == "[%h] %n>"
    assert ctx.kind == "set"


def test_detect_prompt_edit_template():
    ctx = detect_prompt_edit("prompt template ncpd")
    assert ctx is not None
    assert ctx.template == CP2077_TEMPLATES["ncpd"]


def test_detect_prompt_edit_ignores_other_commands():
    assert detect_prompt_edit("look") is None
    assert detect_prompt_edit("/prompt show") is None


def test_expand_prompt_from_view_tokens():
    view = _view(
        player_name="V",
        room="霓虹廣場",
        hp="80/100",
        gold="500",
        level="3",
        street_cred="12",
        wanted="2",
        faction="荒坂公司",
        xp="40/100",
        period="夜晚",
        weather="酸雨",
        ram="4/8",
        time="22:15",
    )
    expanded = expand_prompt_from_view("★%v [%h] %n@%r %p", view)
    assert "★2" in expanded
    assert "80/100" in expanded
    assert "V@霓虹廣場" in expanded
    assert "夜晚" in expanded


def test_format_prompt_preview_markup_en():
    text = format_prompt_preview("[%h] %n>", "[80/100] V>", locale="en")
    assert "Preview" in text
    assert "[80/100] V>" in text


def test_format_prompt_preview_markup_zh():
    text = format_prompt_preview("[%h] %n>", "[80/100] V>", locale="zh")
    assert "預覽" in text
    assert "[80/100] V>" in text


def test_format_prompt_show_lines_lists_tokens_en():
    lines = format_prompt_show_lines(_view(player_name="V", hp="100/100", locale="en"))
    text = "\n".join(lines)
    assert "Prompt" in text
    assert "%n" in text
    assert "%l" in text


def test_format_prompt_show_lines_lists_tokens_zh():
    lines = format_prompt_show_lines(_view(player_name="V", hp="100/100", locale="zh"))
    text = "\n".join(lines)
    assert "提示符" in text
    assert "%n" in text
    assert "%l" in text