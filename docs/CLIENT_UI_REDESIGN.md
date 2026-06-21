# Client UI Redesign (Grok-style + NETRUN Terminal HUD)

> **中文：** [CLIENT_UI_REDESIGN.zh.md](CLIENT_UI_REDESIGN.zh.md)

**Status:** Approved spec (discussion closed); implementation **CU.1–CU.5** then **CU.0** in a separate commit.

**Scope:** In-game Textual UI only. Login layout unchanged except **CU.0** (ASCII art scene rotation).

**References:** [`CLIENT_UI_DEBUG.md`](CLIENT_UI_DEBUG.md), [`PHASES.md`](PHASES.md) § Client UI modernization (CU).

---

## Goals

1. **Grok-like minimal chrome** — one status strip, main log + prompt as hero.
2. **Dropdown dual mode (Plan B)** — browser-style tabs over the **upper 50%** of the log.
3. **NETRUN terminal HUD** — trace bar, link state, English command cheat sheet; opens on `net` / `netrun`.
4. **Sidebar unchanged role** — PDA, map, equipment, gigs, **mesh**; NETRUN auto-opens **mesh**.
5. **Locale for copy; commands always English** in HUD and cheat sheets.

---

## Layout (in-game)

```text
┌─ #status_strip (CU.1: merged info + link) ─────────────────┐
├─ #scrollback_wrap ─────────────────────────────────────────┤
│  ┌─ #overlay_panel (~50% height, layer: dropdown) ──────┐ │
│  │ [⎈ NET]  [? Help]     trace ████░░ 67%    [−]  Esc     │ │  ← tab row
│  ├────────────────────────────────────────────────────────┤ │
│  │ Active tab body (NETRUN HUD or Help categories)        │ │
│  └────────────────────────────────────────────────────────┘ │
│  #log (lower 50%, scrollable)                               │
├────────────────────────────┬───────────────────────────────┤
│                            │ #sidebar_wrap (F11 toggle)    │
│                            │ default on NETRUN: mesh panel │
├─ #focus_block (1–2 lines) ─┴───────────────────────────────┤
│ #prompt_dock                                                │
│ #hotkey_bar (contextual; shows F1–F12 map when dim)         │
└─────────────────────────────────────────────────────────────┘
```

---

## Overlay panel (CU.2–CU.3)

### Tab row (browser-style)

| Tab ID | Label | Visible when |
|--------|-------|--------------|
| `netrun` | `⎈ NET` | `net_shell=1` (dim/disabled when offline from NETRUN) |
| `help` | `? Help` | Always |

- **Active tab:** accent underline + bold (Rich markup on `#overlay_tab_*` click targets).
- **Inactive tab:** dim; click switches tab and refreshes body.
- **Not Tab key** — `Tab` remains command completion only.

### Chrome controls

| Control | Action |
|---------|--------|
| `[−]` / collapse action | Collapse overlay to zero height; log full height; session stays in NETRUN |
| **Esc** | Close overlay entirely |
| **F12** | Toggle overlay; when opening in NETRUN, select `⎈ NET` tab |
| **F2** | Open overlay on `? Help` tab (toggle if already on Help) |

### NETRUN tab body

Driven by server meta: `net_shell`, `net_trace`, `net_prompt`, `complete_net_nodes`, plus connected node when exposed.

- Trace bar: `████████░░` style, critical tint ≥ 80%.
- Link line: connected node label (locale name + English id).
- Sector nodes from completion meta.
- Command cheat sheet — **names always English:** `connect`, `breach`, `exploit`, `probe`, `route`, `cat`, `cover`, `exit`; descriptions use `player.locale`.

### Help tab body

Existing `help_overlay.py` formatting; server `help` fetch unchanged.

### Lifecycle

| Event | Overlay |
|-------|---------|
| `net` / `netrun` enter | Expand overlay, active tab `⎈ NET` |
| `exit` / forced disconnect | Close overlay |
| User collapse `[−]` | Hidden until F12 or re-enter `net` |

---

## Hotkeys (F1–F12)

**Sidebar toggle moves to F11.** Panel keys **renumber from F1** in order.

| Key | In-game action | Server / panel |
|-----|----------------|----------------|
| **F1** | PDA | `pda` |
| **F2** | Help overlay tab | `help` |
| **F3** | Map | `map` |
| **F4** | Equipment | `equipment` |
| **F5** | Gigs / journal | `gigs` |
| **F6** | Mesh (ctOS links) | `mesh` |
| **F7–F10** | *Reserved* | Future client features |
| **F11** | Toggle sidebar (open / collapse stack) | was F6 |
| **F12** | Toggle NETRUN overlay (`⎈ NET` tab) | NETRUN only |

| Key | Other |
|-----|--------|
| **Tab** | Command completion (unchanged) |
| **Esc** | Close overlay |

### Login screen exceptions

| Key | Login only |
|-----|------------|
| **F8** | Clear stored credentials (moved from old F7-on-login) |

Update `client/ui_format.py` `_PANEL_KEYS`, `format_hotkey_bar`, `BINDINGS`, locale `client.ui.hotkeys.*`, and player docs when implementing.

---

## Sidebar + NETRUN (CU.4–CU.5)

### Mesh panel (CU.5)

- New server panel command **`mesh`** → `@ui` JSON with discovered `discovered_net_links` (reuse `world/ctos_mesh.format_mesh_map_lines`).
- `resolve_panel_command("mesh")` on client.
- Empty state: locale hint to run `probe` in NETRUN.

### Auto-open on NETRUN

When `net_shell` becomes `1` and `netrun_sidebar_auto` is true (default):

1. Save sidebar snapshot (`open`, `stack`).
2. Open sidebar and fetch **mesh** (not map).
3. If user presses **F11** to close, do not force reopen until next `net` entry.
4. On NETRUN exit, restore snapshot.

Disable auto-switch: `/overlay netrun-sidebar off` (persist in client settings) — CU.5.

---

## Status strip (CU.1)

Merge `#info_bar` + `#chrome_bar` into `#status_strip`:

- Room, HP, gold, time, weather, NETRUN chip, quest chip (compact).
- Link state only when relevant (waiting, slow, reconnecting, panel fetch).

Remove duplicate vertical bar; keep `min-height: 1` per `CLIENT_UI_DEBUG.md`.

---

## NETRUN log styling (CU.4)

- NETRUN command echoes / `◈` lines: cyan/magenta channel or prefix.
- Physical world `look` / `scan` during NETRUN: keep existing env channels.
- `scrollback_wrap` optional subtle border tint while `net_shell=1`.

---

## Localization policy

| UI | Language |
|----|----------|
| Tab labels | Icon + short **English** (`⎈ NET`, `? Help`) — all locales |
| Descriptions, warnings, empty states | `player.locale` |
| Command names in HUD | **English only** |

---

## Delivery phases

| Phase | Item | Acceptance |
|-------|------|------------|
| CU.1 | Status strip merge | One top bar; 24-row terminal shows prompt |
| CU.2 | `#overlay_panel` + tab row | Help works via F2; click tabs switch |
| CU.3 | NETRUN HUD tab | `net` expands overlay; trace bar from meta |
| CU.4 | Log styling + F11/F12 + sidebar snapshot | NETRUN enter/exit restores sidebar |
| CU.5 | `mesh` panel + auto-open + `/overlay` setting | NETRUN defaults to mesh sidebar |
| CU.0 | Login ASCII scene rotation (8–12 s) | **Separate commit**; art height unchanged |

**Suggested implementation order:** CU.1 → CU.2 → CU.3 → CU.4 → CU.5, then CU.0.

**Tests:** `tests/test_client_app.py`, `tests/test_client_meta.py`, `tests/test_help_overlay.py`; update F-key assertions.

**Docs to sync on ship:** `docs/player/CLIENT.md`, `motd.tips`, locale hotkey strings.

---

## Risks

- Textual `layers` + 50% overlay height: verify `size.height` in real terminal (`CLIENT_UI_DEBUG.md` probe).
- F-key renumber breaks muscle memory — batch-update player guides in same milestone.
- Login F8 for credential clear must not fire in-game (gate on `authenticated`).