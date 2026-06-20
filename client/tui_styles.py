"""Textual CSS inspired by Grok Build CLI scrollback + prompt layout."""

APP_CSS = """
Screen {
    background: $background;
}

Header {
    background: $surface;
    color: $text-muted;
    border-bottom: solid $surface;
    height: 1;
}

Footer {
    background: $surface;
    color: $text-muted;
    border-top: solid $surface;
}

Input {
    border: none;
    background: transparent;
    padding: 0 1;
}

Input:focus {
    border: none;
}

Select {
    margin-bottom: 1;
    border: tall $surface;
}

#login_container {
    height: 1fr;
}
.login-hidden {
    display: none;
}
#login_art {
    height: 38%;
    max-height: 14;
    min-height: 6;
    width: 100%;
    content-align: center middle;
    text-align: center;
    color: $accent;
    background: $background;
    border-bottom: solid $surface;
    overflow: hidden;
}
#login_form_scroll {
    height: 1fr;
    padding: 0 6;
    background: $background;
}
#login_form {
    width: 1fr;
    height: auto;
    padding: 1 2;
}
#login_title {
    text-align: center;
    margin-bottom: 1;
}
#login_theme_label, #auth_mode_label, #login_name_label, #login_password_label,
#login_pin_label, #login_pin_setup_label, #login_pin_confirm_label {
    color: $text-muted;
    margin-top: 1;
}
.credential-hidden {
    display: none;
}
#remember_credentials {
    margin-top: 1;
    margin-bottom: 1;
}
#login_form Input {
    width: 1fr;
    height: 3;
    min-height: 3;
    border: tall $accent 50%;
    background: $panel;
    margin-bottom: 1;
}
#login_form Input:focus {
    border: tall $accent;
    background: $surface;
}
#login_form Select {
    width: 1fr;
    margin-bottom: 1;
}
#login_hint {
    color: $text-muted;
    text-align: center;
    margin-top: 2;
}
#login_status {
    color: $warning;
    text-align: center;
    margin-top: 1;
    height: auto;
}

#game_container {
    height: 1fr;
}
.game-hidden {
    display: none;
}

#top_dock {
    dock: top;
    width: 100%;
    height: auto;
}

#info_bar {
    width: 100%;
    height: auto;
    max-height: 2;
    background: $surface;
    color: $foreground;
    padding: 0 2;
    border-bottom: solid $surface;
    overflow: hidden;
}

#chrome_bar {
    width: 100%;
    height: auto;
    min-height: 1;
    background: $panel;
    color: $foreground;
    padding: 0 2;
    border-bottom: solid $accent 40%;
    text-style: bold;
}

#bottom_dock {
    dock: bottom;
    width: 100%;
    height: auto;
}

#prompt_preview {
    width: 100%;
    height: auto;
    min-height: 1;
    background: $surface;
    color: $text-muted;
    padding: 0 2;
    border-top: solid $surface;
    overflow: hidden;
}
.preview-hidden {
    display: none;
}

#hotkey_bar {
    width: 100%;
    height: auto;
    min-height: 1;
    background: $surface;
    color: $foreground;
    padding: 0 2;
    border-top: solid $surface;
    text-style: bold;
}

#prompt_dock {
    width: 100%;
    height: 3;
    layout: horizontal;
    background: $panel;
    border-top: solid $surface;
    padding: 0 1 0 0;
}

#main_row {
    height: 1fr;
    width: 100%;
    min-height: 1;
    padding: 0 1;
}

#scrollback_wrap {
    width: 1fr;
    height: 1fr;
    border-left: heavy $accent;
    background: $background;
    padding: 0 1 0 1;
    margin: 0 0 0 1;
}

#log {
    width: 1fr;
    height: 1fr;
    overflow-y: scroll;
    scrollbar-background: $surface;
    scrollbar-color: $accent;
    padding: 0 1;
}

#sidebar_wrap {
    width: 38;
    height: 1fr;
    margin: 0 1 0 0;
    border-left: solid $surface;
}

#sidebar_header {
    height: 1;
    color: $accent;
    background: $panel;
    border-left: heavy $accent;
    padding: 0 1;
}

#sidebar {
    height: 1fr;
    background: $panel;
    border-left: heavy $accent;
    padding: 0 1;
    scrollbar-background: $surface;
    scrollbar-color: $accent;
    overflow-y: auto;
}
#sidebar:focus {
    border-left: heavy $accent;
}

#sidebar_content {
    width: 1fr;
    height: auto;
    padding: 1 0;
}

.sidebar-hidden {
    display: none;
}
.sidebar-visible {
    display: block;
}

#prompt_dock.prompt-focused {
    border-top: heavy $accent;
}

#prompt_accent {
    width: 1;
    color: $accent;
    content-align: center middle;
}

#prompt_row {
    width: 1fr;
    height: 3;
    layout: horizontal;
}

#prompt_prefix {
    width: auto;
    max-width: 40%;
    height: 1;
    color: $accent;
    text-style: bold;
    padding: 0 1 0 0;
    content-align: left middle;
}

#prompt {
    width: 1fr;
    height: 3;
    min-height: 3;
}
"""