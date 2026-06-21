from __future__ import annotations

from commands.registry import dispatch
from tests.conftest import make_player, make_state
from world.romance import load_romance_profiles, profile_for_npc


def _flat_setup(state):
    for nid in ("watson_flatmate_rin", "watson_flatmate_yoojin", "watson_flatmate_eunbi"):
        state.npc_rooms[nid] = "watson_flat"


def test_flatmate_peer_talk():
    player = make_player(locale="en", room_id="watson_flat", content_rating="mature")
    state = make_state()
    _flat_setup(state)
    result = dispatch("talk watson_flatmate_rin", player, state, [], [])
    joined = "\n".join(result.lines).lower()
    assert "yoojin" in joined or "eunbi" in joined or "flat" in joined


def test_rin_scene_requires_home():
    player = make_player(locale="en", room_id="watson_flat", content_rating="mature")
    player.romance_flags["watson_flatmate_rin"] = "3"
    state = make_state()
    _flat_setup(state)
    result = dispatch("scene watson_flatmate_rin", player, state, [], [])
    assert any("home" in line.lower() or "rent" in line.lower() for line in result.lines)

    player.home_room_id = "watson_flat"
    result = dispatch("scene watson_flatmate_rin", player, state, [], [])
    joined = "\n".join(result.lines).lower()
    assert "fade" in joined or "curtain" in joined or "heat" in joined or "簾" in joined


def test_rin_scene_requires_home_profile():
    profiles = load_romance_profiles()
    profile = profile_for_npc(profiles, "watson_flatmate_rin")
    assert profile is not None
    assert profile.scene_requires_home == "watson_flat"