from __future__ import annotations

from dataclasses import dataclass, field
from uuid import uuid4


@dataclass
class ScheduledTask:
    id: str
    fire_at_tick: int
    kind: str
    player_name: str = ""
    payload: dict[str, str] = field(default_factory=dict)
    interval_ticks: int = 0

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "fire_at_tick": self.fire_at_tick,
            "kind": self.kind,
            "player_name": self.player_name,
            "payload": dict(self.payload),
            "interval_ticks": self.interval_ticks,
        }

    @classmethod
    def from_dict(cls, data: dict) -> ScheduledTask:
        return cls(
            id=str(data.get("id", "")),
            fire_at_tick=int(data.get("fire_at_tick", 0)),
            kind=str(data.get("kind", "")),
            player_name=str(data.get("player_name", "")),
            payload={str(k): str(v) for k, v in (data.get("payload") or {}).items()},
            interval_ticks=int(data.get("interval_ticks", 0)),
        )


@dataclass
class Scheduler:
    tasks: list[ScheduledTask] = field(default_factory=list)

    def schedule_once(
        self,
        fire_at_tick: int,
        kind: str,
        *,
        player_name: str = "",
        payload: dict[str, str] | None = None,
    ) -> str:
        task = ScheduledTask(
            id=uuid4().hex,
            fire_at_tick=max(0, fire_at_tick),
            kind=kind,
            player_name=player_name,
            payload=dict(payload or {}),
        )
        self.tasks.append(task)
        return task.id

    def schedule_interval(
        self,
        first_at_tick: int,
        interval_ticks: int,
        kind: str,
        *,
        player_name: str = "",
        payload: dict[str, str] | None = None,
    ) -> str:
        task = ScheduledTask(
            id=uuid4().hex,
            fire_at_tick=max(0, first_at_tick),
            kind=kind,
            player_name=player_name,
            payload=dict(payload or {}),
            interval_ticks=max(1, interval_ticks),
        )
        self.tasks.append(task)
        return task.id

    def cancel(self, task_id: str) -> bool:
        before = len(self.tasks)
        self.tasks = [task for task in self.tasks if task.id != task_id]
        return len(self.tasks) < before

    def cancel_kind(self, kind: str, *, player_name: str = "") -> int:
        before = len(self.tasks)
        self.tasks = [
            task
            for task in self.tasks
            if not (task.kind == kind and (not player_name or task.player_name == player_name))
        ]
        return before - len(self.tasks)

    def process(self, tick_count: int) -> list[ScheduledTask]:
        fired: list[ScheduledTask] = []
        remaining: list[ScheduledTask] = []
        for task in self.tasks:
            if task.fire_at_tick > tick_count:
                remaining.append(task)
                continue
            fired.append(task)
            if task.interval_ticks > 0:
                remaining.append(
                    ScheduledTask(
                        id=task.id,
                        fire_at_tick=tick_count + task.interval_ticks,
                        kind=task.kind,
                        player_name=task.player_name,
                        payload=dict(task.payload),
                        interval_ticks=task.interval_ticks,
                    )
                )
        self.tasks = remaining
        return fired

    def to_list(self) -> list[dict]:
        return [task.to_dict() for task in self.tasks]

    @classmethod
    def from_list(cls, data: list | None) -> Scheduler:
        tasks = [ScheduledTask.from_dict(entry) for entry in (data or []) if isinstance(entry, dict)]
        return cls(tasks=tasks)


def minutes_to_ticks(minutes: int, *, minutes_per_tick: int) -> int:
    if minutes <= 0:
        return 0
    step = max(1, minutes_per_tick)
    return max(1, (minutes + step - 1) // step)