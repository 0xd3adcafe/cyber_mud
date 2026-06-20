from __future__ import annotations

from combat.actions import resolve_quickhack
from combat.strike import resolve_player_attack
from combat.encounter import encounter_for_player
from commands.registry import dispatch
from tests.conftest import make_player, make_state


def test_cyber_arm_bonus_damage():
    player = make_player(room_id="alley", name="V")
    player.body = 3
    player.cyberware["arms"] = "cyber_arm_v1"
    state = make_state()
    dispatch("attack thug", player, state, [], [])
    encounter = encounter_for_player(state, player)
    assert encounter is not None
    assert encounter.npc_hp == 26


def test_breach_protocol_boosts_quickhack():
    player = make_player(room_id="alley", name="V")
    player.intelligence = 5
    player.skills.extend(["quickhack", "breach_protocol"])
    player.ram = 8
    state = make_state()
    dispatch("attack thug", player, state, [], [])
    encounter = encounter_for_player(state, player)
    assert encounter is not None
    encounter.player_cd = 0
    before_hp = encounter.npc_hp
    resolve_quickhack(state, player)
    assert encounter.npc_hp == before_hp - 10