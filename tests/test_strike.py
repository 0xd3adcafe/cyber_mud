from __future__ import annotations

from unittest.mock import patch

from combat.encounter import encounter_for_player
from combat.strike import resolve_player_strike
from commands.registry import dispatch
from tests.conftest import make_player, make_state


def _fighter(**kwargs):
    player = make_player(room_id="alley", name="V", **kwargs)
    player.body = 5
    player.reflex = 4
    player.cool = 6
    return player, make_state()


def test_shoot_requires_gun():
    player, state = _fighter()
    player.equipment["weapon_secondary"] = "knife"
    result = dispatch("shoot thug", player, state, [], [])
    assert not player.in_combat
    assert any("遠程武器" in line for line in result.lines)


def test_shoot_with_pistol():
    player, state = _fighter()
    player.equipment["weapon_secondary"] = "liberty_pistol"
    dispatch("shoot thug", player, state, [], [])
    encounter = encounter_for_player(state, player)
    assert encounter is not None
    assert encounter.npc_hp == 15


def test_slash_with_knife():
    player, state = _fighter()
    player.equipment["weapon_secondary"] = "knife"
    dispatch("slash thug", player, state, [], [])
    encounter = encounter_for_player(state, player)
    assert encounter is not None
    assert encounter.npc_hp == 21


def test_bash_with_pipe():
    player, state = _fighter()
    player.equipment["weapon_secondary"] = "pipe"
    dispatch("bash thug", player, state, [], [])
    encounter = encounter_for_player(state, player)
    assert encounter is not None
    assert encounter.npc_hp == 21


def test_punch_requires_unarmed():
    player, state = _fighter()
    player.equipment["weapon_secondary"] = "knife"
    result = dispatch("punch thug", player, state, [], [])
    assert any("空手" in line for line in result.lines)


def test_punch_unarmed():
    player, state = _fighter()
    dispatch("punch thug", player, state, [], [])
    encounter = encounter_for_player(state, player)
    assert encounter is not None
    assert encounter.npc_hp == 23


def test_backstab_success(monkeypatch):
    player, state = _fighter()
    player.equipment["weapon_secondary"] = "knife"
    monkeypatch.setattr("combat.styles.random.random", lambda: 0.0)
    dispatch("backstab thug", player, state, [], [])
    encounter = encounter_for_player(state, player)
    assert encounter is not None
    assert encounter.npc_hp == 6


def test_attack_defaults_to_shoot_with_gun():
    player, state = _fighter()
    player.equipment["weapon_secondary"] = "liberty_pistol"
    result = dispatch("attack thug", player, state, [], [])
    assert any("槍" in line or "瞄準" in line for line in result.lines)


def test_attack_explicit_slash():
    player, state = _fighter()
    player.equipment["weapon_secondary"] = "liberty_pistol"
    result = dispatch("attack slash thug", player, state, [], [])
    assert any("刀械" in line for line in result.lines)


def test_shoot_has_longer_cooldown():
    player, state = _fighter()
    player.equipment["weapon_secondary"] = "liberty_pistol"
    dispatch("shoot thug", player, state, [], [])
    encounter = encounter_for_player(state, player)
    assert encounter is not None
    assert encounter.player_cd == 2


def test_resolve_backstab_fail_message(monkeypatch):
    player, state = _fighter()
    player.equipment["weapon_secondary"] = "knife"
    dispatch("attack thug", player, state, [], [])
    encounter = encounter_for_player(state, player)
    assert encounter is not None
    encounter.player_cd = 0
    with patch("combat.styles.random.random", return_value=1.0):
        result = resolve_player_strike(state, player, style="backstab")
    assert any("背刺失敗" in line for line in result.lines)