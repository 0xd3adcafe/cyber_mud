```text
╔══════════════════════════════════════════════════════════════════════════╗
║  ██████╗██╗   ██╗██████╗ ███████╗██████╗     ███╗   ███╗██╗   ██╗██████╗ ║
║ ██╔════╝╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗    ████╗ ████║██║   ██║██╔══██╗║
║ ██║      ╚████╔╝ ██████╔╝█████╗  ██████╔╝    ██╔████╔██║██║   ██║██║  ██║║
║ ██║       ╚██╔╝  ██╔══██╗██╔══╝  ██╔══██╗    ██║╚██╔╝██║██║   ██║██║  ██║║
║ ╚██████╗   ██║   ██████╔╝███████╗██║  ██║    ██║ ╚═╝ ██║╚██████╔╝██████╔╝║
║  ╚═════╝   ╚═╝   ╚═════╝ ╚══════╝╚═╝  ╚═╝    ╚═╝     ╚═╝ ╚═════╝ ╚═════╝ ║
║                    ▸  N E O N   N I G H T   C I T Y  ◂                    ║
╚══════════════════════════════════════════════════════════════════════════╝
```

[![GitHub](https://img.shields.io/badge/GitHub-0xd3adcafe%2Fcyber__mud-181717?logo=github)](https://github.com/0xd3adcafe/cyber_mud)
[![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)](.python-version)
[![Textual](https://img.shields.io/badge/Client-Textual_TUI-00D4AA)](https://textual.textualize.io/)
[![Cyberpunk MUD](https://img.shields.io/badge/Genre-Cyberpunk_MUD-FF00FF)](docs/WORLD.md)
[![Locale](https://img.shields.io/badge/Locale-en+zh-00D4AA)](docs/LOCALIZATION.md)
[![中文](https://img.shields.io/badge/中文-README.zh.md-red)](README.zh.md)

Cyberpunk text MUD set in **Night City**. Forked from the original **mud** project with a full MVP codebase and implementation docs.

Built-in **Textual TUI client** is the primary player interface (`look` / `go` / `help` / `quit` + starter world).

**Default locale: English.** Use `lang zh` in-game for Traditional Chinese. See [docs/LOCALIZATION.md](docs/LOCALIZATION.md).

**中文說明：** [README.zh.md](README.zh.md)

## Agent guide

Collaboration rules: **[CLAUDE.md](CLAUDE.md)** (behavior guidelines reference `andrej-karpathy-skills.md`).

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

Chinese mirrors: same paths with `.zh.md` suffix (e.g. [docs/WORLD.zh.md](docs/WORLD.zh.md)).

## Reading order

1. [WORLD.md](docs/WORLD.md) — what Night City is  
2. [ARCHITECTURE.md](docs/ARCHITECTURE.md) — system overview  
3. [BOOTSTRAP.md](docs/BOOTSTRAP.md) — minimal playable build  
4. [IMPLEMENTATION.md](docs/IMPLEMENTATION.md) — module details  
5. [PHASES.md](docs/PHASES.md) — schedule & acceptance

## Core principles

1. **English default locale (mandatory)** — `locale=en` at runtime; `lang zh` is opt-in. See [CLAUDE.md](CLAUDE.md) § Project rules and [docs/LOCALIZATION.md](docs/LOCALIZATION.md).  
2. **Built-in Textual client** — no third-party MUD clients for production play.  
3. **World in `data/`** — code interprets YAML, not hardcoded rooms.  
4. **One command per module** under `commands/`.  
5. **Bilingual mirrors** — `en.yaml` + `zh.yaml`, English `*.md` + `*.zh.md`.

## Quick start

```bash
cd cyber_mud
./setup.sh          # first run: install deps
./run.sh            # start server
./run.sh --client   # another terminal: TUI client
./admin.sh validate # validate world data + tests
```

## Git

Runtime data (`data/saves/`, `data/world_state.json`) and `.venv/` are not tracked.

```bash
git status
./admin.sh validate
git commit -m "feat: short English summary / 可選中文簡述"
```

Convention: one commit per major feature; update [PHASES.md](docs/PHASES.md) backlog before commit.