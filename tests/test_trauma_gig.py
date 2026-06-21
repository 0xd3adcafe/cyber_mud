from __future__ import annotations

from commands.registry import dispatch
from tests.conftest import make_player, make_state
from world.quests import accept_quest, advance_quest_on_defeat, advance_quest_on_visit, quest_is_done
from world.status_effects import EFFECT_BLEED
from world.trauma import apply_player_bleed


def _setup(state):
    state.npc_rooms["trauma_team_medic"] = "ripper_clinic"
    state.npc_rooms["ripperdoc_triage"] = "ripper_clinic"
    state.npc_rooms["thug"] = "alley"


def test_trauma_run_accept_and_stages():
    player = make_player(locale="en", room_id="ripper_clinic", content_rating="mature")
    state = make_state()
    _setup(state)

    lines = accept_quest(player, state, "trauma_run", "en")
    assert lines
    assert player.active_quest == "trauma_run"

    visit_lines = advance_quest_on_visit(player, state, "alley", "en")
    assert visit_lines
    assert player.quest_flags["trauma_run"] == "stage_1"

    defeat_lines = advance_quest_on_defeat(player, state, "thug", "en")
    assert defeat_lines
    assert player.quest_flags["trauma_run"] == "stage_2"

    clinic_lines = advance_quest_on_visit(player, state, "ripper_clinic", "en")
    assert clinic_lines
    assert player.quest_flags["trauma_run"] == "stage_3"


def test_trauma_run_complete_via_triage_talk():
    player = make_player(locale="en", room_id="ripper_clinic", content_rating="mature")
    state = make_state()
    _setup(state)

    accept_quest(player, state, "trauma_run", "en")
    player.quest_flags["trauma_run"] = "stage_3"

    result = dispatch("talk ripperdoc_triage", player, state, [], [])
    assert player.quest_flags["trauma_run"] == "ready"

    result = dispatch("talk ripperdoc_triage", player, state, [], [])
    assert quest_is_done(player, "trauma_run")
    assert "trauma_kit" in player.inventory
    assert any("complete" in line.lower() or "Gig" in line for line in result.lines)


def test_scene_trauma_intimate_requires_quest():
    player = make_player(locale="en", room_id="ripper_clinic", content_rating="mature")
    player.romance_flags["trauma_team_medic"] = "3"
    state = make_state()
    _setup(state)

    result = dispatch("scene trauma_team_medic", player, state, [], [])
    assert any("trauma_run" in line or "gig" in line.lower() for line in result.lines)


def test_scene_trauma_intimate_after_quest_done():
    player = make_player(locale="en", room_id="ripper_clinic", content_rating="mature")
    player.romance_flags["trauma_team_medic"] = "3"
    player.quest_flags["trauma_run"] = "done"
    state = make_state()
    _setup(state)

    result = dispatch("scene trauma_team_medic", player, state, [], [])
    joined = "\n".join(result.lines).lower()
    assert "chart" in joined or "curtain" in joined or "病歷" in joined


def test_bleed_at_clinic_treated_on_go():
    player = make_player(locale="en", room_id="square", content_rating="mature")
    apply_player_bleed(player)
    state = make_state()

    result = dispatch("go west", player, state, [], [])
    assert player.room_id == "ripper_clinic"
    assert EFFECT_BLEED not in player.player_status
    joined = "\n".join(result.lines).lower()
    assert "trauma" in joined or "stabil" in joined or "ripperdoc" in joined