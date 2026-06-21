from unittest.mock import patch

from commands.registry import dispatch
from combat.actions import resolve_flee
from combat.encounter import start_encounter
from tests.conftest import make_player, make_state
from world.npc_ai import patrol_is_jammed, try_jam_npc
from world.tick import PATROL_EVERY, process_tick


def _setup(state):
    state.npc_rooms["broker"] = "square"
    state.npc_rooms["corp_scout"] = "square"
    state.npc_rooms["thug"] = "alley"


def test_jam_skips_patrol_movement():
    state = make_state()
    _setup(state)
    broker = state.world.npc("broker")
    assert broker is not None
    saved_schedule = dict(broker.schedule)
    broker.schedule.clear()
    try:
        player = make_player(room_id="square", locale="en", ram=4)
        lines = try_jam_npc(player, state, "broker", "en")
        assert lines
        assert patrol_is_jammed(state, "broker")

        state.tick_count = PATROL_EVERY - 1
        with patch("world.tick.random.random", return_value=0.1):
            process_tick(state, state.time_config)
        assert state.npc_rooms["broker"] == "square"
    finally:
        broker.schedule.clear()
        broker.schedule.update(saved_schedule)


def test_jam_security_detail_shorter_effect():
    player = make_player(room_id="square", locale="en", ram=4, profiled_npcs=["corp_scout"])
    state = make_state()
    _setup(state)
    try_jam_npc(player, state, "corp_scout", "en")
    assert state.npc_patrol_jam.get("corp_scout") == 1


def test_distract_suppresses_aggro_chase():
    player = make_player(room_id="alley", locale="en")
    state = make_state()
    _setup(state)
    start_encounter(state, player, "thug")
    player.in_combat = True

    dispatch("distract thug", player, state, [], [])
    assert state.npc_aggro_distract.get("thug", 0) > 0

    with patch("combat.encounter.random.random", return_value=1.0):
        result = resolve_flee(state, player)
    assert not player.chased_by_npc
    assert result.ended