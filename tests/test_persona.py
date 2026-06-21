from __future__ import annotations

from commands.registry import dispatch
from tests.conftest import make_player, make_state
from world.persona import PERSONA_MAX_LEN


def test_persona_set_and_clear():
    state = make_state()
    player = make_player(locale="en", content_rating="mature")
    set_result = dispatch("persona set chrome runner with a scar", player, state, [], [player])
    assert any("chrome runner" in line for line in set_result.lines)
    assert player.persona == "chrome runner with a scar"

    show = dispatch("persona", player, state, [], [player])
    assert any("chrome runner" in line for line in show.lines)

    clear = dispatch("persona clear", player, state, [], [player])
    assert player.persona == ""
    assert any("cleared" in line.lower() for line in clear.lines)


def test_persona_max_length():
    state = make_state()
    player = make_player(locale="en")
    long_text = "x" * (PERSONA_MAX_LEN + 50)
    dispatch(f"persona set {long_text}", player, state, [], [player])
    assert len(player.persona) == PERSONA_MAX_LEN


def test_look_me_keeps_vitals():
    state = make_state()
    player = make_player(locale="en", hp=80, max_hp=100, fatigue=12)
    dispatch("persona set quiet fixer", player, state, [], [player])
    result = dispatch("look me", player, state, [], [player])
    joined = "\n".join(result.lines)
    assert "80/100" in joined
    assert "Fatigue 12" in joined or "fatigue" in joined.lower()
    assert "quiet fixer" in joined


def test_look_peer_shows_persona():
    state = make_state()
    viewer = make_player(name="Vy", locale="en", room_id="square")
    peer = make_player(name="Alt", locale="en", room_id="square")
    peer.persona = "Street doc with mirrored shades"
    result = dispatch("look Alt", viewer, state, [peer], [viewer, peer])
    joined = "\n".join(result.lines)
    assert "Alt" in joined
    assert "mirrored shades" in joined


def test_teen_can_set_persona():
    state = make_state()
    teen = make_player(locale="en", content_rating="teen")
    result = dispatch("persona set rookie netrunner", teen, state, [], [teen])
    assert teen.persona == "rookie netrunner"
    assert result.lines