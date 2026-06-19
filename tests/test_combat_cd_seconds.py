from combat.strike import resolve_player_attack
from combat.encounter import ATTACK_CD, cd_ticks_to_seconds, combat_meta, encounter_for_player
from tests.conftest import make_player, make_state


def test_player_cd_message_uses_seconds():
    player = make_player(room_id="alley", named=True)
    state = make_state()
    from combat.encounter import start_encounter

    encounter = start_encounter(state, player, "thug")
    encounter.player_cd = ATTACK_CD
    result = resolve_player_attack(state, player, target="thug")
    assert any("3s" in line for line in result.lines)


def test_combat_meta_cd_in_seconds():
    player = make_player(room_id="alley", named=True)
    state = make_state()
    from combat.encounter import start_encounter

    start_encounter(state, player, "thug")
    encounter = encounter_for_player(state, player)
    assert encounter is not None
    encounter.player_cd = 2
    encounter.npc_cd = 1
    meta = combat_meta(state, player)
    assert meta["combat_cd"] == f"P:{cd_ticks_to_seconds(state, 2)} N:{cd_ticks_to_seconds(state, 1)}"