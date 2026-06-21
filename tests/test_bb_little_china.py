from __future__ import annotations

from tests.conftest import make_state
from world.romance import load_romance_profiles, profile_for_npc


def test_little_china_bb_npcs():
    state = make_state()
    for nid in (
        "little_china_host_misato",
        "little_china_sister_sayaka",
        "shrine_net_shaman_nari",
    ):
        assert state.world.npc(nid) is not None


def test_sayaka_lewd_profile():
    profiles = load_romance_profiles()
    profile = profile_for_npc(profiles, "little_china_sister_sayaka")
    assert profile is not None
    assert profile.voice_default == "lewd" or profile.voice_override == "lewd"