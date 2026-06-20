from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from shared.i18n import t
from world.world import Room

GRID_ROOM_RE = re.compile(r"^([a-z_]+)_(\d+)_(\d+)$")

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "districts.yaml"

_CONFIG: dict[str, "DistrictProfile"] | None = None


@dataclass
class DistrictProfile:
    safety: int = 2
    atmosphere: str = ""
    patrol_density: float = 0.6
    aggro_bonus: float = 0.0
    weather_bias: dict[str, int] = field(default_factory=dict)
    entry_blocked_factions: list[str] = field(default_factory=list)
    allied_factions: list[str] = field(default_factory=list)


def load_district_profiles(path: Path | None = None) -> dict[str, DistrictProfile]:
    global _CONFIG
    if _CONFIG is not None and path is None:
        return _CONFIG
    raw = yaml.safe_load((path or DATA_PATH).read_text(encoding="utf-8")) or {}
    profiles: dict[str, DistrictProfile] = {}
    for district_id, data in (raw.get("districts") or {}).items():
        profiles[str(district_id)] = DistrictProfile(
            safety=int(data.get("safety", 2)),
            atmosphere=str(data.get("atmosphere", "")),
            patrol_density=float(data.get("patrol_density", 0.6)),
            aggro_bonus=float(data.get("aggro_bonus", 0.0)),
            weather_bias={str(k): int(v) for k, v in (data.get("weather_bias") or {}).items()},
            entry_blocked_factions=[str(x) for x in (data.get("entry_blocked_factions") or [])],
            allied_factions=[str(x) for x in (data.get("allied_factions") or [])],
        )
    if path is None:
        _CONFIG = profiles
    return profiles


def district_profile(district_id: str) -> DistrictProfile:
    return load_district_profiles().get(district_id, DistrictProfile())


def district_safety(room: Room | None) -> int:
    if room is None or not room.district:
        return 2
    return district_profile(room.district).safety


def is_grid_cell(room: Room | None) -> bool:
    if room is None:
        return False
    return bool(GRID_ROOM_RE.match(room.id))


def atmosphere_line(room: Room | None, locale: str) -> str | None:
    if room is None or not room.district:
        return None
    atmosphere = district_profile(room.district).atmosphere
    if not atmosphere:
        return None
    key = f"district.atmosphere.{atmosphere}"
    line = t(locale, key)
    return line if line != key else None


def grid_flavor_line(room: Room | None, locale: str) -> str | None:
    if not is_grid_cell(room) or not room.district:
        return None
    key = f"district.grid.{room.district}"
    line = t(locale, key)
    return line if line != key else None


def patrol_move_chance(base: float, room: Room | None, *, period_id: str = "") -> float:
    if room is None or not room.district:
        chance = base
    else:
        density = district_profile(room.district).patrol_density
        chance = base * density
    if period_id:
        from world.schedule import patrol_period_multiplier

        chance *= patrol_period_multiplier(period_id)
    return min(0.95, chance)


def aggro_chance_bonus(room: Room | None) -> float:
    if room is None or not room.district:
        return 0.0
    return district_profile(room.district).aggro_bonus


def weighted_weather_choice(pool: list[str], district_id: str, current: str) -> str:
    profile = district_profile(district_id)
    if not profile.weather_bias:
        choices = [w for w in pool if w != current] or pool
        import random

        return random.choice(choices)
    import random

    weights = []
    for weather in pool:
        if weather == current and len(pool) > 1:
            continue
        weights.append((weather, profile.weather_bias.get(weather, 1)))
    if not weights:
        return current
    total = sum(weight for _, weight in weights)
    roll = random.uniform(0, total)
    acc = 0.0
    for weather, weight in weights:
        acc += weight
        if roll <= acc:
            return weather
    return weights[-1][0]


def entry_refusal(player, room: Room | None, locale: str) -> list[str] | None:
    if room is None or not room.district or not player.faction:
        return None
    profile = district_profile(room.district)
    if player.faction not in profile.entry_blocked_factions:
        return None
    if player.faction in profile.allied_factions:
        return None
    if player.reputation >= 15:
        return None
    return [t(locale, "faction.entry_denied", district=room.district)]