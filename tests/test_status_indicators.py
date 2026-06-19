from client.meta_handlers import ClientViewState
from client.status_indicators import status_needs_animation, vitals_alert
from client.ui_format import format_hint_rows, format_status_markup
from client.output_prefix import SPINNER_FRAMES


def test_vitals_alert_low_hp():
    state = ClientViewState(hp="20/100")
    assert vitals_alert(state)


def test_status_needs_animation_in_combat():
    state = ClientViewState(in_combat=True)
    assert status_needs_animation(state)


def test_combat_hint_spins():
    state = ClientViewState(
        in_combat=True,
        combat_log="你擊中目標",
        combat_target="街頭暴徒",
        combat_npc_hp="12",
        combat_player_cd=30,
    )
    state.combat_cd_synced_at = __import__("time").monotonic()
    text = format_hint_rows(state, spinner_frame=2)
    assert SPINNER_FRAMES[2] in text
    assert "街頭暴徒" in text
    assert "P:30s" in text


def test_quest_hint_spins():
    state = ClientViewState(hint="追擊情報經紀人", quest="傳聞任務")
    text = format_hint_rows(state, spinner_frame=1)
    assert SPINNER_FRAMES[1] in text
    assert "追擊" in text


def test_status_hp_spins_in_combat():
    state = ClientViewState(hp="80/100", in_combat=True, room="小巷")
    text = format_status_markup(state, host="127.0.0.1", port=4000, spinner_frame=0)
    assert SPINNER_FRAMES[0] in text