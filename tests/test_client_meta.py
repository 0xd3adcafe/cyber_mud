from client.meta_handlers import (
    ClientViewState,
    active_prompt,
    apply_meta,
    classify_server_line,
    handle_panel_line,
    hint_text,
    is_local_command,
    is_netrun_exit_command,
    netrun_blocks_server_command,
    parse_local_command,
    reconnect_delay,
    status_text,
)


def test_apply_meta_updates_status():
    state = ClientViewState()
    apply_meta(state, "room", "霓虹廣場")
    apply_meta(state, "hp", "80/100")
    apply_meta(state, "weather", "酸雨")
    text = status_text(state, host="127.0.0.1", port=4000)
    assert "霓虹廣場" in text
    assert "80/100" in text
    assert "酸雨" in text


def test_panel_stream_lifecycle():
    state = ClientViewState()
    apply_meta(state, "ui_panel", "pda")
    handle_panel_line(state, "◈ PDA")
    apply_meta(state, "ui_panel_end", "1")
    assert state.sidebar_open
    assert state.sidebar_panel == "pda"
    assert state.sidebar_lines == ["◈ PDA"]


def test_combat_hint_priority():
    state = ClientViewState(combat_log="P:0 N:1", hint="任務提示")
    assert hint_text(state) == "P:0 N:1"


def test_local_commands():
    assert is_local_command("/reconnect")
    assert is_local_command("/prompt set %n>")
    assert not is_local_command("look")
    assert parse_local_command("/prompt set %h>") == ("prompt", "set %h>")


def test_classify_server_line():
    assert classify_server_line("@meta hp=10") == "meta"
    assert classify_server_line("@panel line") == "panel"
    assert classify_server_line("@ui {}") == "ui"
    assert classify_server_line("hello") == "text"


def test_reconnect_backoff():
    assert reconnect_delay(1) == 1.0
    assert reconnect_delay(2) == 2.0
    assert reconnect_delay(5) == 16.0


def test_netrun_prompt_and_blocking():
    state = ClientViewState()
    apply_meta(state, "net_shell", "1")
    apply_meta(state, "net_prompt", "ghost@net> ")
    assert active_prompt(state) == "ghost@net> "
    assert netrun_blocks_server_command("look")
    assert not netrun_blocks_server_command("exit")
    assert is_netrun_exit_command("/exit")
    assert not is_local_command("/exit")
    assert is_local_command("/reconnect")