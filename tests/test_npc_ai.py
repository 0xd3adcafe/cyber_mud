from unittest.mock import patch

from world.npc_ai import NPC_AI_EVERY, factions_rival, load_npc_ai_config, process_npc_ai
from world.tick import process_tick
from tests.conftest import make_state


def test_factions_rival_maelstrom_arasaka():
    cfg = load_npc_ai_config()
    assert factions_rival(cfg, "maelstrom", "arasaka")
    assert not factions_rival(cfg, "maelstrom", "maelstrom")


def test_rival_npc_fight_in_same_room():
    state = make_state()
    state.npc_rooms["thug"] = "alley"
    state.npc_rooms["corp_scout"] = "alley"
    state.tick_count = NPC_AI_EVERY
    events = process_npc_ai(state, roll=0.1)
    fight_events = [e for e in events if e.kind == "npc_ai_fight"]
    assert fight_events
    assert state.npc_vitals.get("corp_scout", 35) < 35 or any(e.kind == "npc_ai_defeat" for e in events)


def test_trade_social_when_broker_with_thug():
    state = make_state()
    state.npc_rooms["broker"] = "alley"
    state.npc_rooms["thug"] = "alley"
    state.tick_count = NPC_AI_EVERY
    with patch("world.npc_ai.factions_rival", return_value=False):
        events = process_npc_ai(state, roll=0.2)
    social = [e for e in events if e.kind == "npc_ai_social"]
    assert social
    assert social[0].message_key == "npc.ai.msg.trade"


def test_hunt_rival_moves_toward_enemy():
    state = make_state()
    state.npc_rooms["thug"] = "square"
    state.npc_rooms["corp_scout"] = "alley"
    state.tick_count = NPC_AI_EVERY
    events = process_npc_ai(state, roll=0.1)
    enter = [e for e in events if e.kind == "npc_enter" and e.npc_id == "thug"]
    assert enter
    assert state.npc_rooms["thug"] == "alley"


def test_npc_ai_integrated_in_world_tick():
    state = make_state()
    state.npc_rooms["thug"] = "alley"
    state.npc_rooms["corp_scout"] = "alley"
    state.tick_count = NPC_AI_EVERY - 1
    with patch("world.npc_ai.random.random", return_value=0.05):
        result = process_tick(state, state.time_config)
    kinds = {e.kind for e in result.events}
    assert "npc_ai_fight" in kinds or "npc_ai_defeat" in kinds


def test_corp_scout_loaded_with_faction():
    state = make_state()
    scout = state.world.npc("corp_scout")
    assert scout is not None
    assert scout.faction == "arasaka"
    assert scout.motivation == "guard"