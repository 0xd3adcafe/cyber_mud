from __future__ import annotations

from world.state import WorldState


def weather_for_room(state: WorldState, room_id: str) -> str:
    room = state.world.room(room_id)
    if room is None or not room.district:
        return ""
    return state.weather.get(room.district, "")


def period_for_room(state: WorldState) -> str:
    return state.clock.period_id(state.time_config)


def combat_damage_multiplier(weather_type: str, period_id: str = "") -> float:
    mult = 1.0
    if weather_type == "acid_rain":
        mult *= 0.9
    if period_id == "night":
        mult *= 0.95
    elif period_id == "dawn":
        mult *= 1.05
    return mult


def flee_chance_bonus(weather_type: str, period_id: str = "") -> float:
    bonus = 0.0
    if weather_type == "fog":
        bonus += 0.10
    if period_id == "night":
        bonus += 0.05
    return bonus


def movement_fail_chance(weather_type: str, period_id: str = "") -> float:
    chance = 0.0
    if weather_type == "acid_rain":
        chance += 0.10
    if weather_type == "fog":
        chance += 0.05
    if period_id in {"dusk", "night"}:
        chance += 0.03
    elif period_id in {"morning", "noon"}:
        chance = max(0.0, chance - 0.02)
    return chance


def apply_damage_modifier(state: WorldState, room_id: str, damage: int) -> int:
    weather = weather_for_room(state, room_id)
    period = period_for_room(state)
    multiplier = combat_damage_multiplier(weather, period)
    return max(1, int(damage * multiplier))


def modified_flee_chance(base_chance: float, state: WorldState, room_id: str) -> float:
    weather = weather_for_room(state, room_id)
    period = period_for_room(state)
    bonus = flee_chance_bonus(weather, period)
    return min(0.95, base_chance + bonus)


def movement_blocked_by_weather(state: WorldState, room_id: str, *, roll: float) -> bool:
    weather = weather_for_room(state, room_id)
    period = period_for_room(state)
    return roll < movement_fail_chance(weather, period)


def rest_weather_multiplier(
    weather_type: str,
    *,
    outdoor: bool,
    table: dict[str, float] | None = None,
) -> float:
    if not outdoor:
        return 1.0
    return (table or {}).get(weather_type, 1.0)


def rest_period_multiplier(
    period_id: str,
    *,
    indoor: bool,
    table: dict[str, float] | None = None,
) -> float:
    mult = (table or {}).get(period_id, 1.0)
    if indoor and period_id == "night":
        mult *= 1.1
    return mult


def rest_unsafe_district_penalty(
    district_safety: int,
    min_safety: int,
    *,
    outdoor: bool,
) -> float:
    if not outdoor or district_safety >= min_safety:
        return 1.0
    return 0.5