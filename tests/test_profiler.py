from commands.registry import dispatch
from persistence.save import player_from_dict, player_to_dict
from tests.conftest import make_player, make_state
from world.profiler import is_profiled, load_profiler_profiles, profiler_entry


def test_profiler_yaml_loads():
    profiles = load_profiler_profiles()
    assert "broker" in profiles
    broker = profiles["broker"]
    assert broker.income_band == "mid"
    assert "gambling_debt" in broker.traits


def test_scan_npc_profiles_broker():
    player = make_player(room_id="square", locale="en")
    state = make_state()
    result = dispatch("scan broker", player, state, [], [])
    text = "\n".join(result.lines)
    assert "Profiler" in text
    assert "gambling debt" in text
    assert is_profiled(player, "broker")


def test_scan_npc_cached_header():
    player = make_player(room_id="square", locale="en", profiled_npcs=["broker"])
    state = make_state()
    result = dispatch("scan broker", player, state, [], [])
    text = "\n".join(result.lines)
    assert "cached" in text.lower()
    assert player.profiled_npcs.count("broker") == 1


def test_scan_npc_no_profile_data():
    player = make_player(room_id="tutorial_combat", locale="en")
    state = make_state()
    result = dispatch("scan sparring_bot", player, state, [], [])
    text = "\n".join(result.lines)
    assert "No profiler data" in text
    assert not is_profiled(player, "sparring_bot")


def test_profiled_npcs_persist_roundtrip():
    player = make_player(locale="en", profiled_npcs=["broker", "thug"])
    restored = player_from_dict(player_to_dict(player))
    assert restored.profiled_npcs == ["broker", "thug"]


def test_profiler_entry_missing():
    assert profiler_entry("nonexistent_npc_xyz") is None