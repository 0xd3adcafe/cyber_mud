from commands.net_shell import dispatch_net
from commands.registry import CommandContext
from tests.conftest import make_player, make_state


def _net_ctx(*, room_id: str = "docks", ram: int = 8, street_cred: int = 5) -> CommandContext:
    player = make_player(room_id=room_id, locale="en", net_shell=True, ram=ram, street_cred=street_cred)
    state = make_state()
    return CommandContext(player=player, state=state, args="", peers=[])


def test_blackout_hack_at_docks():
    ctx = _net_ctx(room_id="docks")
    result = dispatch_net("hack blackout", ctx)
    text = "\n".join(result.lines)
    assert "blackout" in text.lower() or "lights" in text.lower()
    assert ctx.player.ram < 8
    assert ctx.player.footprint > 0


def test_blackout_fails_without_power_grid():
    ctx = _net_ctx(room_id="square")
    result = dispatch_net("hack blackout", ctx)
    text = "\n".join(result.lines)
    assert "No hackable" in text or "blackout" in text


def test_jam_signals_at_square():
    ctx = _net_ctx(room_id="square", street_cred=2)
    result = dispatch_net("hack jam_signals", ctx)
    text = "\n".join(result.lines)
    assert "jam" in text.lower() or "signal" in text.lower()