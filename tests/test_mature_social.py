from __future__ import annotations

import pytest

from commands.registry import dispatch
from shared.mature_paths import mature_content_available
from tests.conftest import make_player, make_state
from world.romance import load_romance_profiles, profile_for_npc

pytestmark = pytest.mark.skipif(
    not mature_content_available(),
    reason="mature content pack missing (git submodule data/mature)",
)


def test_scene_stage_gate():
    state = make_state()
    player = make_player(locale="en", room_id="kabuki_lounge", content_rating="mature")
    state.npc_rooms["kabuki_host"] = "kabuki_lounge"
    profiles = load_romance_profiles()
    profile = profile_for_npc(profiles, "kabuki_host")
    assert profile is not None

    blocked = dispatch("scene kabuki_host", player, state, [], [player])
    assert any("stage" in line.lower() for line in blocked.lines)

    player.romance_flags[profile.id] = str(profile.scene_min_stage)
    ok = dispatch("scene kabuki_host", player, state, [], [player])
    joined = "\n".join(ok.lines).lower()
    assert "booth" in joined or "scanner" in joined or "privacy" in joined or "field" in joined


def test_whisper_does_not_advance_affinity():
    state = make_state()
    player = make_player(locale="en", room_id="kabuki_lounge", content_rating="mature")
    state.npc_rooms["kabuki_host"] = "kabuki_lounge"
    profiles = load_romance_profiles()
    profile = profile_for_npc(profiles, "kabuki_host")
    assert profile is not None

    dispatch("flirt kabuki_host", player, state, [], [player])
    affinity_after_flirt = int(player.romance_flags.get(profile.id, "0"))

    dispatch("whisper kabuki_host meet me after close", player, state, [], [player])
    assert int(player.romance_flags.get(profile.id, "0")) == affinity_after_flirt


def test_whisper_to_npc():
    state = make_state()
    player = make_player(locale="en", room_id="kabuki_lounge", content_rating="mature", name="Vy")
    state.npc_rooms["kabuki_host"] = "kabuki_lounge"
    result = dispatch("whisper kabuki_host keep a booth open", player, state, [], [player])
    joined = "\n".join(result.lines).lower()
    assert "booth" in joined or "murmur" in joined or "whisper" in joined