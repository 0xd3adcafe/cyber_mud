from __future__ import annotations

from combat.gore import maybe_gore_crit
from tests.conftest import make_player
from world.mature_voice import (
    mature_combat_line,
    resolve_mature_combat_voice,
    resolve_mature_voice,
)
from world.mature_social import random_mature_finish_line, random_mature_taunt_line
from world.status_effects import EFFECT_BLEED


def test_combat_voice_always_noir():
    player = make_player(locale="en", content_rating="mature", room_id="kabuki_vip")
    player.player_status[EFFECT_BLEED] = 3
    assert resolve_mature_combat_voice(player) == "noir"
    assert resolve_mature_voice(player, None, None) == "lewd"


def test_noir_combat_locale_resolves():
    line = mature_combat_line("en", "crit", variant=4, target="Thug", damage="18")
    assert line
    assert "subdermal" in line.lower() or "smartgun" in line.lower()


def test_taunt_finish_use_noir_combat_pools():
    taunt = random_mature_taunt_line("en", target="Thug")
    finish = random_mature_finish_line("en", target="Thug")
    assert taunt and "Thug" in taunt
    assert finish and "Thug" in finish
    assert "cunt" not in taunt.lower()


def test_gore_crit_uses_noir_pool():
    mature = make_player(locale="en", content_rating="mature")
    line = maybe_gore_crit(mature, "en", target="Thug", damage=20, npc_max_hp=30)
    assert line
    assert "Thug" in line