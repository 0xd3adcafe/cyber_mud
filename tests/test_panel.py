from commands.registry import ok_panel
from shared.protocol import PANEL_PREFIX, UI_PREFIX, meta_line, ui_line


def test_ok_panel_result_fields():
    result = ok_panel(["line1"], panel="pda", ui_json='{"panel":"pda"}')
    assert result.panel == "pda"
    assert result.ui_json
    assert result.lines == ["line1"]


def test_panel_protocol_lines():
    panel = "equipment"
    lines = ["◈ 裝備", "  weapon: knife"]
    ui = '{"panel":"equipment"}'
    protocol = [
        meta_line("ui_panel", panel),
        ui_line(ui),
        *[f"{PANEL_PREFIX}{line}" for line in lines],
        meta_line("ui_panel_end", "1"),
    ]
    assert protocol[0] == "@meta ui_panel=equipment"
    assert protocol[1].startswith(UI_PREFIX)
    assert protocol[2].startswith(PANEL_PREFIX)
    assert protocol[-1] == "@meta ui_panel_end=1"