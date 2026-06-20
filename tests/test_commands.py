from commands.registry import dispatch
from tests.conftest import make_player, make_state


def _ctx(room_id: str = "square"):
    return make_player(room_id=room_id), make_state()


def test_look_square():
    player, state = _ctx()
    result = dispatch("look", player, state, [], [])
    assert any("霓虹廣場" in line for line in result.lines)


def test_go_north(monkeypatch):
    import random

    monkeypatch.setattr(random, "random", lambda: 1.0)
    player, state = _ctx()
    result = dispatch("go north", player, state, [], [])
    assert player.room_id == "alley"
    assert result.moved


def test_alias_l():
    player, state = _ctx()
    result = dispatch("l", player, state, [], [])
    assert any("霓虹廣場" in line for line in result.lines)


def test_look_item_on_ground():
    player, state = _ctx()
    result = dispatch("look knife", player, state, [], [])
    text = "\n".join(result.lines)
    assert "戰術折刀" in text or "Tactical Knife" in text
    assert "傷害" in text or "Damage" in text
    assert "地上" in text or "ground" in text


def test_look_npc_in_room():
    player, state = _ctx()
    result = dispatch("look broker", player, state, [], [])
    text = "\n".join(result.lines)
    assert "情報經紀人" in text or "Info Broker" in text
    assert "50/50" in text
    assert "敵意" in text or "Hostile" in text


def test_look_equipped_weapon():
    player, state = _ctx()
    player.inventory = ["knife"]
    dispatch("equip knife", player, state, [], [])
    result = dispatch("look knife", player, state, [], [])
    text = "\n".join(result.lines)
    assert "武器" in text or "weapon" in text.lower()


def test_look_equipment_panel():
    player, state = _ctx()
    player.inventory = ["knife", "jacket"]
    dispatch("equip knife", player, state, [], [])
    dispatch("equip jacket", player, state, [], [])
    result = dispatch("look equipment", player, state, [], [])
    text = "\n".join(result.lines)
    assert "戰術折刀" in text or "Tactical Knife" in text
    assert "防彈夾克" in text or "Armored Jacket" in text


def test_look_missing_target():
    player, state = _ctx()
    result = dispatch("look phantom", player, state, [], [])
    assert any("phantom" in line for line in result.lines)


def test_look_npc_combat_hp():
    from combat.encounter import start_encounter

    player, state = _ctx(room_id="alley")
    start_encounter(state, player, "thug")
    result = dispatch("look thug", player, state, [], [])
    text = "\n".join(result.lines)
    assert "交戰中" in text or "in combat" in text
    assert "30/30" in text