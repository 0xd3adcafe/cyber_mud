from __future__ import annotations

import asyncio

from textual.widgets import Select

from client.app import CyberMudApp


def test_auth_select_mounts_with_login_value():
    async def _run() -> None:
        app = CyberMudApp("127.0.0.1", 4000)
        async with app.run_test(size=(80, 40)):
            select = app.query_one("#auth_mode", Select)
            assert select.value == "login"

    asyncio.run(_run())