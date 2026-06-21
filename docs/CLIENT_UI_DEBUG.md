# Client UI Debug Cases & Conventions

> **中文：** [CLIENT_UI_DEBUG.zh.md](CLIENT_UI_DEBUG.zh.md)

This document records **June 2026** Textual client layout/sidebar issues that were hard to fix, with root causes and final solutions. Use when changing `client/`.

## Table of contents

- [Symptom summary](#symptom-summary)
- [Root cause 1: Textual `region` vs `size`](#root-cause-1-textual-vs)
- [Root cause 2: Dock stacking](#root-cause-2-dock-stacking)
- [Root cause 3: Sidebar state machine (dual paths)](#root-cause-3-sidebar-state-machine-dual-paths)
- [Root cause 4: Async blocking](#root-cause-4-async-blocking)
- [Pre-delivery checklist (client UI changes)](#pre-delivery-checklist-client-ui-changes)
- [Test conventions (avoid false positives)](#test-conventions-avoid-false-positives)
- [Anti-patterns](#anti-patterns)
- [Related tests](#related-tests)
- [Change history (summary)](#change-history-summary)
- [Client log UX (CL.1–CL.8 shipped)](#client-log-ux-cl1cl8-shipped)

## Symptom summary

| Symptom | User observation | Actual root cause |
|---------|------------------|-------------------|
| Link / hotkey / info bars missing | Any top/bottom `Static` blank in terminal | `Static` without `min-height:1` → `region.height≥1` but `size.height=0`; real terminal draws nothing |
| Typing `map`/`pda` does not open sidebar | F2–F5 works | Prompt path never set `sidebar_open`; `ui_panel_end` only stacks when `sidebar_open` |
| Spamming F keys freezes UI | UI stuck for tens of seconds | `action_*` did `await _fetch_panel()` (up to 15s) on main loop |
| Sidebar reopens after F6 (old bug) | Late meta after close | `ui_panel_end` unconditionally appended (fixed with `sidebar_open` gate) |
| Thought saves were broken | Same after character swap | Sidebar state is in-memory; layout does not read `data/saves/` |

**Not** a model issue; **usually not** a player save issue.

## Root cause 1: Textual `region` vs `size`

Headless `run_test` often shows:

```text
#info_bar:   region.height=1  size.height=0  → test passes, terminal blank
#chrome_bar: region.height=1  size.height=0  → same
```

**Wrong fix**: only tweak `dock`, move widgets, assert `region`.  
**Right fix**: `#info_bar` / `#chrome_bar` / `#hotkey_bar` use `height: auto; min-height: 1`; do not set `max-height: 1` on `#info_bar` (see `client/tui_styles.py`).

Probe (run after client changes):

```bash
.venv/bin/python -c "
import asyncio
from client.meta_handlers import apply_meta
from client.app import CyberMudApp

async def main():
    app = CyberMudApp('127.0.0.1', 4000)
    async with app.run_test(size=(120, 30)) as pilot:
        apply_meta(app.view, 'auth', '1')
        app._set_auth_ui(True)
        await pilot.pause()
        for wid in ('#info_bar', '#chrome_bar', '#hotkey_bar'):
            w = app.query_one(wid)
            print(wid, 'region', w.region.height, 'size', w.size.height)

asyncio.run(main())
"
```

Acceptance: `size.height >= 1` and visible in a real terminal.

## Root cause 2: Dock stacking

Multiple children with `dock: top` / `dock: bottom` **overlap** (e.g. `info_bar` and `chrome_bar` same y).

**Working structure** (`client/app.py` compose):

```text
#top_dock (dock:top, vertical) → info_bar + chrome_bar
#main_row (1fr)
#bottom_dock (dock:bottom, vertical) → prompt_dock + hotkey_bar
```

Single dock container + internal vertical flow; do not stack multiple same-direction docks.

## Root cause 3: Sidebar state machine (dual paths)

```text
F2–F5  → _send_panel_command → toggle_sidebar_panel → sidebar_open=True
      → pending_panel → _schedule_panel_fetch (background)
      → server ui_panel / ui_panel_end → stack → _render_sidebar

Type map → on_game_input → resolve_panel_command
      → prepare_sidebar_for_panel + pending_panel (aligned with F keys)
      → send_line → same meta stream
```

Display: `sidebar_should_show()` = `sidebar_open` AND (`sidebar_stack` OR `pending_panel`).

| Meta / behavior | Notes |
|-----------------|-------|
| `ui_panel_end` stacks | Only when `sidebar_open` (F6 → False → late response does not reopen) |
| F key while loading | Cancel fetch (`_cancel_panel_fetch`), do not queue again |
| F6 | Clear stack, `sidebar_open=False`, bump `_panel_fetch_generation` |

Modules: `client/meta_handlers.py` (`resolve_panel_command`, `prepare_sidebar_for_panel`, `sidebar_should_show`), `client/app.py` (`_send_panel_command`, `_schedule_panel_fetch`).

## Root cause 4: Async blocking

**Do not** `await _fetch_panel()` inside `action_panel_*`.  
Use `asyncio.create_task` + lock serialization + cancellable generation.

Spamming F keys used to queue 6×15s; new behavior should return in <1s (`tests/test_client_app.py::test_panel_fetch_actions_do_not_block`).

## Pre-delivery checklist (client UI changes)

Verify in **Windows Terminal / your usual terminal** and `pytest`:

1. [ ] After login: `info_bar`, **link bar** (chrome), **hotkey bar** visible (even at 24 rows)
2. [ ] Type `map`, `pda`, `h` (help) → sidebar opens
3. [ ] F2 + F4 stack → F6 closes all; late `ui_panel_end` does not reopen
4. [ ] Rapid F2/F3/F4 → prompt still accepts input, no obvious freeze
5. [ ] `pytest tests/test_client_app.py tests/test_client_meta.py` pass
6. [ ] Update [PHASES.md](PHASES.md) backlog / completed

## Test conventions (avoid false positives)

| Do not only test | Also test |
|------------------|-----------|
| `widget.region.height == 1` | `widget.size.height >= 1` |
| Set `sidebar_open=True` then feed meta | Full path via `prepare_sidebar_for_panel` or `_send_panel_command` |
| Single F2 press | Rapid presses, `test_f6_closes_sidebar_*`, typed map |

## Anti-patterns

1. **Symptom-driven**: change colors/layout without measuring `size.height`
2. **F6-only fix**: gate `ui_panel_end` but not `sidebar_open` on prompt path
3. **Over-docking**: multiple `dock: top` expecting auto stack
4. **Long await in actions**: network / 15s wait in key handlers
5. **Headless only**: never checked real terminal

## Related tests

- `tests/test_client_app.py`: `test_chrome_bar_*`, `test_hotkey_bar_*`, `test_typed_map_command_opens_sidebar`, `test_panel_fetch_actions_do_not_block`, `test_f6_closes_sidebar_*`
- `tests/test_client_meta.py`: `test_resolve_panel_command_aliases`, `test_sidebar_should_show_with_pending_panel`

## Change history (summary)

| Item | Module |
|------|--------|
| Single top/bottom dock containers | `client/app.py`, `client/tui_styles.py` |
| chrome/hotkey `min-height:1` | `client/tui_styles.py` |
| Prompt panel auto-open sidebar | `client/meta_handlers.py`, `client/app.py` |
| Non-blocking fetch + cancel | `client/app.py` |

Full backlog entry: [PHASES.md](PHASES.md) — hotkey bar visibility.

## Client log UX (CL.1–CL.8 shipped)

**Problem:** Most server lines use the same dim `›` prefix (`client/output_prefix.py` kind `text`). Only MOTD/SYS/ERR/echo differ; `env_format.py` colors look/scan entity rows but not combat, quests, social, or progression.

**Before changing log styling:**

1. Read PHASES **Client log UX** — implement CL.1 classifier before palette tweaks.
2. Add tests in `tests/test_log_classifier.py` (prefix → kind); extend `test_output_prefix` / `test_env_format`.
3. Theme changes must redraw log via `AnimatedLogBuffer` + `LogPalette` (mirror `EnvPalette` pattern in `client/themes.py`).
4. Do not break CD countdown (`cd_display.py`) or pending-command spinner on the in-flight echo line.

**Key files:** `client/animated_log.py`, `client/output_prefix.py`, `client/env_format.py`, `client/app.py` (`_append_log`, `_read_loop`).
