from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass
class StartupReport:
    steps: list[tuple[str, float]] = field(default_factory=list)
    _t0: float = field(default_factory=time.perf_counter, repr=False)

    def measure(self, name: str) -> _StartupStep:
        return _StartupStep(self, name)

    @property
    def total_ms(self) -> float:
        return (time.perf_counter() - self._t0) * 1000

    def format_console(self, *, title: str = "啟動摘要") -> str:
        lines = [f"{title}:"]
        for name, ms in self.steps:
            lines.append(f"  {name}: {ms:.0f}ms")
        lines.append(f"  總計: {self.total_ms:.0f}ms")
        return "\n".join(lines)

    def format_status(self) -> str:
        if not self.steps:
            return f"啟動完成 · {self.total_ms:.0f}ms"
        parts = [f"{name} {ms:.0f}ms" for name, ms in self.steps]
        return f"啟動完成 · {' · '.join(parts)} · 共 {self.total_ms:.0f}ms"

    def format_brief(self) -> str:
        return f"就緒 · {self.total_ms:.0f}ms"


class _StartupStep:
    def __init__(self, report: StartupReport, name: str) -> None:
        self._report = report
        self._name = name
        self._t0 = 0.0

    def __enter__(self) -> _StartupStep:
        self._t0 = time.perf_counter()
        return self

    def __exit__(self, *_exc: object) -> None:
        elapsed_ms = (time.perf_counter() - self._t0) * 1000
        self._report.steps.append((self._name, elapsed_ms))