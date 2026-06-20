from __future__ import annotations

from textual.dom import DOMNode
from textual.pilot import Pilot


async def settle_layout(pilot: Pilot, *, rounds: int = 4, delay: float = 0.02) -> None:
    for _ in range(rounds):
        await pilot.pause(delay=delay)


async def wait_for_class(
    widget: DOMNode,
    class_name: str,
    pilot: Pilot,
    *,
    present: bool = True,
    attempts: int = 10,
    delay: float = 0.02,
) -> None:
    for _ in range(attempts):
        await settle_layout(pilot, rounds=1, delay=delay)
        if (class_name in widget.classes) == present:
            return
    assert (class_name in widget.classes) == present


def scroll_covers_log(scroll: DOMNode, log_wrap: DOMNode, *, margin: int = 8) -> bool:
    return scroll.region.width >= log_wrap.region.width - margin