from __future__ import annotations

import time

from shared.startup import StartupReport


def test_startup_report_measures_steps():
    report = StartupReport()
    with report.measure("alpha"):
        time.sleep(0.01)
    with report.measure("beta"):
        pass
    assert len(report.steps) == 2
    assert report.steps[0][0] == "alpha"
    assert report.steps[0][1] >= 5
    assert report.steps[1][0] == "beta"
    assert report.total_ms >= report.steps[0][1]


def test_startup_format_status():
    report = StartupReport()
    with report.measure("主題"):
        pass
    text = report.format_status()
    assert "啟動完成" in text
    assert "主題" in text
    assert "ms" in text


def test_startup_format_console():
    report = StartupReport()
    with report.measure("世界資料"):
        pass
    text = report.format_console(title="伺服器載入")
    assert "伺服器載入" in text
    assert "世界資料" in text
    assert "總計" in text


def test_create_game_returns_startup_report():
    from server.game import create_game

    game, report = create_game()
    assert game.state.world.rooms
    assert report.steps
    assert any(name == "世界資料" for name, _ in report.steps)