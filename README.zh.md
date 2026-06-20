# cyber_mud

> **English:** [README.md](README.md)

[![GitHub](https://img.shields.io/badge/GitHub-0xd3adcafe%2Fcyber__mud-181717?logo=github)](https://github.com/0xd3adcafe/cyber_mud)
[![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)](.python-version)
[![Textual](https://img.shields.io/badge/Client-Textual_TUI-00D4AA)](https://textual.textualize.io/)
[![Cyberpunk MUD](https://img.shields.io/badge/Genre-Cyberpunk_MUD-FF00FF)](docs/WORLD.zh.md)
[![Locale](https://img.shields.io/badge/Locale-en+zh-00D4AA)](docs/LOCALIZATION.zh.md)

賽博龐克文字 MUD，背景為**夜城**。由原 **mud** 專案 fork，含 MVP 程式骨架與完整實作文件。

內建 **Textual TUI client** 為正式玩家介面（`look`／`go`／`help`／`quit` 與起始世界）。

**預設語系為英文**；遊戲內輸入 `lang zh` 可切換繁體中文。雙語慣例見 [docs/LOCALIZATION.zh.md](docs/LOCALIZATION.zh.md)。

## 協作指引

Agent 行為準則：**[CLAUDE.zh.md](CLAUDE.zh.md)**

## 文件

| 文件 | 用途 |
|------|------|
| [CLAUDE.zh.md](CLAUDE.zh.md) | Agent 協作與開發慣例 |
| [docs/LOCALIZATION.zh.md](docs/LOCALIZATION.zh.md) | **雙語政策**（英文主述 + 中文對照） |
| [docs/WORLD.zh.md](docs/WORLD.zh.md) | 世界觀、區域、派系 |
| [docs/IMPLEMENTATION.zh.md](docs/IMPLEMENTATION.zh.md) | 實作藍圖 |
| [docs/ARCHITECTURE.zh.md](docs/ARCHITECTURE.zh.md) | 系統架構 |
| [docs/BOOTSTRAP.zh.md](docs/BOOTSTRAP.zh.md) | MVP 啟動步驟 |
| [docs/PHASES.zh.md](docs/PHASES.zh.md) | 分階段實作清單 |

英文版（GitHub 預設）：同路徑無 `.zh` 後綴，例如 [docs/WORLD.md](docs/WORLD.md)。

## 建議閱讀順序

1. [WORLD.zh.md](docs/WORLD.zh.md) — 夜城是什麼  
2. [ARCHITECTURE.zh.md](docs/ARCHITECTURE.zh.md) — 系統總覽  
3. [BOOTSTRAP.zh.md](docs/BOOTSTRAP.zh.md) — 最小可玩版本  
4. [IMPLEMENTATION.zh.md](docs/IMPLEMENTATION.zh.md) — 模組細節  
5. [PHASES.zh.md](docs/PHASES.zh.md) — 排程與驗收

## 核心原則

1. **英文為預設語系（強制）** — 執行時 `locale=en`；`lang zh` 為選用。見 [CLAUDE.zh.md](CLAUDE.zh.md) § 專案規則與 [docs/LOCALIZATION.zh.md](docs/LOCALIZATION.zh.md)。  
2. **內建 Textual client** 為正式介面。  
3. **世界放 `data/`**，程式只負責解讀。  
4. **一指令一模組**，`commands/` 註冊制。  
5. **雙語對照** — `en.yaml` + `zh.yaml`；英文 `*.md` + 中文 `*.zh.md`。

## 快速開始

```bash
./setup.sh && ./run.sh
./run.sh --client
./admin.sh validate
```

## Commit

```
feat: English summary / 中文簡述（可選）
```

變更須同步 [PHASES.zh.md](docs/PHASES.zh.md) backlog。