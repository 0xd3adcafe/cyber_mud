from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from shared.i18n import t

TIME_PATH = Path(__file__).resolve().parent.parent / "data" / "time.yaml"


@dataclass
class TimeConfig:
    tick_interval_seconds: int = 30
    minutes_per_tick: int = 10
    start_day: int = 1
    start_hour: int = 20
    start_minute: int = 0
    periods: dict[str, dict[str, int]] | None = None

    def __post_init__(self) -> None:
        if self.periods is None:
            self.periods = {
                "dawn": {"start": 5, "end": 7},
                "morning": {"start": 7, "end": 12},
                "noon": {"start": 12, "end": 13},
                "afternoon": {"start": 13, "end": 18},
                "dusk": {"start": 18, "end": 20},
                "night": {"start": 20, "end": 5},
            }


@dataclass
class WorldClock:
    day: int = 1
    hour: int = 20
    minute: int = 0

    def advance(self, minutes: int) -> None:
        self.minute += minutes
        while self.minute >= 60:
            self.minute -= 60
            self.hour += 1
        while self.hour >= 24:
            self.hour -= 24
            self.day += 1

    def period_id(self, config: TimeConfig) -> str:
        for period_id, bounds in config.periods.items():
            start = int(bounds["start"])
            end = int(bounds["end"])
            if start <= end:
                if start <= self.hour < end:
                    return period_id
            elif self.hour >= start or self.hour < end:
                return period_id
        return "night"

    def format_clock(self, locale: str) -> str:
        return t(locale, "time.clock", day=self.day, hour=f"{self.hour:02d}", minute=f"{self.minute:02d}")

    def format_period(self, locale: str, config: TimeConfig) -> str:
        return t(locale, f"periods.{self.period_id(config)}")

    def to_dict(self) -> dict:
        return {"day": self.day, "hour": self.hour, "minute": self.minute}

    @classmethod
    def from_dict(cls, data: dict) -> WorldClock:
        return cls(
            day=int(data.get("day", 1)),
            hour=int(data.get("hour", 20)),
            minute=int(data.get("minute", 0)),
        )


_TIME_CONFIG_CACHE: TimeConfig | None = None


def clear_time_config_cache() -> None:
    global _TIME_CONFIG_CACHE
    _TIME_CONFIG_CACHE = None


def load_time_config(path: Path | None = None) -> TimeConfig:
    global _TIME_CONFIG_CACHE
    if path is not None:
        return _load_time_config_from_path(path)
    if _TIME_CONFIG_CACHE is not None:
        return _TIME_CONFIG_CACHE
    config = _load_time_config_from_path(TIME_PATH)
    _TIME_CONFIG_CACHE = config
    return config


def _load_time_config_from_path(src: Path) -> TimeConfig:
    with src.open(encoding="utf-8") as fh:
        raw = yaml.safe_load(fh) or {}
    periods = {
        str(k): {"start": int(v["start"]), "end": int(v["end"])}
        for k, v in (raw.get("periods") or {}).items()
    }
    return TimeConfig(
        tick_interval_seconds=int(raw.get("tick_interval_seconds", 30)),
        minutes_per_tick=int(raw.get("minutes_per_tick", 10)),
        start_day=int(raw.get("start_day", 1)),
        start_hour=int(raw.get("start_hour", 20)),
        start_minute=int(raw.get("start_minute", 0)),
        periods=periods,
    )


def default_clock(config: TimeConfig) -> WorldClock:
    return WorldClock(day=config.start_day, hour=config.start_hour, minute=config.start_minute)