> **中文：** [IMPLEMENTATION.zh.md](IMPLEMENTATION.zh.md)

# Implementation Blueprint

> This document is distilled from the original **mud** project (commit ~`34d5525`), for **cyber_mud** to rebuild from scratch or fork with a new theme.  
> It does not include runnable source code; details are described as **module responsibilities + data structures + protocol + behavior**.

## Table of Contents

- [Design Principles](#design-principles)
- [Tech Stack](#tech-stack)
- [Module Overview](#module-overview)
- [Communication Protocol](#communication-protocol)
- [Command System](#command-system)
- [Entities and State](#entities-and-state)
- [World and Data](#world-and-data)
- [World-Building Documentation](#world-building-documentation)
- [Server Flow](#server-flow)
- [Client TUI](#client-tui)
- [Game Subsystems](#game-subsystems)
- [Persistence](#persistence)
- [Testing Strategy](#testing-strategy)
- [What to Change When Forking a New MUD](#what-to-change-when-forking-a-new-mud)

## Design Principles

1. **The built-in Textual client is the sole official interface**; the TCP plain-text protocol is for debugging only.
2. **Data-driven**: rooms, NPCs, items, skills, weather, etc. live in `data/`; code only interprets and executes.
3. **One command per file**: `commands/<verb>.py` registers with `registry`.
4. **Per-connection command serialization**: the server reads the next line only after `await handle_command` for each client (the client can safely send a refresh after a command based on this).
5. **English is the default locale** (switch with `lang en` / `lang zh`); copy lives in `locale/en.yaml` + `locale/zh.yaml`, looked up by key (`shared/i18n.py`); conventions in [`LOCALIZATION.md`](LOCALIZATION.md).

## Tech Stack

| Item | Choice |
|------|--------|
| Language | Python 3.13 |
| Environment | pyenv + virtualenv (`setup.sh`) |
| Client UI | Textual + Rich |
| World data | YAML (rooms, items, NPCs, …) |
| Tests | pytest (target 150+ tests) |
| Communication | asyncio TCP, `readline` newline protocol |

## Module Overview

```text
server/          Game, ClientSession, tick_loop, broadcast
server/main.py   accept connections, read lines, graceful shutdown
client/          MudClientApp (Textual), connection, sidebar, autocomplete
shared/          protocol constants, i18n, completion, ui_json
world/           World, Room, WorldState, clock, weather, tick
entities/        Player, NPC, Item data classes
commands/        all player commands + registry + helpers
combat/          Encounter real-time combat state
persistence/     player saves, world_state.json
data/            static world definitions
locale/          zh / en string tables
tests/           unit and integration tests
```

## Communication Protocol

Defined in `shared/protocol.py`. One message per line, UTF-8 with newline terminator.

### Prefix Overview

| Prefix | Purpose | Consumer |
|--------|---------|----------|
| (no prefix) | General game text | Client main log |
| `@meta key=value` | State sync (room, HP, hint, sidebar triggers, etc.) | Client `_apply_meta` |
| `@panel ` | Sidebar line-by-line content | Client `_write_panel_line` |
| `@ui ` | JSON structured UI (panel/sections) | Client `_apply_ui_json` |
| MOTD / SYS / ERR prefixes | Banner, system, error | Client colored output |

### Sidebar Streaming Protocol

Panel commands (`pda`, `help`, `map`, `equipment`) use `ok_panel()`:

```text
@meta ui_panel=pda
@ui {"panel":"pda","title":"...","sections":[...]}   # optional
@panel ═══ ...
@panel content line...
@meta ui_panel_end=1
```

The client uses `_sidebar_pending_panel` / `_sidebar_stream_panel` to prevent stale responses from polluting a new panel.

### Client → Server Control Meta

- `@meta rows=<terminal row count>`: used by paginator `take_page`

### Output Types (CommandResult)

| Type | Function | Behavior |
|------|----------|----------|
| General | `ok(lines)` | Multi-line text to main log |
| Document | `ok_document(lines)` | Long text pagination (`c`/`q` to continue) |
| Panel | `ok_panel(lines, panel=..., ui_json=...)` | Sidebar + optional JSON |

**Note**: `look` should use `ok_document` so content goes to the main log; do not use `ok_panel`, or players will not see the room description.

## Command System

### Registration and Dispatch

```python
# commands/registry.py
register("look", handle)
dispatch(line, player, state, peers, all_players)
```

Flow:

1. `expand_line()` resolves aliases (`l`→`look`, `eq`→`equipment`)
2. Split `verb` + `args`
3. Build `CommandContext(player, state, args, peers, all_players)`
4. Handler returns `CommandResult`
5. `server/game.py` sends output, `send_meta`, broadcast, and save based on result

### player_meta

Almost every successful command attaches `meta=player_meta(ctx)`, with fields including:

- `room`, `room_id`, `hp`, `gold`, `name`, `locale`, `auth`
- `hint`, `time`, `period`, `ram`, `humanity`, `reputation`
- `prompt_mud`, `prompt_netrun`
- `combat`, `combat_log`, `combat_cd` (during combat)
- `comp_*` (for autocomplete)
- `net_shell`, `net_prompt` (netrunning mode)

### Implemented Command Categories (Original Project)

**Movement / perception**: `look`, `go`, `map`, `scan`, `search`, `probe`  
**Items**: `take`, `drop`, `inventory`, `equip`, `unequip`, `use`, `give`, `appraise` + `all` batch  
**Combat**: `attack`, `quickhack`, `defend`, `flee`  
**Cyberware / mods**: `install`, `mod`, `learn`  
**Social**: `say`, `tell`, `talk`  
**System**: `help`, `pda`/`status`, `equipment`, `time`, `save`, `quit`, `prompt`, `lang`, `alias`  
**Netrunning**: `net` shell (`net_shell` subsystem)  
**Authentication**: `login` / `register` (unnamed player gate)

### Aliases

`commands/aliases.py`: `DEFAULT_ALIASES` + player `custom_aliases`.

## Entities and State

### Player (`entities/player.py`)

Core fields:

| Category | Fields |
|----------|--------|
| Identity | `name`, `named`, `locale`, `room_id` |
| Survival | `hp`, `max_hp`, `gold` |
| CP2077 attributes | `body`, `reflex`, `tech`, `cool`, `intelligence`, `humanity`, `reputation` |
| Netrunner | `ram`, `max_ram`, `skills[]`, `net_shell` |
| Inventory / equipment | `inventory[]`, `equipment{slot: item_id}` |
| Cyberware | `implants[]` (or equivalent structure) |
| Combat | `in_combat`, `status_effects[]` |
| Custom | `prompt_mud`, `prompt_netrun`, `custom_aliases` |

### Item / NPC

- Item: `slot`, `takeable`, `weapon_damage`, `defense`, value, description (multilingual keys)
- NPC: `hp`, `hostile`, `room_id`, dialogue, drops; can move / idle during tick

### WorldState (`world/state.py`)

- Static: `world` (room graph, item table, NPC table, …)
- Dynamic: `room_items` (ground items per room), `clock`, `weather`, `combat_encounters`, NPC runtime positions

## World and Data

### Recommended Directory Layout

```text
data/
  world.yaml      # or rooms.yaml + index
  items.yaml
  npcs.yaml
  skills.yaml
  implants.yaml
  weather.yaml
  time.yaml
```

### Rooms

- `id`, `name`, `description` (locale key)
- `exits`: `{direction: room_id}`
- `district`, `tags` (security level, indoor/outdoor)
- grid coordinates (for map)

### Equipment Slots

`shared/equipment.py` defines `EQUIP_SLOTS` (e.g. weapon, armor, head, …). `equip` wears items by `item.slot`.

### World-Building Documentation

Settings, districts, factions, narrative anchors, and gameplay mapping are in **[WORLD.md](WORLD.md)** (the “Night City” homage to Blade Runner + Cyberpunk 2077).

## Server Flow

```text
main.py: readline loop
  → @meta rows → apply_client_meta
  → otherwise → game.handle_command
       → dispatch
       → send_output / send_meta
       → broadcast / notify
       → persist player + world_state (if world_changed)

game.tick_loop (background):
  → process_tick(state, sessions)
       → advance clock, weather, NPC move/idle, combat tick
       → push meta / messages to online players
```

**Hot reload** (`./run.sh --dev`): code changes restart the server; `world` / `locale` can reload without kicking players.

## Client TUI

### Layout

- Header, status bar (room / HP / money / time / RAM, …)
- `hint_bar` (combat log, quest hints)
- Main `RichLog` + collapsible `GameSidebar`
- Prompt line (password masking, history, Tab completion)

### Hotkeys

| Key | Panel |
|-----|-------|
| F2 | PDA (vitals + equipment + cyberware + skills) |
| F3 | Help |
| F4 | Map |
| F5 | Equipment |

### Sidebar Refresh

- Open panel: `_refresh_panel` → send `pda` / `equipment`, etc.
- **Auto-refresh after equipment changes** (original project `34d5525`): if the sidebar has `pda` or `equipment` open, automatically `_refresh_panel` after `equip`/`unequip`/`drop`/`install`/`mod` commands are sent

### Auto-Reconnect

Exponential backoff reconnect after disconnect; if previously logged in, resend auth line.

### Local Commands (starting with `/`)

`/prompt`, `/theme`, `/reconnect`, `/quit`, etc.—not sent to the server.

## Game Subsystems

### A. Time and Tick (Phase A)

- `world/clock.py`: `TimeConfig`, `day`, `period` (morning / afternoon / night, …)
- `world/tick.py`: `process_tick` every N seconds
- `commands/time.py` queries world time
- `@meta time` / `period` updates client status bar

### B. Attributes (Phase A)

Five core attributes affect combat / checks; shown on `pda`. Alongside `hp` / `ram` / `humanity` / `reputation`.

### C. Weather (Phase B)

- `world/weather.py`: per district or global; `look` / status bar can display
- Data in `data/weather.yaml`

### D. NPC Movement and Idle (Phase B)

- During tick, patrol / guard based on district, personality, time of day
- Enter/leave same room: broadcast or visible via `look`
- Idle actions (smoking, shouting) throttled to avoid spam

### E. Real-Time Combat (Phase C)

- `combat/encounter.py`: `Encounter` with both sides' CDs, turn queue
- Player: `attack`, `defend`, `flee`, `quickhack`
- Tick advances NPC actions; `@meta combat=1`, `combat_log`, `combat_cd`
- Passive skills / cyberware can hook conditional triggers (extension point)

### F. Bulk Items and UI Polish (Phase D)

- `commands/bulk_helpers.py`: `take/drop/equip/unequip all` (including `全部`, `*`)
- `shared/ui_json.py`: structured sidebar
- `scan` + `search` merged display logic
- `give`, `appraise` valuation

### G. Prompt Customization

- Server `prompt` command + client `/prompt` local override
- Tokens: `%n` name, `%r` room, `%h` hp, … (extensible)

### H. NETRUN Sub-Shell

- `player.net_shell` switches theme / prompt
- `commands/net_shell.py` independent dispatch
- Client blocks general MUD commands (except `/reconnect`, etc.)

## Persistence

| File | Contents |
|------|----------|
| `saves/<name>.json` | Player progress |
| `world_state.json` | Dynamic world (ground items, clock, weather, …) |

`admin.sh validate`: validate `data/` + run pytest.

## Testing Strategy

| Area | Example Test Files |
|------|-------------------|
| Commands | `test_look.py`, `test_equip.py`, `test_bulk.py` |
| Combat | `test_combat.py` |
| Tick / time | `test_tick.py`, `test_time.py` |
| Client logic | `test_client_sidebar.py` (pure functions, no TUI) |
| Protocol / meta | `test_hint.py`, `test_prompt.py` |

Convention: change a command or world logic → run related tests → full `pytest tests/`.

## What to Change When Forking a New MUD

| Priority | Item | Notes |
|----------|------|-------|
| 1 | `data/` | New world, NPCs, story—**main effort** |
| 2 | `locale/` | World-building copy, command help text |
| 3 | `client/theme` | Colors, banner ASCII |
| 4 | `shared/` constants | Port, title, equipment slot names |
| 5 | `commands/` | Add only “new gameplay” commands; reuse the rest of the architecture |
| 6 | `CLAUDE.md` / agent skills | Update project name and world description |

**No need to rewrite**: `server` connection model, `registry` dispatch, `protocol`, `persistence` skeleton, Textual client framework.

---

Next step: build the MVP per [BOOTSTRAP.md](BOOTSTRAP.md), then fill in phase by phase per [PHASES.md](PHASES.md).