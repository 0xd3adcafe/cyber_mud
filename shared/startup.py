from __future__ import annotations

import time
from dataclasses import dataclass, field

from shared.i18n import t
from shared.server_locale import server_locale


@dataclass
class StartupReport:
    steps: list[tuple[str, float]] = field(default_factory=list)
    _t0: float = field(default_factory=time.perf_counter, repr=False)
    locale: str = field(default_factory=server_locale)

    def measure(self, name: str) -> _StartupStep:
        return _StartupStep(self, name)

    @property
    def total_ms(self) -> float:
        return (time.perf_counter() - self._t0) * 1000

    def _step_label(self, name: str) -> str:
        key = f"server.startup.steps.{name}"
        label = t(self.locale, key)
        return label if label != key else name

    def format_console(self, *, title: str | None = None) -> str:
        heading = title or t(self.locale, "server.startup.title")
        lines = [f"{heading}:"]
        for name, ms in self.steps:
            lines.append(f"  {self._step_label(name)}: {ms:.0f}ms")
        lines.append(t(self.locale, "server.startup.total", total=f"{self.total_ms:.0f}"))
        return "\n".join(lines)

    def format_status(self) -> str:
        if not self.steps:
            return t(self.locale, "server.startup.complete", total=f"{self.total_ms:.0f}")
        parts = [f"{self._step_label(name)} {ms:.0f}ms" for name, ms in self.steps]
        return t(
            self.locale,
            "server.startup.complete_steps",
            steps=" · ".join(parts),
            total=f"{self.total_ms:.0f}",
        )

    def format_brief(self) -> str:
        return t(self.locale, "server.startup.brief", total=f"{self.total_ms:.0f}")


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