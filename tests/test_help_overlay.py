from client.help_overlay import format_help_overlay_content, help_overlay_header
from client.meta_handlers import SidebarPanel


def test_help_overlay_header():
    assert "指令說明" in help_overlay_header()
    assert "F3" in help_overlay_header()


def test_format_help_overlay_from_ui_list():
    panel = SidebarPanel(
        ui={
            "panel": "help",
            "sections": [
                {
                    "kind": "list",
                    "items": ["look — 察看環境", "go — 移動"],
                }
            ],
        }
    )
    text = format_help_overlay_content(panel)
    assert "look" in text
    assert "察看環境" in text
    assert "go" in text


def test_format_help_overlay_from_panel_lines():
    panel = SidebarPanel(lines=["◈ 可用指令", "", "  take — 撿起地上物品"])
    text = format_help_overlay_content(panel)
    assert "take" in text
    assert "撿起" in text