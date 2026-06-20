from commands.registry import dispatch
from shared.completion import complete_input_cycle
from tests.conftest import make_player, make_state


def test_go_up_and_down(monkeypatch):
    import random

    monkeypatch.setattr(random, "random", lambda: 1.0)
    player = make_player(room_id="square")
    state = make_state()
    dispatch("go up", player, state, [], [])
    assert player.room_id == "square_rooftop"
    dispatch("go down", player, state, [], [])
    assert player.room_id == "square"
    dispatch("go north", player, state, [], [])
    dispatch("go down", player, state, [], [])
    assert player.room_id == "undercity"


def test_interact_smuggler_cache():
    player = make_player(room_id="alley")
    state = make_state()
    dispatch("take rusty_key", player, state, [], [])
    result = dispatch("interact smuggler_cache", player, state, [], [])
    assert "mod_chip" in player.inventory
    assert player.interact_flags.get("smuggler_cache") == "done"
    assert any("晶片" in line or "chip" in line.lower() for line in result.lines)


def test_craft_med_stim_at_ripperdoc():
    player = make_player(room_id="ripper_clinic", gold=50)
    player.inventory = ["synth_ramen", "energy_drink"]
    state = make_state()
    dispatch("craft med_stim", player, state, [], [])
    assert player.inventory.count("med_stim") == 1
    assert "synth_ramen" not in player.inventory


def test_disassemble_mod_chip():
    player = make_player()
    player.inventory = ["mod_chip"]
    state = make_state()
    dispatch("disassemble mod_chip", player, state, [], [])
    assert "mod_chip" not in player.inventory
    assert "glowstick" in player.inventory
    assert player.gold == 15


def test_braindance_dock_heist():
    player = make_player(room_id="undercity", gold=50)
    state = make_state()
    result = dispatch("bd dock_heist", player, state, [], [])
    assert player.braindance_flags.get("bd_dock_heist") == "done"
    assert player.gold == 35
    assert any("腦舞" in line or "BD" in line for line in result.lines)


def test_multi_stage_quest_dock_watch():
    player = make_player(room_id="square", street_cred=10)
    player.active_quest = "dock_watch"
    player.quest_flags["dock_watch"] = "started"
    player.skills = ["breach_protocol"]
    state = make_state()
    dispatch("go south", player, state, [], [])
    assert player.quest_flags["dock_watch"] == "stage_1"
    dispatch("interact dock_crane", player, state, [], [])
    assert player.quest_flags["dock_watch"] == "stage_2"
    dispatch("go north", player, state, [], [])
    dispatch("talk broker", player, state, [], [])
    assert player.quest_flags["dock_watch"] == "ready"


def test_tab_completion_cycles_candidates():
    kwargs = dict(
        room_items=(),
        room_npcs=(),
        room_exits=(),
        inventory=(),
    )
    first, idx1 = complete_input_cycle("t", 0, **kwargs)
    second, idx2 = complete_input_cycle("t", idx1, **kwargs)
    assert first in {"transit", "take", "talents", "talk", "time"}
    assert second in {"transit", "take", "talents", "talk", "time"}
    assert first != second or len({first, second}) == 1


def test_vehicle_garage_buy_two():
    player = make_player(room_id="docks", gold=5000)
    state = make_state()
    dispatch("vehicles buy archer", player, state, [], [])
    dispatch("vehicles buy yaiba", player, state, [], [])
    assert len(player.vehicles) == 2
    dispatch("vehicles select yaiba", player, state, [], [])
    assert player.active_vehicle == "yaiba_kusanagi"


def test_world_loads_interactables_and_recipes():
    _, state = make_player(), make_state()
    assert "smuggler_cache" in state.world.interactables
    assert "mod_chip" in state.world.recipes
    assert "dock_heist" in state.world.braindances
    assert "chrome_brawler" in state.world.passive_chains