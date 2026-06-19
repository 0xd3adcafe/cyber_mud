from __future__ import annotations

from commands.registry import dispatch
from tests.conftest import make_player, make_state


def test_look_npc_shows_equipment():
    player = make_player(room_id="alley")
    state = make_state()

    result = dispatch("look thug", player, state, [], [])
    text = "\n".join(result.lines)

    assert "穿戴" in text
    assert "戰術折刀" in text or "knife" in text.lower()


def test_npc_equipment_drops_on_death():
    player = make_player(room_id="alley", name="V")
    player.body = 50
    player.equipment["weapon_secondary"] = "knife"
    state = make_state()

    dispatch("attack thug", player, state, [], [])
    corpse = state.corpses["thug_corpse"]

    assert "mod_chip" in corpse.loot
    assert "knife" in corpse.loot