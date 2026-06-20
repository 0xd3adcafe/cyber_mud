from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass
class AuthRateLimiter:
    max_failures: int = 5
    window_seconds: float = 60.0
    block_seconds: float = 300.0
    _failures: list[float] = field(default_factory=list)
    _blocked_until: float = 0.0

    def is_blocked(self, *, now: float | None = None) -> bool:
        current = time.monotonic() if now is None else now
        return current < self._blocked_until

    def record_failure(self, *, now: float | None = None) -> None:
        current = time.monotonic() if now is None else now
        if self.is_blocked(now=current):
            return
        cutoff = current - self.window_seconds
        self._failures = [stamp for stamp in self._failures if stamp >= cutoff]
        self._failures.append(current)
        if len(self._failures) >= self.max_failures:
            self._blocked_until = current + self.block_seconds
            self._failures.clear()

    def reset(self) -> None:
        self._failures.clear()
        self._blocked_until = 0.0