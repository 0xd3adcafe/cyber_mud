from commands.net_shell import dispatch_net
from commands.registry import CommandContext, dispatch
from tests.conftest import make_player, make_state
from world.quests import accept_quest, quest_is_done


def _setup(state):
    state.npc_rooms["broker"] = "square"
    state.npc_rooms["corp_scout"] = "square"


def test_profiler_contract_stages():
    player = make_player(room_id="square", locale="en", street_cred=5, ram=8)
    player.quest_flags["broker_rumor"] = "done"
    state = make_state()
    _setup(state)

    accept_quest(player, state, "profiler_contract", "en")
    assert player.active_quest == "profiler_contract"
    assert player.quest_flags["profiler_contract"] == "started"

    dispatch("scan corp_scout", player, state, [], [])
    assert player.quest_flags["profiler_contract"] == "stage_2"

    ctx = CommandContext(player=player, state=state, args="", peers=[])
    player.net_shell = True
    dispatch_net("hack jam_signals", ctx)
    assert player.quest_flags["profiler_contract"] == "stage_3"

    result = dispatch("talk broker", player, state, [], [])
    assert player.quest_flags["profiler_contract"] == "ready"
    assert any("progress" in line.lower() or "objective" in line.lower() for line in result.lines)

    result = dispatch("talk broker", player, state, [], [])
    assert quest_is_done(player, "profiler_contract")
    assert any("complete" in line.lower() for line in result.lines)