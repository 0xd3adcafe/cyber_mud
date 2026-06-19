from __future__ import annotations

from entities.player import Player

PERIOD_REGEN_MULT: dict[str, float] = {
    "dawn": 1.5,
    "morning": 1.25,
    "noon": 1.0,
    "afternoon": 1.0,
    "dusk": 0.75,
    "night": 0.5,
}


def calc_hp_regen(player: Player, period_id: str) -> int:
    """Return HP restored this tick (0 if no regen applies)."""
    if player.in_combat or player.hp >= player.max_hp:
        return 0
    base = max(1, player.body // 2)
    cool_bonus = player.cool // 10
    mult = PERIOD_REGEN_MULT.get(period_id, 1.0)
    amount = int((base + cool_bonus) * mult)
    if amount <= 0:
        return 0
    return min(amount, player.max_hp - player.hp)


def apply_hp_regen(player: Player, period_id: str) -> int:
    amount = calc_hp_regen(player, period_id)
    if amount > 0:
        player.hp += amount
    return amount