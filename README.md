# cyber_mud

[![GitHub](https://img.shields.io/badge/GitHub-0xd3adcafe%2Fcyber__mud-181717?logo=github)](https://github.com/0xd3adcafe/cyber_mud)
[![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)](.python-version)
[![Textual](https://img.shields.io/badge/Client-Textual_TUI-00D4AA)](https://textual.textualize.io/)
[![Cyberpunk MUD](https://img.shields.io/badge/Genre-Cyberpunk_MUD-FF00FF)](docs/WORLD.md)
[![Locale](https://img.shields.io/badge/Locale-en+zh-00D4AA)](docs/LOCALIZATION.md)

Cyberpunk text MUD set in **Night City**. Forked from the original **mud** project with a full MVP codebase and implementation docs.

Built-in **Textual TUI client** is the primary player interface (`look` / `go` / `help` / `quit` + starter world).

**Default locale: English.** Use `lang zh` in-game for Traditional Chinese. See [docs/LOCALIZATION.md](docs/LOCALIZATION.md).

## Agent guide

Collaboration rules: **[CLAUDE.md](CLAUDE.md)** (behavior guidelines reference `andrej-karpathy-skills.md`).

## Documentation

| Doc | Purpose |
|-----|---------|
| [CLAUDE.md](CLAUDE.md) | Agent collaboration & dev conventions |
| [docs/LOCALIZATION.md](docs/LOCALIZATION.md) | **Bilingual policy** (en primary + zh) |
| [docs/WORLD.md](docs/WORLD.md) | World setting, districts, factions |
| [docs/IMPLEMENTATION.md](docs/IMPLEMENTATION.md) | Implementation blueprint |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | System architecture |
| [docs/BOOTSTRAP.md](docs/BOOTSTRAP.md) | MVP bootstrap steps |
| [docs/PHASES.md](docs/PHASES.md) | Phased delivery checklist |

## Reading order

1. [WORLD.md](docs/WORLD.md) — what Night City is  
2. [ARCHITECTURE.md](docs/ARCHITECTURE.md) — system overview  
3. [BOOTSTRAP.md](docs/BOOTSTRAP.md) — minimal playable build  
4. [IMPLEMENTATION.md](docs/IMPLEMENTATION.md) — module details  
5. [PHASES.md](docs/PHASES.md) — schedule & acceptance

## Core principles

1. **Built-in Textual client** — no third-party MUD clients for production play.  
2. **World in `data/`** — code interprets YAML, not hardcoded rooms.  
3. **One command per module** under `commands/`.  
4. **English default**, bilingual `en` + `zh` locale files.

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

---

## 中文

賽博龐克文字 MUD，背景為**夜城**。由原 **mud** 專案 fork，含 MVP 程式骨架與完整實作文件。

**預設語系為英文**；遊戲內輸入 `lang zh` 可切換繁體中文。雙語慣例見 [docs/LOCALIZATION.md](docs/LOCALIZATION.md)。

### 核心原則

1. **內建 Textual client** 為正式介面。  
2. **世界放 `data/`**，程式只負責解讀。  
3. **一指令一模組**，`commands/` 註冊制。  
4. **英文為預設**，`data/locale/en.yaml` 與 `zh.yaml` 並行維護。

### 快速開始

```bash
./setup.sh && ./run.sh
./run.sh --client
```

### Commit

```
feat: English summary / 中文簡述（可選）
```

變更須同步 [PHASES.md](docs/PHASES.md) backlog。