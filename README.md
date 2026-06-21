```text
╔══════════════════════════════════════════════════════════════════════════╗
║  ██████╗██╗   ██╗██████╗ ███████╗██████╗     ███╗   ███╗██╗   ██╗██████╗ ║
║ ██╔════╝╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗    ████╗ ████║██║   ██║██╔══██╗║
║ ██║      ╚████╔╝ ██████╔╝█████╗  ██████╔╝    ██╔████╔██║██║   ██║██║  ██║║
║ ██║       ╚██╔╝  ██╔══██╗██╔══╝  ██╔══██╗    ██║╚██╔╝██║██║   ██║██║  ██║║
║ ╚██████╗   ██║   ██████╔╝███████╗██║  ██║    ██║ ╚═╝ ██║╚██████╔╝██████╔╝║
║  ╚═════╝   ╚═╝   ╚═════╝ ╚══════╝╚═╝  ╚═╝    ╚═╝     ╚═╝ ╚═════╝ ╚═════╝ ║
║                  ▸  N E O N   N I G H T   C I T Y  ◂                     ║
╚══════════════════════════════════════════════════════════════════════════╝
```

[![GitHub](https://img.shields.io/badge/GitHub-0xd3adcafe%2Fcyber__mud-181717?logo=github)](https://github.com/0xd3adcafe/cyber_mud)
[![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)](.python-version)
[![Textual](https://img.shields.io/badge/Client-Textual_TUI-00D4AA)](https://textual.textualize.io/)
[![Cyberpunk MUD](https://img.shields.io/badge/Genre-Cyberpunk_MUD-FF00FF)](docs/WORLD.md)
[![Locale](https://img.shields.io/badge/Locale-en+zh-00D4AA)](docs/LOCALIZATION.md)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-2563EB)](LICENSE)
[![Content: CC BY 4.0](https://img.shields.io/badge/Content-CC_BY_4.0-7C3AED)](LICENSE-CONTENT.md)
[![中文](https://img.shields.io/badge/中文-README.zh.md-red)](README.zh.md)

Cyberpunk text MUD set in **Night City** — jack in, take gigs, hack the grid, and survive the after-dark economy. **263 rooms**, **109 NPCs**, full Python codebase, and a built-in **Textual TUI** — play in-repo, not through a legacy MUD client.

**Default locale: English.** Use `lang zh` in-game for Traditional Chinese. See [docs/LOCALIZATION.md](docs/LOCALIZATION.md).

**中文說明：** [README.zh.md](README.zh.md)

## Table of contents

- [Why jack in?](#why-jack-in)
  - [Play the city](#play-the-city)
  - [Optional 18+ (opt-in)](#optional-18-opt-in)
  - [Built for players and builders](#built-for-players-and-builders)
- [Player guides (read on GitHub)](#player-guides-read-on-github)
- [Agent guide](#agent-guide)
- [Documentation](#documentation)
- [Reading order](#reading-order)
- [Core principles](#core-principles)
- [Quick start](#quick-start)
- [Git](#git)
- [License](#license)

---

```text
  ◈ WHY JACK IN ── homage worlds, optional 18+, play tonight
```

## Why jack in?

Original Night City fiction with **homage vibes** you will recognize — neon rain and corporate dystopia (**Blade Runner**), street cred, cyberware, and quickhacks (**Cyberpunk 2077**), plus a **Watch Dogs**-style surveillance-hacking roadmap (profiler, ctOS hacks, digital footprint). Not official IP; built to *feel* like the worlds you already love.

```text
  · PLAY THE CITY ·
```

### Play the city

| | |
|---|---|
| **Explore** | Districts, rooftops, underground, transit, vehicles, housing & stash |
| **Fight** | Real-time combat, CP2077 weapon types, quickhacks, taunt/finish, corpses & loot |
| **Run the net** | NETRUN nodes, `hack` / `probe`, RAM, environment interaction mid-run |
| **Live the grind** | Gigs & journal, street cred, shops, craft, braindance, NCPD heat, faction AI |
| **Grow** | Levels, talents, nine cyberware slots, romance scaffolding, `sit` / `rest` / `sleep` vitals |

Tutorial yard onboarding → Watson flats → Kabuki clubs and corpo hubs. Type `look`, `scan`, `go`, `talk`, `gigs` — the city answers back.

```text
  · OPTIONAL 18+ ·
```

### Optional 18+ (opt-in)

Mature content is **off by default** (`teen` rating). Register with `mature` or `settings mature on` to unlock 18+ venues, romance beats, mature gigs/braindances, and grittier combat copy — gated at login and command layer. Pack lives in private **`cyber_mud_mature`**; public clones stay teen-safe. See [docs/MATURE_CONTENT.md](docs/MATURE_CONTENT.md).

```text
  · PLAYERS & BUILDERS ·
```

### Built for players and builders

- **Textual TUI** — sidebar PDA, live map, equipment, gigs tracker, Tab completion, `/theme` (incl. ctOS / DedSec / Profiler skins), auto-reconnect  
- **Data-driven world** — rooms, NPCs, quests, and locale in YAML; `./run.sh --dev` hot-reloads data and code  
- **Bilingual** — `en` default, `zh` opt-in; player guides under [docs/player/](docs/player/README.md)  
- **Agent-friendly repo** — [CLAUDE.md](CLAUDE.md), phased backlog [PHASES.md](docs/PHASES.md), `./admin.sh validate`

```bash
./setup.sh && ./run.sh          # server
./run.sh --client               # jack in — this is the real game
```

---

```text
  ◈ NEURAL LINK DOCS ── jack in before you connect
```

## Player guides (read on GitHub)

| Guide | For players |
|-------|-------------|
| **[docs/player/README.md](docs/player/README.md)** | Start here — tutorial, commands, client |
| [Getting Started](docs/player/GETTING_STARTED.md) | Install, login, first `look` |
| [Tutorial](docs/player/TUTORIAL.md) | Training yard walkthrough |
| [Commands](docs/player/COMMANDS.md) | Full command matrix |
| [Client & Hotkeys](docs/player/CLIENT.md) | F2–F7, `/theme`, `/clear` |

繁中：[docs/player/README.zh.md](docs/player/README.zh.md)

---

```text
  ◈ AGENT GUIDE ── rules for humans and AI collaborators
```

## Agent guide

Collaboration rules: **[CLAUDE.md](CLAUDE.md)** (behavior guidelines reference `andrej-karpathy-skills.md`).

---

```text
  ◈ DOCUMENTATION ── world, architecture, phases
```

## Documentation

| Doc | Purpose |
|-----|---------|
| [CLAUDE.md](CLAUDE.md) | Agent collaboration & dev conventions |
| [docs/LOCALIZATION.md](docs/LOCALIZATION.md) | **Bilingual policy** (en primary + zh mirrors) |
| [docs/WORLD.md](docs/WORLD.md) | World setting, districts, factions |
| [docs/IMPLEMENTATION.md](docs/IMPLEMENTATION.md) | Implementation blueprint |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | System architecture |
| [docs/BOOTSTRAP.md](docs/BOOTSTRAP.md) | MVP bootstrap steps |
| [docs/PHASES.md](docs/PHASES.md) | Phased delivery checklist |
| [docs/WORLD_TOOLS.md](docs/WORLD_TOOLS.md) | World grid / population / quest authoring CLI |

Chinese mirrors: same paths with `.zh.md` suffix (e.g. [docs/WORLD.zh.md](docs/WORLD.zh.md)).

---

```text
  ◈ READING ORDER ── five docs, one path in
```

## Reading order

1. [WORLD.md](docs/WORLD.md) — what Night City is  
2. [ARCHITECTURE.md](docs/ARCHITECTURE.md) — system overview  
3. [BOOTSTRAP.md](docs/BOOTSTRAP.md) — minimal playable build  
4. [IMPLEMENTATION.md](docs/IMPLEMENTATION.md) — module details  
5. [PHASES.md](docs/PHASES.md) — schedule & acceptance

---

```text
  ◈ CORE PRINCIPLES ── how this repo is built
```

## Core principles

1. **English default locale (mandatory)** — `locale=en` at runtime; `lang zh` is opt-in. See [CLAUDE.md](CLAUDE.md) § Project rules and [docs/LOCALIZATION.md](docs/LOCALIZATION.md).  
2. **Built-in Textual client** — no third-party MUD clients for production play.  
3. **World in `data/`** — code interprets YAML, not hardcoded rooms.  
4. **One command per module** under `commands/`.  
5. **Bilingual mirrors** — `en.yaml` + `zh.yaml`, English `*.md` + `*.zh.md`.

---

```text
  ◈ QUICK START ── two terminals, one neural link
```

## Quick start

First time? Read [Getting Started](docs/player/GETTING_STARTED.md) — register, `look`, leave the tutorial yard.

```bash
cd cyber_mud
./setup.sh          # first run: install deps
./run.sh            # start server
./run.sh --client   # another terminal: TUI client
./admin.sh validate # validate world data + tests
```

---

```text
  ◈ GIT ── commits and backlog hygiene
```

## Git

Runtime data (`data/saves/`, `data/world_state.json`) and `.venv/` are not tracked.

```bash
git status
./admin.sh validate
git commit -m "feat: short English summary / 可選中文簡述"
```

Convention: one commit per major feature; update [PHASES.md](docs/PHASES.md) backlog before commit.

---

```text
  ◈ LICENSE ── code vs world content
```

## License

| Layer | License | File |
|-------|---------|------|
| **Code** | [Apache License 2.0](LICENSE) | `server/`, `client/`, `commands/`, tests, scripts |
| **World content** | [CC BY 4.0](LICENSE-CONTENT.md) | `data/` narrative, `data/locale/` copy, world lore docs |

Contributions: see [CONTRIBUTING.md](CONTRIBUTING.md). AI-assisted patches welcome; submitter reviews and accepts the licenses above.