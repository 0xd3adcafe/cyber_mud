from commands.registry import dispatch, player_meta, CommandContext
from shared.prompt_tokens import expand_prompt
from tests.conftest import make_player, make_state


def test_prompt_show_default():
    player, state = make_player(), make_state()
    result = dispatch("prompt show", player, state, [], [])
    text = "\n".join(result.lines)
    assert "提示符" in text
    assert "%n" in text


def test_prompt_set():
    player, state = make_player(), make_state()
    result = dispatch("prompt set [%h] %r>", player, state, [], [])
    assert player.prompt_mud == "[%h] %r>"
    assert result.world_changed
    meta = player_meta(CommandContext(player, state, ""))
    assert "[" in meta["prompt_mud"]


def test_expand_prompt_tokens():
    player, state = make_player(name="Vy"), make_state()
    expanded = expand_prompt("%n|%r|%h|%t", player, state)
    assert "V" in expanded
    assert "霓虹廣場" in expanded
    assert "100/100" in expanded