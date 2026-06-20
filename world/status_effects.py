from __future__ import annotations

from dataclasses import dataclass, field

EFFECT_BURN = "burn"
EFFECT_SHOCK = "shock"
EFFECT_BLIND = "blind"
EFFECT_BLEED = "bleed"
EFFECT_POISON = "poison"
EFFECT_OVERHEAT = "overheat"

PLAYER_STATUS_EFFECTS = frozenset(
    {EFFECT_BLEED, EFFECT_POISON, EFFECT_OVERHEAT}
)


@dataclass
class StatusEffectState:
    effects: dict[str, int] = field(default_factory=dict)

    def apply(self, effect: str, duration: int) -> None:
        if duration <= 0 or not effect:
            return
        self.effects[effect] = max(self.effects.get(effect, 0), duration)

    def has(self, effect: str) -> bool:
        return self.effects.get(effect, 0) > 0

    def tick(self) -> list[str]:
        expired: list[str] = []
        for effect in list(self.effects):
            self.effects[effect] -= 1
            if self.effects[effect] <= 0:
                del self.effects[effect]
                expired.append(effect)
        return expired

    def clear(self) -> None:
        self.effects.clear()

    def labels(self, locale: str) -> list[str]:
        from shared.i18n import t

        return [t(locale, f"status.{key}") for key in sorted(self.effects)]


def burn_tick_damage(intelligence: int) -> int:
    return max(1, intelligence // 2)


def poison_tick_damage(body: int) -> int:
    return max(1, body // 5)


def player_overheat_damage_multiplier(player_status: dict[str, int]) -> float:
    if player_status.get(EFFECT_OVERHEAT, 0) > 0:
        return 0.85
    return 1.0


def cure_player_status(player_status: dict[str, int], effect: str) -> bool:
    if effect in player_status:
        del player_status[effect]
        return True
    return False


def npc_damage_multiplier(status: StatusEffectState) -> float:
    if status.has(EFFECT_BLIND):
        return 0.5
    return 1.0


def npc_skip_attack(status: StatusEffectState) -> bool:
    if status.has(EFFECT_SHOCK):
        status.effects[EFFECT_SHOCK] = 0
        if EFFECT_SHOCK in status.effects:
            del status.effects[EFFECT_SHOCK]
        return True
    return False