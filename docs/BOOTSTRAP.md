# Bootstrap — New Project Setup

> **中文：** [BOOTSTRAP.zh.md](BOOTSTRAP.zh.md)

## Table of contents

- [Environment](#environment)
- [Suggested layout](#suggested-layout)
- [Minimum playable version (MVP)](#minimum-playable-version-mvp)
- [Verification checklist](#verification-checklist)

## Environment

- Python **3.13** (pyenv virtualenv recommended, e.g. `cyber-mud-3.13.12`)
- Main deps: `textual`, `rich`, `pyyaml`, `pytest`
- Scripts: `setup.sh`, `run.sh`, `admin.sh`

```bash
# First time
./setup.sh

# Development (hot reload)
./run.sh --dev

# Built-in TUI client
./run.sh --client
```

## Suggested layout

```text
cyber_mud/
├── client/           # Textual TUI (primary player UI)
├── server/           # TCP connections, game loop, sessions
├── shared/           # protocol constants, i18n, protocol
├── world/            # map, rooms, clock, weather, tick
├── entities/         # Player, NPC, Item
├── commands/         # command handlers (one verb per file)
├── combat/           # real-time encounter
├── persistence/      # saves, world_state
├── data/             # YAML/JSON world definitions
├── locale/           # en / zh strings
├── tests/
├── docs/
├── setup.sh
├── run.sh
└── admin.sh
```

## Minimum playable version (MVP)

Build in order; each step is verifiable:

### 1. Protocol and connection

- `shared/protocol.py`: newline protocol, `@meta`, `@panel`, `@ui`, `MOTD_PREFIX`, etc.
- `server/main.py`: accept → `readline` → `handle_command` (**sequential per connection**)
- `client/`: connect, read loop, main log output

**Verify**: client connects, sees MOTD, `look` shows a room.

### 2. World load

- `data/world.yaml` (or split files): rooms, exits, items, npcs
- `world/state.py`: `WorldState` load and runtime `room_items`, etc.
- `commands/look.py`, `commands/go.py`

**Verify**: `go north` changes room; `look` content is correct.

### 3. Player and login

- `entities/player.py`: `hp`, `gold`, `inventory`, `equipment`, `named`
- `commands/login` / `register` (or combined auth flow)
- `persistence/save.py`: logout / periodic save

**Verify**: after register, reconnect keeps position and inventory.

### 4. Command registry

- `commands/registry.py`: `register()`, `dispatch()`, `ok()` / `ok_panel()` / `ok_document()`
- `commands/aliases.py`: `expand_line()` (`l`→`look`, `eq`→`equipment`, etc.)

**Verify**: `pytest tests/test_registry.py` (or equivalent) passes.

### 5. Built-in client base UI

- Status bar: `room`, `hp`, `gold` (from `@meta`)
- Input, Tab completion (`shared/completion.py`); history (↑↓) optional later
- F2–F5 sidebar skeleton (PDA first is fine)

**Verify**: `./run.sh --client` plays MVP without `nc`.

## Verification checklist

| Item | Command / action |
|------|------------------|
| Server start | `./run.sh` |
| Client connect | `./run.sh --client` |
| World data valid | `./admin.sh validate` |
| Tests | `pytest tests/` |
| Hot reload | `./run.sh --dev` — edit `data/` or `commands/` still works |

After MVP, extend per [PHASES.md](PHASES.md) Phases A–D. World lore: [WORLD.md](WORLD.md).