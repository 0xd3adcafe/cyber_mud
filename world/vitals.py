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


def calc_hp_regen(player: Player, period_id: str, *, state=None) -> int:
    """Return HP restored this tick (0 if no regen applies)."""
    if player.in_combat or player.hp >= player.max_hp:
        return 0
    base = max(1, player.body // 2)
    cool_bonus = player.cool // 10
    mult = PERIOD_REGEN_MULT.get(period_id, 1.0)
    amount = int((base + cool_bonus) * mult)
    if amount <= 0:
        return 0
    if state is not None and player.posture != "standing":
        from world.life import posture_hp_mult, rest_environment_mult

        posture_mult = posture_hp_mult(player)
        if posture_mult <= 0:
            return 0
        env_mult = rest_environment_mult(player, state, period_id)
        amount = int(amount * posture_mult * env_mult)
        if amount <= 0:
            return 0
    return min(amount, player.max_hp - player.hp)


def apply_hp_regen(player: Player, period_id: str, *, state=None) -> int:
    amount = calc_hp_regen(player, period_id, state=state)
    if amount > 0:
        player.hp += amount
    return amount


def apply_ram_regen(player: Player, period_id: str, *, state=None) -> int:
    if player.in_combat or player.ram >= player.max_ram or player.posture == "standing":
        return 0
    from world.life import posture_ram_regen, rest_environment_mult

    base = posture_ram_regen(player)
    if base <= 0:
        return 0
    if state is not None:
        env = rest_environment_mult(player, state, period_id)
        base = max(1, int(base * env)) if env > 1 else base
    amount = min(base, player.max_ram - player.ram)
    if amount > 0:
        player.ram += amount
    return amount