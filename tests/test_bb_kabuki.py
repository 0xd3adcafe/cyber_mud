from __future__ import annotations

from commands.registry import dispatch
from tests.conftest import make_player, make_state
from world.romance import load_romance_profiles, profile_for_npc


def test_kabuki_bb_npcs_exist():
    state = make_state()
    for nid in (
        "kabuki_fixer_amara",
        "kabuki_streamer_jenna",
        "kabuki_artist_selene",
        "kabuki_brat_neon",
    ):
        assert state.world.npc(nid) is not None


def test_jenna_lewd_romance_profile():
    profiles = load_romance_profiles()
    profile = profile_for_npc(profiles, "kabuki_streamer_jenna")
    assert profile is not None
    assert profile.voice_override == "lewd"


def test_bouncer_cred_tier_talk():
    player = make_player(locale="en", room_id="kabuki_vip", content_rating="mature", street_cred=16)
    state = make_state()
    state.npc_rooms["kabuki_bouncer"] = "kabuki_vip"
    result = dispatch("talk kabuki_bouncer", player, state, [], [])
    joined = "\n".join(result.lines).lower()
    assert "cred" in joined or "regular" in joined or "vip" in joined