from __future__ import annotations

import time

from client.animated_log import AnimatedLogBuffer
from client.focus_block import (
    FocusTracker,
    flowing_accent_markup,
    render_focus_block,
    resolve_focus,
)
from client.meta_handlers import ClientViewState
from client.themes import focus_palette_for_theme
from tests.conftest import make_player, make_state


def test_resolve_focus_priority_combat_over_quest():
    state = ClientViewState(hint="前往小巷", quest="經紀人的傳聞", in_combat=True, combat_log="交戰")
    snap = resolve_focus(state, has_pending=False)
    assert snap is not None
    assert snap.kind == "combat"


def test_resolve_focus_command_over_quest():
    state = ClientViewState(hint="前往小巷", quest="經紀人的傳聞")
    snap = resolve_focus(state, has_pending=True, pending_text="look")
    assert snap is not None
    assert snap.kind == "command"
    assert "look" in snap.body


def test_focus_tracker_resets_on_phase_change():
    tracker = FocusTracker()
    t1 = tracker.sync("quest:a")
    time.sleep(0.05)
    t2 = tracker.sync("quest:a")
    assert t2 > t1
    tracker.sync("quest:b")
    t3 = tracker.sync("quest:b")
    assert t3 < 0.02


def test_flowing_accent_changes_with_frame():
    a = flowing_accent_markup(frame=0, theme_id="night_city")
    b = flowing_accent_markup(frame=3, theme_id="night_city")
    assert a != b


def test_focus_palette_varies_by_theme():
    night = focus_palette_for_theme("night_city")
    matrix = focus_palette_for_theme("matrix")
    assert night.quest_color != matrix.quest_color or night.quest_icon != matrix.quest_icon


def test_render_focus_block_quest_with_timer():
    player = make_player()
    player.active_quest = "broker_rumor"
    state = make_state()
    view = ClientViewState(
        hint="與情報經紀人交談",
        quest="經紀人的傳聞",
        locale="zh",
    )
    buffer = AnimatedLogBuffer()
    tracker = FocusTracker()
    rendered = render_focus_block(
        view,
        theme_id="tron",
        locale="zh",
        frame=2,
        buffer=buffer,
        tracker=tracker,
    )
    assert rendered is not None
    accent, content, status = rendered
    assert "▂" in accent or "▃" in accent
    assert "經紀人的傳聞" in content
    assert "追蹤中" in status
    assert "s" in status