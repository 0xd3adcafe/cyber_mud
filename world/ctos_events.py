from __future__ import annotations

from shared.i18n import t
from world.scheduler import ScheduledTask
from world.state import WorldState
from world.tick_events import TickEvent

CTOS_EVENT_DURATION_TICKS = 6

HACK_DISTRICT_EVENTS: dict[str, str] = {
    "blackout": "blackout",
    "jam_signals": "traffic_lock",
}

CTOS_ON_KINDS = frozenset({"ctos_blackout_on", "ctos_traffic_lock_on"})
CTOS_OFF_KINDS = frozenset({"ctos_blackout_off", "ctos_traffic_lock_off"})
CTOS_SCHEDULER_KINDS = CTOS_ON_KINDS | CTOS_OFF_KINDS


def district_label(locale: str, district_id: str) -> str:
    if not district_id:
        return ""
    key = f"district.label.{district_id}"
    label = t(locale, key)
    return label if label != key else district_id


def district_event_active(state: WorldState, district: str, event_id: str) -> bool:
    if not district:
        return False
    return event_id in state.district_events.get(district, [])


def activate_district_event(state: WorldState, district: str, event_id: str) -> bool:
    if not district or not event_id:
        return False
    events = state.district_events.setdefault(district, [])
    if event_id in events:
        return False
    events.append(event_id)
    return True


def deactivate_district_event(state: WorldState, district: str, event_id: str) -> bool:
    events = state.district_events.get(district, [])
    if event_id not in events:
        return False
    events.remove(event_id)
    if not events:
        state.district_events.pop(district, None)
    return True


def _schedule_restore(state: WorldState, district: str, event_id: str) -> None:
    state.scheduler.schedule_once(
        state.tick_count + CTOS_EVENT_DURATION_TICKS,
        f"ctos_{event_id}_off",
        payload={"district": district, "event": event_id},
    )


def _schedule_district_broadcast(state: WorldState, district: str, event_id: str) -> None:
    state.scheduler.schedule_once(
        state.tick_count + 1,
        f"ctos_{event_id}_on",
        payload={"district": district, "event": event_id},
    )


def begin_district_event_from_hack(state: WorldState, hack_id: str, district: str) -> None:
    event_id = HACK_DISTRICT_EVENTS.get(hack_id)
    if not event_id or not district:
        return
    activate_district_event(state, district, event_id)
    _schedule_restore(state, district, event_id)
    _schedule_district_broadcast(state, district, event_id)


def process_ctos_scheduler_task(state: WorldState, task: ScheduledTask) -> list[TickEvent]:
    district = task.payload.get("district", "")
    if not district:
        return []

    if task.kind in CTOS_ON_KINDS:
        event_id = task.kind.removeprefix("ctos_").removesuffix("_on")
        if not district_event_active(state, district, event_id):
            activate_district_event(state, district, event_id)
        return [
            TickEvent(
                kind="ctos_district",
                district=district,
                message_key=f"scheduler.{task.kind}",
                message_kwargs={"district": district},
            )
        ]

    if task.kind in CTOS_OFF_KINDS:
        event_id = task.payload.get("event") or task.kind.removeprefix("ctos_").removesuffix("_off")
        if not deactivate_district_event(state, district, event_id):
            return []
        return [
            TickEvent(
                kind="ctos_district",
                district=district,
                message_key=f"scheduler.{task.kind}",
                message_kwargs={"district": district},
            )
        ]

    return []