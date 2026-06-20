> **中文：** [CLAUDE.zh.md](CLAUDE.zh.md)

# CLAUDE.md

This file guides Claude Code, Cursor, and Grok when collaborating in this repo.  
**Behavior guidelines** follow [Andrej Karpathy Skills](https://github.com/multica-ai/andrej-karpathy-skills/blob/main/CLAUDE.md) (parent-directory link: `andrej-karpathy-skills.md`); below merges **cyber_mud** project-specific notes.

**Trade-off:** Guidelines favor caution over speed; trivial tasks may use judgment.

## Project rules (mandatory)

**These rules are non-negotiable for agents and contributors.**

### English is the default locale

| Area | Rule |
|------|------|
| **In-game** | New players, saves without `locale`, client login, and all `or "en"` fallbacks use **`locale=en`**. Chinese is opt-in: `lang zh`. |
| **Copy** | `data/locale/en.yaml` is authoritative; always add the same key to `zh.yaml`. World YAML: maintain `*_en` / `*_zh`; English when `player.locale == "en"`. |
| **Server logs** | `CYBER_MUD_SERVER_LOCALE` defaults to `en`; use `server.*` locale keys—no hardcoded Chinese/English in logic. |
| **Client UI** | `client.*` keys; default chrome and placeholders in English until `lang zh` meta. |
| **Docs** | English `*.md` is canonical on GitHub; mirror in `*.zh.md`. |
| **Commits** | English summary required: `<type>: EN summary` — optional ` / 中文`. |
| **Tests** | Use `Player()` or `make_player(locale="en")` for new tests unless explicitly testing `zh`. |

**Do not:** switch project default to `zh`, ship Chinese-only user-facing strings without locale keys, or add English-only docs without updating `en.yaml` when the change is in-game text.

Full policy: [`docs/LOCALIZATION.md`](docs/LOCALIZATION.md).

## Table of contents

- [Project rules (mandatory)](#project-rules-mandatory)
- [Claude collaboration guidelines](#claude-collaboration-guidelines)
  - [1. Think before acting](#1-think-before-acting)
  - [2. Simplicity first](#2-simplicity-first)
  - [3. Surgical edits](#3-surgical-edits)
  - [4. Goal-driven execution](#4-goal-driven-execution)
- [Project overview](#project-overview)
- [Install and run](#install-and-run)
- [Architecture](#architecture)
- [Development conventions](#development-conventions)
- [Version control](#version-control)
- [Admin tools](#admin-tools)
- [Backlog](#backlog)
- [Notes](#notes)

## Claude collaboration guidelines

### 1. Think before acting

**Do not assume, do not hide uncertainty, and surface trade-offs proactively.**

Before implementing:

- State assumptions explicitly; if unsure, ask.
- If multiple interpretations exist, list them all—do not silently pick one.
- If a simpler approach exists, say so; push back when warranted.
- If anything is unclear, stop, explain what is unclear, then ask.

### 2. Simplicity first

**Solve the problem with the least code; no speculative implementation.**

- Do not implement features that were not requested.
- Do not abstract one-off code.
- Do not add unrequested “flexibility” or “configurability.”
- Do not add error handling for impossible cases.
- If you wrote 200 lines but 50 would do, rewrite.

Ask yourself: “Would a senior engineer call this over-engineered?” If yes, simplify.

### 3. Surgical edits

**Change only what must change; clean up only mess you created.**

When editing existing code:

- Do not “while I’m here” improvements to nearby code, comments, or formatting.
- Do not refactor things that are not broken.
- Match existing style even if you would write it differently.
- If you find unrelated dead code, call it out—do not delete it on your own.

When your change creates orphans:

- Remove imports / variables / functions made unused **by your change**.
- Do not remove pre-existing dead code unless asked.

Litmus test: every changed line should trace directly to the user’s request.

### 4. Goal-driven execution

**Define success criteria and loop until verified.**

Turn tasks into verifiable goals:

- “Add validation” → “Write tests for invalid input, then make them pass”
- “Fix bug” → “Write a test that reproduces the bug, then make it pass”
- “Refactor X” → “Ensure tests pass before and after refactor”

For multi-step work, state a short plan first:

```text
1. [step] → verify: [checkpoint]
2. [step] → verify: [checkpoint]
3. [step] → verify: [checkpoint]
4. Update backlog → verify: PHASES.md “Completed” or “Backlog” reflects the change
```

---

**When these guidelines work:** fewer unnecessary diffs, fewer rewrites from over-design, and clarification happens before implementation—not after mistakes.

## Project overview

**cyber_mud** is a text-based multiplayer adventure game (MUD) set in cyberpunk **Night City** (original narrative inspired by Blade Runner + Cyberpunk 2077 atmosphere). Players explore, interact with NPCs, solve puzzles, and fight via text commands.

This repo was forked from the original **mud** project: MVP code skeleton plus full implementation docs (see `docs/`).

**Core principles**

1. **English default locale** — see [Project rules (mandatory)](#project-rules-mandatory); `lang zh` is opt-in.
2. **Built-in client** — no reliance on external MUD clients.

- The primary player interface is this repo’s `client/` (Textual TUI).
- MUDlet, TinTin++, `nc`, etc. are not the official way to play.
- The server keeps a TCP newline text protocol for debugging; product experience is defined by the built-in client.

**Already shipped:** login/saves, items, combat, NETRUN, tick, sidebar (PDA / map / equipment), Tab completion, auto-reconnect, `--dev` hot-reload, and more—full list in [`docs/PHASES.md`](docs/PHASES.md) “Completed (from Backlog)”.  
**Still to expand:** see [`docs/PHASES.md`](docs/PHASES.md#backlog).

## Install and run

Environment: Python **3.13**; prefer **pyenv** virtualenv `cyber-mud-3.13.12` (see `.python-version`), otherwise `setup.sh` will try to create `.venv`.

```bash
# First-time setup
./setup.sh

# Start server
./run.sh

# Built-in TUI client (separate terminal)
./run.sh --client

# Dev mode (data + code hot-reload)
./run.sh --dev
```

## Architecture

| Module | Responsibility |
|--------|----------------|
| `server/` | Connection management, command parsing, game loop |
| `client/` | Textual TUI client (primary player interface) |
| `shared/` | Client/server shared protocol and constants |
| `world/` | Map, rooms, clock, weather, tick (partially planned) |
| `entities/` | Players, NPCs, items |
| `commands/` | Command handlers (`look`, `go`, `take`, `say`, etc.) |
| `data/` | World definitions (YAML) and `locale/` copy |
| `combat/` | Real-time combat (planned) |
| `persistence/` | Saves (planned) |

**Documentation policy:** Project docs use split English / Traditional Chinese markdown files. **English `.md` files are canonical on GitHub** and for agents; Chinese mirrors live alongside as `*.zh.md`. When adding or updating docs, maintain both files and link to the English default.

Full doc index (English default; `*.zh.md` mirrors where listed):

| Doc | Purpose |
|-----|---------|
| [`docs/WORLD.md`](docs/WORLD.md) ([`WORLD.zh.md`](docs/WORLD.zh.md)) | World setting, districts, factions |
| [`docs/IMPLEMENTATION.md`](docs/IMPLEMENTATION.md) ([`IMPLEMENTATION.zh.md`](docs/IMPLEMENTATION.zh.md)) | Implementation blueprint |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) ([`ARCHITECTURE.zh.md`](docs/ARCHITECTURE.zh.md)) | System architecture |
| [`docs/BOOTSTRAP.md`](docs/BOOTSTRAP.md) ([`BOOTSTRAP.zh.md`](docs/BOOTSTRAP.zh.md)) | MVP bootstrap steps |
| [`docs/PHASES.md`](docs/PHASES.md) ([`PHASES.zh.md`](docs/PHASES.zh.md)) | Phased delivery checklist |
| [`docs/CLIENT_UI_DEBUG.md`](docs/CLIENT_UI_DEBUG.md) ([`CLIENT_UI_DEBUG.zh.md`](docs/CLIENT_UI_DEBUG.zh.md)) | Client layout / sidebar debug cases and delivery checklist |
| [`docs/LOCALIZATION.md`](docs/LOCALIZATION.md) ([`LOCALIZATION.zh.md`](docs/LOCALIZATION.zh.md)) | Bilingual policy (English primary + zh) |
| [`docs/WORLD_TOOLS.md`](docs/WORLD_TOOLS.md) ([`WORLD_TOOLS.zh.md`](docs/WORLD_TOOLS.zh.md)) | World grid / population / quest authoring CLI |

## Development conventions

- Language: Python 3.13 (virtualenv `cyber-mud-3.13.12` or `.venv`)
- UI: Textual + Rich (`client/`)
- Transport: TCP newline text protocol (`shared/protocol.py`)
- World data separate from code; add rooms in `data/` first, not hardcoded in logic
- Command handling is registry-based; one module per command under `commands/`
- **English default locale (mandatory):** see [Project rules](#project-rules-mandatory); `en.yaml` + `zh.yaml` in lockstep ([`docs/LOCALIZATION.md`](docs/LOCALIZATION.md))
- **Documentation:** split `*.md` (English, canonical) + `*.zh.md` (mirror); update both when changing project docs
- Tests: `pytest tests/`; after changing commands or world logic, run related tests
- Runtime: `PYTHONPATH` points at repo root (`run.sh` / `admin.sh` handle this)

## Version control

This project uses git (local repo; remote is configurable).

### Commit convention

**One commit per major item**—do not mix unrelated features in a single commit.

Major item examples:

- Finish one Phase 0 sub-item (e.g. login/saves)
- Add a command group (e.g. `take` / `drop` / `inventory`)
- Finish a client TUI feature (sidebar, autocomplete)
- Expand world data and mechanics
- Tests filled in and `pytest` all green

### Multi-session sync (before coding)

Parallel agents or a new chat **must** align with the repo first:

```bash
git fetch origin 2>/dev/null || true
git status -sb && git log --oneline -15
pytest tests/ -q --tb=no
```

Read [`docs/PHASES.md`](docs/PHASES.md) **Backlog** and recent **Completed** rows—do not duplicate work already committed.

Workflow:

1. Finish one major item → run `pytest tests/` or `./admin.sh validate`
2. **Update backlog** → [`docs/PHASES.md`](docs/PHASES.md) “Completed” or “Backlog”; sync this file’s Backlog summary tables
3. On pass, `git add` relevant files → `git commit`
4. `git push` when needed

Commit message format: **English subject** `<type>: <EN summary>`, optional Traditional Chinese suffix ` / <中文簡述>` (e.g. `feat: add item system / 新增物品系統`).

**Backlog is mandatory:** any fix or client/server behavior change must be recorded in PHASES before delivery—not code-only changes.

## Admin tools

```bash
./admin.sh validate      # validate world data + run tests
```

(Original mud `saves` / `delete-save` commands await persistence implementation.)

## Backlog

Master list: [`docs/PHASES.md`](docs/PHASES.md).

### Pending

| Area | Items |
|------|--------|
| Environment | pyenv native Python build |
| **Client log UX** | CL.1–CL.8 shipped — log channels, `LogPalette`, block separators; see PHASES **Client log UX** |
| **World expansion (WORLD.md)** | W.1–W.14 shipped (263 rooms / 121 NPCs / 45 items); see PHASES **World expansion** |
| **Content depth** | D.1–D.10 shipped (spotlight NPCs, district quests, grid look flavor); see PHASES **Content depth** |

NSFW copy lives in `data/locale/mature_*.yaml`; default `teen` rating; M.0–M.7 shipped — see PHASES **Mature / NSFW content** table.

Recent completions (2026-06) summary:

| Item | Module / acceptance |
|------|---------------------|
| Client main UI modernization | `client/tui_styles.py`, `client/ui_format.py` |
| Login / layout fixes | Input field visible, art height, RichLog does not steal focus |
| Sidebar fixes | `room_id` refreshes map, prefer `@ui` JSON |
| Item / NPC English suffix | `shared/locale_content.py` → `look` / `scan` / `inventory` |
| Tab auto-completion | `shared/completion.py`, `client/completion.py`, `@meta complete_*` |
| Hotkey bar | `#hotkey_bar` (Tab, F2–F6, `/reconnect`); chrome / hotkey `min-height:1`; input-panel commands auto-open sidebar; non-blocking F-key fetch |
| Output animation prefix | `client/output_prefix.py` (Braille spinner) |
| Client reconnect | `client/reconnect.py`, disconnect backoff, `/reconnect`, resend auth |
| Server code hot-reload | `server/code_reload.py`, `server/dev_reload.py`, `./run.sh --dev` |
| Client spinner in-progress indicator | Animate only the in-flight command line; stop when done |
| Client status animation indicator | Status-bar icons spin during combat / gigs / low HP / NETRUN |
| Combat CD countdown (seconds) | `client/cd_display.py`, second-level `combat_cd` meta, live hint / log countdown |
| Combat ends when NPC leaves room | `npc_in_player_room`, `resolve_npc_departed`; end encounter when patrolling enemy exits |
| Tab completion fix | `MudPrompt` intercepts Tab, `_apply_prompt_completion` sync fallback |
| Combat pacing speed-up | `combat_tick_loop` every 3s; attack CD 3s, NPC counter 6s |
| Performance optimizations | Silent CD tick, lean combat meta, lower client spinner frequency |
| Sidebar stack | `sidebar_stack` shows PDA + map together; F2–F5 toggle overlay |
| Startup status | `StartupReport` load timing; server terminal + client hint |
| Client input history | ↑↓ command history, Esc restore, `command_history.json` persistence |
| Client saved credentials / PIN | `client/credentials.py` encrypted storage, PIN quick login, F7 clear memory |
| `look` target inspection | `look <target>` shows item / NPC / equipment state and stats |
| NPC corpses and looting | `world/corpses.py` knockdown leaves corpse, loot, decay drops |
| Corpse English suffix | `corpse_label` shows `(English)` / `(corpse)` for command entry |
| Tutorial zone expansion | Training ground 9 rooms, 10 NPCs, 4 interactables; briefing / cafeteria / obstacle course / sim clinic; `tests/test_tutorial_zone.py` |
| Shop and trading | `shop` / `buy` / `sell`; `data/shops.yaml`; starting cash on register |
| Environment output coloring | `client/env_format.py` colorized `look` / `scan` |
| Environment colors follow theme | `client/themes.py` `EnvPalette`; `/theme` syncs environment colors |
| Consumables system | `use` / `eat` / `drink`; food / drink / meds; `world/consumables.py` |
| NETRUN command passthrough | Client no longer blocks `hack` / `probe` / `status` |
| NPC equipped gear | `entities/npc.py` `equipment`; shown in `look`; drops on knockdown |
| Natural HP recovery | `world/vitals.py` regen by body / cool / time period tick |
| NPC respawn | `world/npc_respawn.py` knockdown schedule; `respawn_minutes` / `tier: boss` |
| Command repeat | `10 punch` / `punch.10` multi-execution |
| Server heartbeat | `server/heartbeat.py` periodic terminal status refresh; dev reload log |
| CP2077 equipment slots and weapon types | `shared/equipment.py` seven slots; CP2077 ranged types + power / tech / smart / melee; `armor` save migration |
| NETRUN English suffix | `net_node_label_with_id`; NETRUN nodes / ground items `(English)`; `hack` Tab completion |
| NETRUN environment / NPC interaction | `look` / `scan` / `talk` / `say` allowed during NETRUN; environment shows hackable nodes |
| Weapon hold modes | `weapon_primary` / `weapon_secondary`; `weapon_mode` primary / secondary / two-hand / dual-wield |
| Level / skills / talents | `world/progression.py`; `stats` / `talents` / `improve`; `data/talents.yaml`; knockdown / hack XP |
| Street cred and gigs | `street_cred`; `gigs`; `world/quests.py`; `broker_rumor` turn-in rewards |
| CP2077 quickhacks | `data/quickhacks.yaml`; overheat / short circuit / reboot optics / synapse burn; combat status effects |
| Cyberware psychosis | `world/cyberpsychosis.py` low humanity damage penalty |
| CP2077 cyberware slots | Nine slots cyberware / install / uninstall; `data/implants.yaml` |
| Housing and stash | `rent` / `home` / `stash`; `watson_flat` |
| Transit and vehicles | `transit`; `vehicles buy` / `drive` |

### To do (excerpt)

Maintenance rules: [`docs/PHASES.md`](docs/PHASES.md#backlog-維護慣例)—**update backlog for every fix or change going forward**.



### Recently completed (2026-06 backlog batch)

| Item | Module / acceptance |
|------|---------------------|
| Tab multi-candidate cycling | `complete_input_cycle`, `client/app.py` |
| Environment interactables | `interact`, `data/interactables.yaml`, `look` / `scan` |
| Vertical movement (up/down) | `go up/down`, `u`/`d`, rooftop / underground areas |
| Prompt tokens | `%l` `%c` `%v` `%x`, `prompt template ncpd` |
| Multi-stage gigs | `dock_watch`, `world/quests.py` stages |
| Time-period balance | `world/modifiers.py` period modifiers |
| Cyberware passive chains | `passive_chains.yaml`, `combat/passives.py` |
| NCPD wanted level | `world/wanted.py`, tick decay |
| Vehicle garage | `vehicles buy/select`, `vehicles[]` |
| Craft / disassemble / braindance | `craft` / `disassemble` / `braindance`, `tests/test_backlog_features.py` |
| NPC faction motive AI | `world/npc_ai.py`, `corp_scout` / `thug` faction conflict, `tests/test_npc_ai.py` |
| Login banner dynamic MOTD | `client/login_motd.py`, `motd.tips` rotation, `tests/test_login_motd.py` |
| Full prompt (client live preview) | `client/prompt_preview.py`, `#prompt_preview`, `tests/test_prompt_preview.py` |
| NPC quest authoring tool | `world/quest_author.py`, `./admin.sh quests`, `tests/test_quest_author.py` |
| Full quest system | `gigs accept` / `journal`, `defeat_npc` / `have_item`, `alley_clearance`, `tests/test_quest_system.py` |
| Help log-area dropdown | `client/help_overlay.py`, `#help_dropdown` overlays log, `tests/test_help_overlay.py` |
| Tutorial zone second expansion | 4 new rooms, 6 tutorial NPCs, `patrol_dummy`, 4 interactables, supply depot new stock; `tests/test_tutorial_zone.py` |
| Gigs sidebar tracking | `gigs` / `journal` sidebar panel, F7 hotkey, auto-refresh quest progress; `tests/test_gigs.py` |
| Help command categories | `HELP_CATEGORIES` 15 categories; F3 overlay category headers; `tests/test_help_cmd.py` |
| Focus tracking block | Grok-style gradient block above prompt; gigs / combat / command execution; theme color + icons; `tests/test_focus_block.py` |
| Client clear log | `/clear` local command; `AnimatedLogBuffer.clear()`; Tab completion; `tests/test_client_app.py` |
| Split EN/ZH documentation | `*.zh.md` mirrors; English default on GitHub; README ASCII banner |
| English default locale in project rules | `CLAUDE.md` § Project rules (mandatory); `LOCALIZATION.md`; README core principle #1 |
| Project licenses | `LICENSE` Apache 2.0; `LICENSE-CONTENT.md` CC BY 4.0; `CONTRIBUTING.md` |
| Player guides (GitHub) | `docs/player/` — getting started, tutorial, commands, client (ASCII art) |
| Mature / NSFW content M.0–M.7 | `world/mature.py`, `combat/gore.py`, `settings mature`, `flirt`, mature locale/YAML, client 18+ login |
| Kabuki & district expansion | `kabuki_vip`, `kabuki_bazaar`, Little China, Corpo hubs; `velvet_job`; `tests/test_world_districts.py` |
| World expansion W.8–W.10 | `data/schedule.yaml`; `docks_gray`/`gray_market`; corp/street `appraise`; `give` to NPC; `presence` on `go`; `tests/test_black_market.py`, `tests/test_multiplayer.py` |
| World expansion W.12–W.13 | `poison`/`antidote`; player `overheat`; `world/reactions.py` rep + ambient tick; `tests/test_status_effects.py`, `tests/test_world_reactions.py` |
| World expansion W.14 | `tools/expand_world_population.py`; `world_population.yaml`; 109 NPCs / 45 items; `tests/test_world_scale.py` |
| Content depth D.1–D.6 | Archetype `talk.*`; quest WARN fixes + `hub_briefing`; hub NPCs; grid craft/shops; 8 net nodes + interactables; `tests/test_content_depth.py` |
| Content depth D.7–D.10 | 8 spotlight NPCs; `district.grid.*` look flavor; 4 district quests; `world.ambient.*` all districts; `tests/test_content_depth.py` |
| Client layout test helpers | `tests/client_ui_helpers.py`; stable sidebar/help overlay assertions |
| Life commands L.1–L.8 | `sit`/`stand`/`lie`/`rest`/`sleep`/`wake`; `world/life.py`, `data/life.yaml`; interactable anchors; vitals/RAM regen; PDA + `%posture`; `tests/test_life_commands.py` |

World setting and district expansion: [`docs/WORLD.md`](docs/WORLD.md) ([`WORLD.zh.md`](docs/WORLD.zh.md)).

## Notes

- World lore is original homage-style content, not official Cyberpunk / Blade Runner canon.
- Before extending features, read `docs/PHASES.md` and `docs/IMPLEMENTATION.md` to avoid conflicting with existing protocol.
- Before changing `client/` layout or sidebar, read [`docs/CLIENT_UI_DEBUG.md`](docs/CLIENT_UI_DEBUG.md) ([`CLIENT_UI_DEBUG.zh.md`](docs/CLIENT_UI_DEBUG.zh.md)); pair with project skill `.grok/skills/cyber-mud-client-ui/`.
- For repeatable workflows, encapsulate as a skill (`.grok/skills/` or `.claude/skills/`); format reference: [andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills).