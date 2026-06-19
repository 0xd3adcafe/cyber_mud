from world.clock import WorldClock, load_time_config


def test_clock_advance_rolls_day():
    clock = WorldClock(day=1, hour=23, minute=55)
    clock.advance(10)
    assert clock.day == 2
    assert clock.hour == 0
    assert clock.minute == 5


def test_period_night_at_start():
    config = load_time_config()
    clock = WorldClock(hour=20, minute=0)
    assert clock.period_id(config) == "night"


def test_period_morning():
    config = load_time_config()
    clock = WorldClock(hour=9, minute=0)
    assert clock.period_id(config) == "morning"


def test_format_clock_zh():
    config = load_time_config()
    clock = WorldClock(day=3, hour=8, minute=5)
    assert clock.format_clock("zh") == "第3天 08:05"
    assert clock.format_period("zh", config) == "上午"