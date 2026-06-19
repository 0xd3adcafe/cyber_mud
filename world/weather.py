from __future__ import annotations

import random
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from world.state import WorldState

WEATHER_PATH = Path(__file__).resolve().parent.parent / "data" / "weather.yaml"


@dataclass
class WeatherType:
    id: str
    name_zh: str = ""
    name_en: str = ""


@dataclass
class DistrictWeather:
    default: str
    types: list[str] = field(default_factory=list)


@dataclass
class WeatherConfig:
    tick_every: int = 6
    districts: dict[str, DistrictWeather] = field(default_factory=dict)
    types: dict[str, WeatherType] = field(default_factory=dict)


def load_weather_config(path: Path | None = None) -> WeatherConfig:
    src = path or WEATHER_PATH
    with src.open(encoding="utf-8") as fh:
        raw = yaml.safe_load(fh) or {}

    districts = {}
    for district_id, data in (raw.get("districts") or {}).items():
        districts[str(district_id)] = DistrictWeather(
            default=str(data.get("default", "clear")),
            types=[str(t) for t in (data.get("types") or [])],
        )

    types = {}
    for type_id, data in (raw.get("types") or {}).items():
        types[str(type_id)] = WeatherType(
            id=str(type_id),
            name_zh=str(data.get("name_zh", "")),
            name_en=str(data.get("name_en", "")),
        )

    return WeatherConfig(
        tick_every=int(raw.get("tick_every", 6)),
        districts=districts,
        types=types,
    )


def default_weather(config: WeatherConfig) -> dict[str, str]:
    return {district_id: info.default for district_id, info in config.districts.items()}


def get_district_weather(state: WorldState, district: str) -> str:
    return state.weather.get(district, "")


def set_district_weather(state: WorldState, district: str, weather_type: str) -> None:
    state.weather[district] = weather_type


def weather_label(weather_type: str, locale: str, config: WeatherConfig | None = None) -> str:
    cfg = config or load_weather_config()
    info = cfg.types.get(weather_type)
    if info is None:
        return weather_type
    return info.name_zh if locale == "zh" else (info.name_en or info.name_zh)


def maybe_tick_weather(state: WorldState, config: WeatherConfig) -> list[str]:
    """Maybe update district weather. Returns list of districts that changed."""
    if config.tick_every <= 0 or state.tick_count % config.tick_every != 0:
        return []

    changed: list[str] = []
    for district_id, info in config.districts.items():
        pool = info.types or list(config.types)
        if len(pool) < 2:
            continue
        current = state.weather.get(district_id, info.default)
        choices = [w for w in pool if w != current] or pool
        new_weather = random.choice(choices)
        if new_weather != current:
            state.weather[district_id] = new_weather
            changed.append(district_id)
    return changed