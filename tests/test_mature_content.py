from __future__ import annotations

from commands.registry import dispatch
from tests.conftest import make_player, make_state
from world.mature_flavor import romance_line
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
    assert "Chrome Pull" not in joined


def test_mature_braindance_gated():
    state = make_state()
    teen = make_player(locale="en", room_id="bd_den", content_rating="teen")
    result = dispatch("braindance velvet_ruin", teen, state, [], [teen])
    assert any("18+" in line or "mature" in line.lower() for line in result.lines)


def test_validate_mature_yaml():
    world = load_world()
    errors = [issue for issue in validate_mature_content(world) if issue.severity == "error"]
    assert not errors


def test_mature_vip_and_dancer():
    state = make_state()
    player = make_player(locale="en", room_id="kabuki_vip", content_rating="mature")
    state.npc_rooms["kabuki_dancer"] = "kabuki_vip"
    teen = make_player(locale="en", room_id="kabuki_lounge", content_rating="teen")
    blocked = dispatch("go north", teen, state, [], [teen])
    assert any("18+" in line or "mature" in line.lower() for line in blocked.lines)

    flirt = dispatch("flirt kabuki_dancer", player, state, [], [player])
    assert flirt.lines


def test_velvet_job_hidden_from_teen():
    state = make_state()
    player = make_player(locale="en", content_rating="teen")
    result = dispatch("gigs list", player, state, [], [player])
    joined = "\n".join(result.lines)
    assert "Velvet Job" not in joined


def test_mature_look_room_flavor():
    state = make_state()
    mature = make_player(locale="en", room_id="kabuki_lounge", content_rating="mature")
    teen = make_player(locale="en", room_id="kabuki_lounge", content_rating="teen")
    mature_look = dispatch("look", mature, state, [], [mature])
    teen_look = dispatch("look", teen, state, [], [teen])
    mature_text = "\n".join(mature_look.lines)
    teen_text = "\n".join(teen_look.lines)
    assert "privacy fields" in mature_text.lower() or "flirt" in mature_text.lower()
    assert "privacy fields" not in teen_text.lower()


def test_mature_look_npc_detail():
    state = make_state()
    player = make_player(locale="en", room_id="bd_den", content_rating="mature")
    state.npc_rooms["bd_den_clerk"] = "bd_den"
    result = dispatch("look bd_den_clerk", player, state, [], [player])
    joined = "\n".join(result.lines)
    assert "archive" in joined.lower() or "cred" in joined.lower()


def test_staged_flirt_lines():
    assert "innuendo" in romance_line("en", "kabuki_flirt", 2).lower()
    assert "invite" in romance_line("en", "kabuki_flirt", 3).lower()
    assert romance_line("en", "kabuki_flirt", 1) != romance_line("en", "kabuki_flirt", 3)


def test_mature_interact_flavor():
    state = make_state()
    player = make_player(locale="en", room_id="kabuki_lounge", content_rating="mature")
    result = dispatch("interact chrome bar", player, state, [], [player])
    joined = "\n".join(result.lines)
    assert "foreplay" in joined.lower() or "contract" in joined.lower()


def test_bd_den_clerk_flirt_and_chrome_mirage():
    state = make_state()
    player = make_player(locale="en", room_id="bd_den", content_rating="mature", gold=50)
    state.npc_rooms["bd_den_clerk"] = "bd_den"
    talk = dispatch("talk bd_den_clerk", player, state, [], [player])
    assert any("chrome_mirage" in line for line in talk.lines)

    flirt = dispatch("flirt bd_den_clerk", player, state, [], [player])
    assert flirt.lines

    bd = dispatch("braindance chrome_mirage", player, state, [], [player])
    joined = "\n".join(bd.lines)
    assert "mirage" in joined.lower() or "mirrored" in joined.lower()
    assert player.braindance_flags.get("bd_chrome_mirage") == "done"


def test_chrome_pull_hidden_from_teen():
    state = make_state()
    player = make_player(locale="en", content_rating="teen", street_cred=10)
    result = dispatch("gigs list", player, state, [], [player])
    assert "Chrome Pull" not in "\n".join(result.lines)