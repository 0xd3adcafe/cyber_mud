from __future__ import annotations

import time

from client.link_status import classify_link, format_link_status_bar, make_link_snapshot


def test_classify_ok_when_connected():
    snap = make_link_snapshot(
        connected=True,
        reconnecting=False,
        command_pending=False,
        panel_fetching=False,
        last_recv_at=time.monotonic(),
    )
    assert classify_link(snap) == "ok"


def test_classify_waiting_on_pending_command():
    snap = make_link_snapshot(
        connected=True,
        reconnecting=False,
        command_pending=True,
        panel_fetching=False,
        last_send_at=time.monotonic(),
    )
    assert classify_link(snap) == "waiting"


def test_classify_slow_on_high_rtt():
    snap = make_link_snapshot(
        connected=True,
        reconnecting=False,
        command_pending=True,
        panel_fetching=False,
        last_rtt_ms=1200.0,
        last_send_at=time.monotonic(),
    )
    assert classify_link(snap) == "slow"


def test_format_link_status_waiting():
    snap = make_link_snapshot(
        connected=True,
        reconnecting=False,
        command_pending=True,
        panel_fetching=False,
        last_send_at=time.monotonic() - 0.5,
    )
    text = format_link_status_bar(snap)
    assert "等待伺服器" in text


def test_format_link_status_reconnecting():
    snap = make_link_snapshot(
        connected=False,
        reconnecting=True,
        command_pending=False,
        panel_fetching=False,
    )
    text = format_link_status_bar(snap)
    assert "重連中" in text