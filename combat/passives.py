from __future__ import annotations

from entities.player import Player
from world.cyberware import has_implant


def bonus_attack_damage(player: Player) -> int:
    bonus = 0
    if has_implant(player, "cyber_arm_v1"):
        bonus += 1
    if has_implant(player, "mantis_blades"):
        bonus += 2
    if "blade_flow" in player.skills:
        bonus += 1
    return bonus


def quickhack_damage_multiplier(player: Player) -> float:
    if "breach_protocol" in player.skills:
        return 1.10
    return 1.0