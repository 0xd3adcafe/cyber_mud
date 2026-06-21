from tests.conftest import make_player, make_state
from world.net_session import tick_net_trace, trace_rate_per_tick, TRACE_MAX
from world.tick import process_tick


def test_trace_accumulates_in_netrun():
    player = make_player(locale="en", net_shell=True, net_connected_node="terminal")
    state = make_state()
    before = player.net_trace
    tick_net_trace(player, state)
    assert player.net_trace > before


def test_footprint_increases_trace_rate():
    player = make_player(locale="en", net_shell=True, footprint=70, net_connected_node="terminal")
    state = make_state()
    rate_high = trace_rate_per_tick(player, state)
    player.footprint = 0
    rate_low = trace_rate_per_tick(player, state)
    assert rate_high >= rate_low


def test_full_trace_forces_disconnect():
    player = make_player(locale="en", net_shell=True, net_trace=TRACE_MAX - 1, net_connected_node="terminal")
    state = make_state()
    lines = tick_net_trace(player, state)
    assert not player.net_shell
    assert lines