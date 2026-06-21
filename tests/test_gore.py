from __future__ import annotations

from combat.gore import maybe_gore_crit, maybe_gore_kill
from combat.strike import resolve_player_strike
from tests.conftest import make_player, make_state


def test_gore_lines_only_when_mature():
    teen = make_player(locale="en", content_rating="teen")
    mature = make_player(locale="en", content_rating="mature")
    assert maybe_gore_crit(mature, "en", target="Thug", damage=20, npc_max_hp=30) is not None
    assert maybe_gore_crit(teen, "en", target="Thug", damage=20, npc_max_hp=30) is None
    assert maybe_gore_kill(mature, "en", target="Thug") is not None
    assert maybe_gore_kill(teen, "en", target="Thug") is None


def test_mature_kill_adds_gore_line():
    from combat.actions import _finish_victory
    from combat.encounter import start_encounter

    state = make_state()
    player = make_player(locale="en", room_id="alley", content_rating="mature")
    state.npc_rooms["thug"] = "alley"
    encounter = start_encounter(state, player, "thug")
    encounter.npc_hp = 1
    result = _finish_victory(state, player, encounter, [])
    joined = "\n".join(result.lines).lower()
    gore_markers = (
        "blood",
        "crunch",
        "neon",
        "fold",
        "wet",
        "silence",
        "twitch",
        "optics",
        "chest",
        "spark",
        "coolant",
    )
    assert any(marker in joined for marker in gore_markers)