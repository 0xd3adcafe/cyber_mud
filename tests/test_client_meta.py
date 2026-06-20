from client.meta_handlers import (
    ClientViewState,
    SidebarPanel,
    active_prompt,
    apply_meta,
    classify_server_line,
    format_sidebar_content,
    handle_panel_line,
    handle_ui_json,
    hint_text,
    is_local_command,
    is_netrun_exit_command,
    netrun_blocks_server_command,
    normalize_netrun_command,
    prepare_netrun_outbound,
    ordered_sidebar_stack,
    parse_local_command,
    panels_to_refresh_on_move,
    reconnect_delay,
    should_refresh_sidebar_on_room_change,
    status_text,
    toggle_sidebar_panel,
)


def test_apply_meta_combat_cd():
    import time

    state = ClientViewState()
    apply_meta(state, "combat", "1")
    apply_meta(state, "combat_cd", "P:60 N:30")
    assert state.in_combat
    assert state.combat_player_cd == 60
    assert state.combat_npc_cd == 30
    assert state.combat_cd_synced_at > 0
    apply_meta(state, "combat", "0")
    assert not state.in_combat
    assert state.combat_player_cd == 0


def test_apply_meta_completion_fields():
    state = ClientViewState()
    apply_meta(state, "complete_room_items", "glowstick,knife")
    apply_meta(state, "complete_npcs", "broker")
    apply_meta(state, "complete_exits", "north,south")
    apply_meta(state, "complete_inventory", "jacket")
    assert state.complete_room_items == ["glowstick", "knife"]
    assert state.complete_npcs == ["broker"]
    assert state.complete_exits == ["north", "south"]
    assert state.complete_inventory == ["jacket"]


def test_apply_meta_prompt_fields():
    state = ClientViewState()
    apply_meta(state, "name", "V")
    apply_meta(state, "prompt_template", "[%h] %n>")
    apply_meta(state, "level", "5")
    apply_meta(state, "xp", "10/200")
    apply_meta(state, "faction", "荒坂公司")
    assert state.player_name == "V"
    assert state.prompt_template == "[%h] %n>"
    assert state.level == "5"
    assert state.xp == "10/200"
    assert state.faction == "荒坂公司"


def test_apply_meta_auth():
    state = ClientViewState()
    apply_meta(state, "auth", "1")
    assert state.authenticated


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
    state = ClientViewState(sidebar_open=True)
    apply_meta(state, "ui_panel", "pda")
    handle_panel_line(state, "◈ PDA")
    apply_meta(state, "ui_panel_end", "1")
    assert state.sidebar_stack == ["pda"]
    assert state.sidebar_panels["pda"].lines == ["◈ PDA"]


def test_sidebar_stack_pda_and_map():
    state = ClientViewState(sidebar_open=True)
    apply_meta(state, "ui_panel", "pda")
    handle_ui_json(state, '{"panel":"pda","sections":[{"kind":"row","label":"HP","value":"100/100"}]}')
    apply_meta(state, "ui_panel_end", "1")
    apply_meta(state, "ui_panel", "map")
    handle_ui_json(state, '{"panel":"map","sections":[{"kind":"text","lines":["[@] square"]}]}')
    apply_meta(state, "ui_panel_end", "1")
    assert ordered_sidebar_stack(state.sidebar_stack) == ["pda", "map"]
    state.sidebar_stack = ["map", "gigs", "pda"]
    assert ordered_sidebar_stack(state.sidebar_stack) == ["pda", "gigs", "map"]
    text = format_sidebar_content(state)
    assert "100/100" in text
    assert "square" in text or "[@]" in text


def test_resolve_panel_command_aliases():
    from client.meta_handlers import resolve_panel_command

    assert resolve_panel_command("map") == "map"
    assert resolve_panel_command("h") == "help"
    assert resolve_panel_command("eq") == "equipment"
    assert resolve_panel_command("st") == "pda"
    assert resolve_panel_command("gigs") == "gigs"
    assert resolve_panel_command("journal") == "gigs"
    assert resolve_panel_command("look") is None


def test_sidebar_should_show_with_pending_panel():
    from client.meta_handlers import sidebar_should_show

    state = ClientViewState(sidebar_open=True, pending_panel="map")
    assert sidebar_should_show(state)
    state.sidebar_open = False
    assert not sidebar_should_show(state)


def test_toggle_sidebar_panel():
    state = ClientViewState(sidebar_open=True, sidebar_stack=["pda"])
    assert not toggle_sidebar_panel(state, "pda")
    assert state.sidebar_stack == []
    assert not state.sidebar_open
    assert toggle_sidebar_panel(state, "map")
    assert state.sidebar_open


def test_combat_hint_priority():
    state = ClientViewState(in_combat=True, combat_log="P:0 N:1", hint="任務提示")
    text = hint_text(state)
    assert "P:0 N:1" in text
    assert "任務提示" in text


def test_local_commands():
    assert is_local_command("/reconnect")
    assert is_local_command("/clear")
    assert is_local_command("/prompt set %n>")
    assert is_local_command("/theme matrix")
    assert not is_local_command("look")
    assert not is_local_command("clear")
    assert parse_local_command("/prompt set %h>") == ("prompt", "set %h>")
    assert parse_local_command("/theme tron") == ("theme", "tron")


def test_classify_server_line():
    assert classify_server_line("@meta hp=10") == "meta"
    assert classify_server_line("@panel line") == "panel"
    assert classify_server_line("@ui {}") == "ui"
    assert classify_server_line("hello") == "text"


def test_reconnect_backoff():
    assert reconnect_delay(1) == 1.0
    assert reconnect_delay(2) == 2.0
    assert reconnect_delay(5) == 16.0


def test_meta_skip_status_refresh_keys():
    from client.meta_handlers import META_SKIP_STATUS_REFRESH

    assert "complete_npcs" in META_SKIP_STATUS_REFRESH
    assert "ui_panel_end" in META_SKIP_STATUS_REFRESH
    assert "room" not in META_SKIP_STATUS_REFRESH


def test_should_refresh_map_sidebar_on_room_change():
    state = ClientViewState(sidebar_open=True, sidebar_stack=["map"], room_id="square")
    assert should_refresh_sidebar_on_room_change(
        state,
        old_room_id="square",
        new_room_id="alley",
    )
    assert panels_to_refresh_on_move(state) == ["map"]
    assert not should_refresh_sidebar_on_room_change(
        state,
        old_room_id="alley",
        new_room_id="alley",
    )
    state.sidebar_stack = ["pda", "map"]
    assert should_refresh_sidebar_on_room_change(
        state,
        old_room_id="square",
        new_room_id="alley",
    )
    state.sidebar_stack = ["pda"]
    assert not should_refresh_sidebar_on_room_change(
        state,
        old_room_id="square",
        new_room_id="alley",
    )


def test_sidebar_ui_text_sections():
    state = ClientViewState()
    apply_meta(state, "ui_panel", "map")
    handle_ui_json(state, '{"title":"地圖","sections":[{"kind":"text","lines":["[@]"," ■ "]}]}')
    apply_meta(state, "ui_panel_end", "1")
    text = format_sidebar_content(state)
    assert "[@]" in text or "[/]" in text


def test_sidebar_prefers_ui_json_over_panel_lines():
    state = ClientViewState(sidebar_open=True, sidebar_stack=["pda"])
    state.sidebar_panels["pda"] = SidebarPanel(
        lines=["◈ PDA", "HP 100/100", "HP 100/100"],
        ui={"title": "PDA", "sections": [{"kind": "row", "label": "HP", "value": "100/100"}]},
    )
    text = format_sidebar_content(state)
    assert text.count("100/100") == 1


def test_active_prompt_expands_local_override():
    state = ClientViewState(hp="50/100", player_name="V")
    assert active_prompt(state, local_override="[%h] %n>") == "[50/100] V>"


def test_netrun_prompt_and_blocking():
    state = ClientViewState()
    apply_meta(state, "net_shell", "1")
    apply_meta(state, "net_prompt", "ghost@net> ")
    assert active_prompt(state) == "ghost@net> "
    assert not netrun_blocks_server_command("look")
    assert not netrun_blocks_server_command("/look")
    assert not netrun_blocks_server_command("talk")
    assert not netrun_blocks_server_command("scan")
    assert not netrun_blocks_server_command("exit")
    assert not netrun_blocks_server_command("hack")
    assert not netrun_blocks_server_command("probe")
    assert not netrun_blocks_server_command("/probe")
    assert not netrun_blocks_server_command("status")
    assert normalize_netrun_command("/probe") == "probe"
    outbound, blocked = prepare_netrun_outbound("/probe")
    assert outbound == "probe"
    assert not blocked
    outbound, blocked = prepare_netrun_outbound("/look")
    assert outbound == "look"
    assert not blocked
    apply_meta(state, "net_shell", "0")
    assert not state.net_shell
    assert is_netrun_exit_command("/exit")
    assert not is_local_command("/exit")
    assert is_local_command("/reconnect")