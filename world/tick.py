from __future__ import annotations

from world.clock import TimeConfig
from world.state import WorldState


def process_tick(state: WorldState, config: TimeConfig) -> bool:
    """Advance world clock. Returns True if time changed."""
    before = (state.clock.day, state.clock.hour, state.clock.minute)
    state.clock.advance(config.minutes_per_tick)
    after = (state.clock.day, state.clock.hour, state.clock.minute)
    return before != after