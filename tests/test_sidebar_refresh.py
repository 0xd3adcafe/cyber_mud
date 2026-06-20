from client.meta_handlers import ClientViewState, SidebarPanel, patch_open_pda_ui
from client.sidebar_refresh import panels_to_fetch, stack_panels_for_poll


def test_panels_to_fetch_intersects_stack():
    pending = {"pda", "equipment", "gigs"}
    stack = ["pda", "map"]
    assert panels_to_fetch(pending, stack) == ["pda"]


def test_stack_panels_for_poll_skips_help():
    assert stack_panels_for_poll(["pda", "help", "map"]) == ["pda", "map"]


def test_patch_open_pda_ui_updates_vitals_without_server_fetch():
    state = ClientViewState(
        sidebar_open=True,
        sidebar_stack=["pda"],
        locale="en",
        hp="80/100",
        gold="42",
    )
    state.sidebar_panels["pda"] = SidebarPanel(
        ui={
            "sections": [
                {"id": "vitals", "kind": "row", "label": "Vitals", "value": "HP 100/100  │  $0"},
                {"id": "ram", "kind": "row", "label": "RAM", "value": "4/8"},
            ]
        }
    )
    assert patch_open_pda_ui(state, "hp")
    vitals = next(s for s in state.sidebar_panels["pda"].ui["sections"] if s["id"] == "vitals")
    assert "80/100" in vitals["value"]
    assert "42" in vitals["value"]