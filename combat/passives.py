from __future__ import annotations

from entities.player import Player


def bonus_attack_damage(player: Player) -> int:
    bonus = 0
    if "cyber_arm_v1" in player.implants:
        bonus += 1
    return bonus


def quickhack_damage_multiplier(player: Player) -> float:
    if "breach_protocol" in player.skills:
        return 1.10
    return 1.0