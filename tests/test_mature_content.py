from __future__ import annotations

import pytest

from commands.registry import dispatch
from shared.mature_paths import mature_content_available
from tests.conftest import make_player, make_state
from world.mature_flavor import romance_line
from world.mature_validate import BANNED_LEWD_CLICHES, validate_mature_content
from world.mature_voice import load_voice_config, resolve_mature_voice
from world.loader import load_world

pytestmark = pytest.mark.skipif(
    not mature_content_available(),
    reason="mature content pack missing (git submodule data/mature)",
)


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
    assert "vip" in romance_line("en", "kabuki_flirt", 2).lower()
    assert "backstage" in romance_line("en", "kabuki_flirt", 4).lower()
    assert romance_line("en", "kabuki_flirt", 1) != romance_line("en", "kabuki_flirt", 3)
    assert romance_line("en", "kabuki_flirt", 3, voice="lewd") != romance_line(
        "en", "kabuki_flirt", 3, voice="noir"
    )


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


def test_mature_say_in_lounge():
    state = make_state()
    player = make_player(locale="en", room_id="kabuki_lounge", content_rating="mature", name="Vy")
    result = dispatch("say hello", player, state, [], [player])
    joined = "\n".join(result.lines)
    assert "murmur" in joined.lower() or "privacy" in joined.lower()
    assert result.broadcast_mature_key == "social.say_broadcast.kabuki_lounge"


def test_romance_gift_to_host():
    state = make_state()
    player = make_player(
        locale="en",
        room_id="kabuki_lounge",
        content_rating="mature",
        inventory=["synth_coffee"],
    )
    state.npc_rooms["kabuki_host"] = "kabuki_lounge"
    result = dispatch("give synth_coffee kabuki_host", player, state, [], [player])
    joined = "\n".join(result.lines)
    assert "synth_coffee" not in player.inventory
    assert "scanner" in joined.lower() or "smile" in joined.lower()
    assert result.broadcast_mature_key == "give.broadcast"


def test_taunt_and_finish_in_combat():
    from combat.encounter import encounter_for_player, start_encounter

    state = make_state()
    player = make_player(locale="en", room_id="alley", content_rating="mature")
    state.npc_rooms["thug"] = "alley"
    start_encounter(state, player, "thug")
    taunt = dispatch("taunt thug", player, state, [], [player])
    assert any("taunt" in line.lower() or "chrome" in line.lower() or "challenge" in line.lower() for line in taunt.lines)

    encounter = encounter_for_player(state, player)
    assert encounter is not None
    encounter.npc_hp = 10
    too_early = dispatch("finish", player, state, [], [player])
    assert any("too strong" in line.lower() for line in too_early.lines) or encounter.npc_hp == 10

    encounter.npc_hp = 8
    finish = dispatch("finish", player, state, [], [player])
    joined = "\n".join(finish.lines).lower()
    assert not player.in_combat
    assert any(
        word in joined
        for word in ("finish", "coup", "mercy", "brutal", "blood", "smear", "wet", "crunch", "unmistakable")
    )
    assert finish.broadcast_mature_key.startswith("combat.victory_broadcast_")


def test_teen_cannot_taunt_or_finish():
    from combat.encounter import start_encounter

    state = make_state()
    player = make_player(locale="en", room_id="alley", content_rating="teen")
    state.npc_rooms["thug"] = "alley"
    start_encounter(state, player, "thug")
    assert any("18+" in line or "mature" in line.lower() for line in dispatch("taunt thug", player, state, [], []).lines)
    assert any("18+" in line or "mature" in line.lower() for line in dispatch("finish", player, state, [], []).lines)


def test_resolve_mature_voice_triggers():
    state = make_state()
    lounge = make_player(locale="en", room_id="kabuki_lounge", content_rating="mature")
    square = make_player(locale="en", room_id="square", content_rating="mature")
    lounge_room = state.world.room("kabuki_lounge")
    square_room = state.world.room("square")
    assert resolve_mature_voice(lounge, state, lounge_room) == "lewd"
    assert resolve_mature_voice(square, state, square_room) == "noir"

    cfg = load_voice_config()
    square.braindance_flags[cfg.voice_mature_bd_flag] = "1"
    assert resolve_mature_voice(square, state, square_room) == "lewd"


def test_banned_lewd_cliches_exported():
    assert "member" in BANNED_LEWD_CLICHES
    assert "manhood" in BANNED_LEWD_CLICHES


def test_mature_combat_broadcast_line_for_observer():
    from world.mature_social import localized_broadcast_line

    mature = make_player(locale="en", content_rating="mature")
    teen = make_player(locale="en", content_rating="teen")
    mature_line = localized_broadcast_line(
        mature,
        "combat.victory_broadcast",
        mature_key="combat.victory_broadcast_1",
        name="Vy",
        target="Thug",
    )
    teen_line = localized_broadcast_line(
        teen,
        "combat.victory_broadcast",
        mature_key="combat.victory_broadcast_1",
        name="Vy",
        target="Thug",
    )
    assert "smear" in mature_line.lower() or "blood" in mature_line.lower()
    assert "dropped" in teen_line.lower()