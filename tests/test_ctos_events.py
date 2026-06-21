from __future__ import annotations

from commands.net_shell import dispatch_net
from commands.registry import CommandContext
from persistence.world_state import load_world_state, save_world_state
from tests.conftest import make_player, make_state
from world.ctos_events import CTOS_EVENT_DURATION_TICKS, district_event_active
from world.tick import process_tick


def _net_ctx(*, room_id: str = "docks", ram: int = 8, street_cred: int = 5) -> CommandContext:
    player = make_player(room_id=room_id, locale="en", net_shell=True, ram=ram, street_cred=street_cred)
    state = make_state()
    return CommandContext(player=player, state=state, args="", peers=[])


def test_blackout_hack_activates_district_event_and_schedules_restore():
    ctx = _net_ctx(room_id="docks")
    dispatch_net("hack blackout", ctx)
    assert district_event_active(ctx.state, "docks", "blackout")
    off_tasks = [task for task in ctx.state.scheduler.tasks if task.kind == "ctos_blackout_off"]
    on_tasks = [task for task in ctx.state.scheduler.tasks if task.kind == "ctos_blackout_on"]
    assert len(off_tasks) == 1
    assert len(on_tasks) == 1
    assert off_tasks[0].fire_at_tick == ctx.state.tick_count + CTOS_EVENT_DURATION_TICKS


def test_jam_signals_schedules_traffic_lock():
    ctx = _net_ctx(room_id="square", street_cred=2)
    dispatch_net("hack jam_signals", ctx)
    assert district_event_active(ctx.state, "watson", "traffic_lock")
    assert any(task.kind == "ctos_traffic_lock_off" for task in ctx.state.scheduler.tasks)


def test_blackout_restores_on_scheduled_tick():
    player = make_player(room_id="docks", locale="en")
    state = make_state()
    state.district_events["docks"] = ["blackout"]
    state.tick_count = 10
    state.scheduler.schedule_once(
        11,
        "ctos_blackout_off",
        payload={"district": "docks", "event": "blackout"},
    )
    result = process_tick(state, state.time_config, players=[player])
    assert not district_event_active(state, "docks", "blackout")
    event = next(item for item in result.events if item.kind == "ctos_district")
    assert event.message_key == "scheduler.ctos_blackout_off"
    assert event.district == "docks"


def test_district_events_persist_in_world_state(world_state_path):
    state = make_state()
    state.district_events["docks"] = ["blackout"]
    state.scheduler.schedule_once(20, "ctos_blackout_off", payload={"district": "docks", "event": "blackout"})
    save_world_state(state)

    loaded = load_world_state(state.world, state.time_config)
    assert loaded.district_events.get("docks") == ["blackout"]
    assert any(task.kind == "ctos_blackout_off" for task in loaded.scheduler.tasks)