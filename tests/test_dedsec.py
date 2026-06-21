from __future__ import annotations

from commands.help_cmd import HELP_CATEGORIES, format_help
from commands.registry import CommandContext, dispatch
from tests.conftest import make_player, make_state
from world.factions import npc_aggro_modifier
from world.footprint import add_footprint
from world.reactions import reputation_from_pledge


def test_dedsec_faction_in_world():
    state = make_state()
    assert "dedsec" in state.world.factions


def test_pledge_dedsec():
    player = make_player(locale="en")
    state = make_state()
    result = dispatch("pledge dedsec", player, state, [], [])
    assert player.faction == "dedsec"
    assert player.reputation == reputation_from_pledge("dedsec")
    assert any("DedSec" in line for line in result.lines)


def test_dedsec_reduces_footprint_gain():
    player = make_player(locale="en", faction="dedsec", footprint=0)
    state = make_state()
    add_footprint(player, 8, state, "en", reason="hack")
    assert player.footprint == 6


def test_dedsec_extra_aggro_in_corpo():
    player = make_player(faction="dedsec")
    state = make_state()
    room = state.world.room("corpo_plaza")
    assert room is not None
    mod = npc_aggro_modifier(player, room)
    assert mod >= 1


def test_help_has_city_os_category():
    player = make_player(locale="en")
    state = make_state()
    ctx = CommandContext(player=player, state=state, args="")
    lines = format_help(ctx)
    text = "\n".join(lines)
    assert "City OS" in text
    assert "scan" in text
    category_ids = [category_id for category_id, _ in HELP_CATEGORIES]
    assert "city_os" in category_ids


def test_tutorial_profiler_lesson_on_scan_netcoach():
    player = make_player(room_id="tutorial_net", locale="en")
    state = make_state()
    result = dispatch("scan netcoach", player, state, [], [])
    text = "\n".join(result.lines)
    assert "Profiler" in text
    assert player.quest_flags.get("tutorial_profiler") == "done"
    again = dispatch("scan netcoach", player, state, [], [])
    assert "Profiler drill" not in "\n".join(again.lines)