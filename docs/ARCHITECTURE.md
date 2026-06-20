# Architecture

> **中文：** [ARCHITECTURE.zh.md](ARCHITECTURE.zh.md)

> cyber_mud documentation fork. Describes the system architecture of the original **mud** project (implemented + planned).

## Table of contents

- [World setting](#world-setting)
- [Overview](#overview)
- [Runtime architecture](#runtime-architecture)
- [Data flow](#data-flow)
- [Module dependencies](#module-dependencies)
- [Implemented features](#implemented-features)
- [Planned](#planned)

## World setting

The original **mud** setting is cyberpunk **Night City**: corporations, gangs, cyberware, and black markets. Players enter via a **neural link** and switch between the **NETRUN** hack layer and the physical streets. Full lore: **[WORLD.md](WORLD.md)**.

## Overview

```text
                    ┌─────────────┐
                    │ Textual TUI │  client/ (primary UI)
                    └──────┬──────┘
                           │ TCP newline text
                    ┌──────▼──────┐
                    │ server/     │  asyncio, Session, Game
                    │  game.py    │
                    └──────┬──────┘
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
    ┌────────────┐  ┌────────────┐  ┌────────────┐
    │ commands/  │  │ world/     │  │ combat/    │
    │ registry   │  │ tick/clock │  │ encounter  │
    └─────┬──────┘  └─────┬──────┘  └────────────┘
          │               │
          ▼               ▼
    ┌────────────┐  ┌────────────┐
    │ entities/  │  │ data/      │
    │ Player…    │  │ YAML world │
    └────────────┘  └────────────┘
          │
          ▼
    ┌────────────┐
    │persistence/│  saves/, world_state.json
    └────────────┘
```

## Runtime architecture

### Connection model

- One player per `ClientSession` (includes `StreamWriter`, `Player`, panel state)
- `server/main.py`: `readline` → `handle_command` (**blocks until done**)
- Background `tick_loop`: periodic `process_tick`, shares `WorldState` with command handling (watch asyncio concurrency / locks)

### Game responsibilities

- Maintain `sessions` list
- `dispatch` player commands
- `broadcast_localized` room / global messages
- `tick_loop` drives the world
- `reload_world` (dev mode)
- Graceful shutdown: save, notify offline

## Data flow

### Commands (Client → Server)

```text
Player types "equip blade"
  → client sends "equip blade\n"
  → server dispatch
  → updates Player.equipment
  → returns text lines + @meta lines
  → (if sidebar open) client may send "equipment" to refresh
```

### Meta (state sync)

```text
@meta hp=80/100
@meta hint=▸ quest hint…
@meta combat=1
```

Client updates status bar, hint_bar, prompt token sources.

### Panel stream

```text
@meta ui_panel=pda
@panel …
@meta ui_panel_end=1
```

## Module dependencies

| Module | Depends on | Must not depend on |
|--------|------------|-------------------|
| `shared/` | stdlib | server, client |
| `entities/` | shared | commands, server |
| `world/` | entities, data loaders | client |
| `commands/` | world, entities, combat | client |
| `server/` | commands, world, persistence | client |
| `client/` | shared | server, commands |
| `combat/` | entities, world | client |

## Implemented features

### Core

- [x] Multi-player TCP server
- [x] Command registry and aliases
- [x] World YAML load and validation
- [x] Player saves and world_state
- [x] Textual client (log, status, sidebar, Tab completion, hotkey bar, spinner, themes)
- [x] i18n (zh/en)
- [x] Paginated long output (look, help, etc.)

### Game systems

- [x] Items take/drop/equip/unequip (incl. all)
- [x] Equipment slots and weapon mods
- [x] Cyberware install, skill learn
- [x] World clock and tick
- [x] CP2077-style attribute fields
- [x] Regional weather
- [x] NPC tick movement / idle
- [x] Real-time combat encounter (`combat_cd` second-level meta, client countdown)
- [x] NETRUN sub-shell (server `net` + client `net_shell` meta)
- [x] PDA / map / help / equipment sidebar
- [x] Custom prompt (server + client override)
- [x] Dev hot-reload (`data/*.yaml` + code `reload_application_code`), client auto-reconnect and `/reconnect`
- [x] Sidebar equipment auto-refresh

### Tools

- [x] `admin.sh validate` / `saves` / `delete-save`
- [x] `tools/generate_world.py` (procedural room grid)
- [x] pytest

## Planned

Changelog and todos: [PHASES.md — Backlog](PHASES.md#backlog). **Update before every delivery** ([backlog convention](PHASES.md#backlog-maintenance)).

Excerpt:

- Weather / period gameplay modifiers
- Full passive skills and cyberware triggers
- NPC quest-driven AI
- Advanced NPC chase and flee
- Shop hours, quest authoring tools

---

Implementation steps: [IMPLEMENTATION.md](IMPLEMENTATION.md). New project bootstrap: [BOOTSTRAP.md](BOOTSTRAP.md).