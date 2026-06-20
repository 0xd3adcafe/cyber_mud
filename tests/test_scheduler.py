from __future__ import annotations

from commands.registry import dispatch
from persistence.world_state import load_world_state, save_world_state
from tests.conftest import make_player, make_state
from world.scheduler import Scheduler, minutes_to_ticks
from world.tick import process_tick


def test_minutes_to_ticks_rounds_up():
    assert minutes_to_ticks(30, minutes_per_tick=10) == 3
    assert minutes_to_ticks(1, minutes_per_tick=10) == 1


def test_scheduler_once_and_interval():
    once_sched = Scheduler()
    once_sched.schedule_once(5, "ping", player_name="Vy", payload={"n": "1"})
    assert once_sched.process(3) == []
    assert [task.kind for task in once_sched.process(5)] == ["ping"]

    interval_sched = Scheduler()
    interval_sched.schedule_interval(4, 2, "tick", player_name="Vy")
    assert interval_sched.process(3) == []
    assert [task.kind for task in interval_sched.process(4)] == ["tick"]
    assert [task.kind for task in interval_sched.process(6)] == ["tick"]
    assert interval_sched.process(7) == []


def test_scheduler_cancel():
    sched = Scheduler()
    task_id = sched.schedule_once(10, "implant_side_effect", player_name="Vy")
    assert sched.cancel(task_id)
    assert sched.process(10) == []


def test_scheduler_persists_in_world_state(world_state_path):
    state = make_state()
    state.scheduler.schedule_once(42, "implant_side_effect", player_name="Vy", payload={"label": "Kerenzikov"})
    save_world_state(state)

    loaded = load_world_state(state.world, state.time_config)
    assert len(loaded.scheduler.tasks) == 1
    assert loaded.scheduler.tasks[0].fire_at_tick == 42


def test_implant_install_schedules_side_effect():
    player = make_player(room_id="ripper_clinic", named=True, name="Chrome")
    state = make_state()
    player.inventory.append("kerenzikov_kit")
    before = state.tick_count
    dispatch("install kerenzikov_kit", player, state, [], [])
    tasks = [task for task in state.scheduler.tasks if task.kind == "implant_side_effect"]
    assert len(tasks) == 1
    assert tasks[0].player_name == "Chrome"
    assert tasks[0].fire_at_tick == before + minutes_to_ticks(30, minutes_per_tick=state.time_config.minutes_per_tick)


def test_scheduler_fires_implant_side_effect_event():
    player = make_player(named=True, name="Chrome", locale="en")
    state = make_state()
    state.tick_count = 9
    state.scheduler.schedule_once(10, "implant_side_effect", player_name="Chrome", payload={"label": "Kerenzikov"})
    result = process_tick(state, state.time_config, players=[player])
    kinds = [event.kind for event in result.events]
    assert "scheduler_msg" in kinds
    event = next(event for event in result.events if event.kind == "scheduler_msg")
    assert event.message_key == "scheduler.implant_side_effect"
    assert event.message_kwargs.get("label") == "Kerenzikov"