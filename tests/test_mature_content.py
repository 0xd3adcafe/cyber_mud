from __future__ import annotations

from commands.registry import dispatch
from tests.conftest import make_player, make_state
from world.mature_validate import validate_mature_content
from world.loader import load_world


def test_mature_talk_and_flirt():
    state = make_state()
    player = make_player(locale="en", room_id="kabuki_lounge", content_rating="mature")
    state.npc_rooms["kabuki_host"] = "kabuki_lounge"
    talk = dispatch("talk kabuki_host", player, state, [], [player])
    assert any("flirt" in line.lower() or "vip" in line.lower() for line in talk.lines)

    flirt = dispatch("flirt kabuki_host", player, state, [], [player])
    assert flirt.lines


def test_teen_cannot_see_mature_gig():
    state = make_state()
    player = make_player(locale="en", content_rating="teen")
    result = dispatch("gigs list", player, state, [], [player])
    joined = "\n".join(result.lines)
    assert "Lounge Rumor" not in joined


def test_mature_braindance_gated():
    state = make_state()
    teen = make_player(locale="en", room_id="bd_den", content_rating="teen")
    result = dispatch("braindance velvet_ruin", teen, state, [], [teen])
    assert any("18+" in line or "mature" in line.lower() for line in result.lines)


def test_validate_mature_yaml():
    world = load_world()
    errors = [issue for issue in validate_mature_content(world) if issue.severity == "error"]
    assert not errors