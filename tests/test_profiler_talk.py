from commands.registry import dispatch
from tests.conftest import make_player, make_state


def _ctx(*, locale: str = "en"):
    player = make_player(room_id="square", locale=locale)
    state = make_state()
    state.npc_rooms["broker"] = "square"
    state.npc_rooms["corp_scout"] = "square"
    return player, state


def test_talk_broker_gambling_debt_branch():
    player, state = _ctx()
    dispatch("scan broker", player, state, [], [])
    result = dispatch("talk broker", player, state, [], [])
    text = "\n".join(result.lines)
    assert "gambling" in text.lower() or "tables" in text.lower()
    assert player.quest_flags.get("profiler_broker_tip") == "1"


def test_talk_broker_bribe_consumes_mod_chip():
    player, state = _ctx()
    player.inventory.append("mod_chip")
    dispatch("scan broker", player, state, [], [])
    result = dispatch("talk broker", player, state, [], [])
    text = "\n".join(result.lines)
    assert "mod_chip" not in player.inventory
    assert "chip" in text.lower() or "ledger" in text.lower()


def test_talk_corp_scout_corp_access_branch():
    player, state = _ctx()
    dispatch("scan corp_scout", player, state, [], [])
    result = dispatch("talk corp_scout", player, state, [], [])
    text = "\n".join(result.lines)
    assert "relay" in text.lower() or "patrol" in text.lower()
    assert player.quest_flags.get("profiler_scout_relay") == "1"


def test_talk_without_profile_skips_branch():
    player, state = _ctx()
    result = dispatch("talk broker", player, state, [], [])
    assert "profiler_broker_tip" not in player.quest_flags
    assert result.lines