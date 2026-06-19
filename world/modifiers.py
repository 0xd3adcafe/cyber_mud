from __future__ import annotations

from world.state import WorldState


def weather_for_room(state: WorldState, room_id: str) -> str:
    room = state.world.room(room_id)
    if room is None or not room.district:
        return ""
    return state.weather.get(room.district, "")


def combat_damage_multiplier(weather_type: str) -> float:
    if weather_type == "acid_rain":
        return 0.9
    return 1.0


def flee_chance_bonus(weather_type: str) -> float:
    if weather_type == "fog":
        return 0.10
    return 0.0


def movement_fail_chance(weather_type: str) -> float:
    if weather_type == "acid_rain":
        return 0.10
    if weather_type == "fog":
        return 0.05
    return 0.0


def apply_damage_modifier(state: WorldState, room_id: str, damage: int) -> int:
    weather = weather_for_room(state, room_id)
    multiplier = combat_damage_multiplier(weather)
    return max(1, int(damage * multiplier))


def modified_flee_chance(base_chance: float, state: WorldState, room_id: str) -> float:
    weather = weather_for_room(state, room_id)
    bonus = flee_chance_bonus(weather)
    return min(0.95, base_chance + bonus)


def movement_blocked_by_weather(state: WorldState, room_id: str, *, roll: float) -> bool:
    weather = weather_for_room(state, room_id)
    return roll < movement_fail_chance(weather)