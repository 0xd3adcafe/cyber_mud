from combat.actions import resolve_quickhack
from combat.encounter import start_encounter
from commands.registry import dispatch
from tests.conftest import make_player, make_state
from world.loader import load_world
from world.status_effects import EFFECT_BURN, EFFECT_BLIND


def test_world_loads_quickhacks():
    world = load_world()
    assert "overheat" in world.quickhacks
    assert world.quickhacks["synapse_burnout"].skill_req == "breach_protocol"


def test_overheat_applies_burn():
    player = make_player()
    player.skills = ["quickhack"]
    player.ram = 8
    state = make_state()
    state.npc_rooms["thug"] = "alley"
    player.room_id = "alley"
    encounter = start_encounter(state, player, "thug")
    result = resolve_quickhack(state, player, "overheat")
    assert result.lines
    assert encounter.npc_status.has(EFFECT_BURN)
    assert player.ram == 6


def test_reboot_optics_blinds_without_damage():
    player = make_player()
    player.skills = ["quickhack"]
    player.intelligence = 6
    player.ram = 8
    state = make_state()
    state.npc_rooms["thug"] = "alley"
    player.room_id = "alley"
    encounter = start_encounter(state, player, "thug")
    before_hp = encounter.npc_hp
    resolve_quickhack(state, player, "reboot_optics")
    assert encounter.npc_hp == before_hp
    assert encounter.npc_status.has(EFFECT_BLIND)


def test_synapse_requires_breach_protocol():
    player = make_player()
    player.skills = ["quickhack"]
    player.ram = 8
    state = make_state()
    state.npc_rooms["thug"] = "alley"
    player.room_id = "alley"
    start_encounter(state, player, "thug")
    result = resolve_quickhack(state, player, "synapse_burnout")
    assert any("未知" in line for line in result.lines)


def test_cyberpsychosis_reduces_damage():
    from combat.encounter import Encounter
    from world.cyberpsychosis import player_damage_multiplier

    player = make_player()
    player.humanity = 20
    assert player_damage_multiplier(player) < 1.0
    player.humanity = 80
    assert player_damage_multiplier(player) == 1.0


def test_quickhack_command_with_name():
    player = make_player(room_id="alley")
    player.skills = ["quickhack"]
    player.ram = 8
    player.body = 20
    state = make_state()
    state.npc_rooms["thug"] = "alley"
    dispatch("attack thug", player, state, [], [])
    from combat.encounter import encounter_for_player

    enc = encounter_for_player(state, player)
    assert enc is not None
    enc.player_cd = 0
    result = dispatch("quickhack short_circuit", player, state, [], [])
    text = "\n".join(result.lines)
    assert "短路" in text or "short" in text.lower()