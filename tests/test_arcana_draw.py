from __future__ import annotations

from commands.registry import dispatch
from tests.conftest import make_player, make_state
from world.arcana import MAJOR_ARCANA, PERIOD_FLAG, arcana_on_cooldown


def test_arcana_draw_and_period_cooldown():
    player = make_player(locale="en", room_id="shrine", content_rating="mature")
    state = make_state()
    period = state.clock.period_id(state.time_config)

    result = dispatch("interact shrine_arcana_spread", player, state, [], [])
    assert any(
        word in "\n".join(result.lines).lower()
        for word in ("neon", "beginnings", "fool", "magician", "arcana", "spread")
    )
    assert player.interact_flags[PERIOD_FLAG] == period
    assert arcana_on_cooldown(player, state)

    again = dispatch("interact shrine_arcana_spread", player, state, [], [])
    assert any("period" in line.lower() or "shift" in line.lower() for line in again.lines)


def test_arcana_three_card_spread():
    player = make_player(locale="en", room_id="shrine")
    state = make_state()
    state.clock.hour = 8
    result = dispatch("interact shrine_arcana_spread three", player, state, [], [])
    joined = "\n".join(result.lines).lower()
    assert "three" in joined or "spread" in joined or "三" in joined


def test_lovers_unlocks_idol_flag():
    player = make_player(locale="en", room_id="shrine")
    state = make_state()
    from unittest.mock import patch
    from world import arcana as arcana_mod

    with patch.object(arcana_mod.random, "choice", return_value="lovers"):
        with patch.object(arcana_mod.random, "sample", return_value=["lovers", "star", "moon"]):
            lines = arcana_mod.perform_arcana_draw(player, state, "en", spread=1)
    assert lines
    assert player.quest_flags.get("arcana_unlock_idol_blackmail") == "1"


def test_major_arcana_count():
    assert len(MAJOR_ARCANA) == 22