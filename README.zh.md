# cyber_mud

> **English:** [README.md](README.md)

[![GitHub](https://img.shields.io/badge/GitHub-0xd3adcafe%2Fcyber__mud-181717?logo=github)](https://github.com/0xd3adcafe/cyber_mud)
[![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)](.python-version)
[![Textual](https://img.shields.io/badge/Client-Textual_TUI-00D4AA)](https://textual.textualize.io/)
[![Cyberpunk MUD](https://img.shields.io/badge/Genre-Cyberpunk_MUD-FF00FF)](docs/WORLD.zh.md)
[![Locale](https://img.shields.io/badge/Locale-en+zh-00D4AA)](docs/LOCALIZATION.zh.md)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-2563EB)](LICENSE)
[![Content: CC BY 4.0](https://img.shields.io/badge/Content-CC_BY_4.0-7C3AED)](LICENSE-CONTENT.md)

賽博龐克文字 MUD，背景為**夜城**。由原 **mud** 專案 fork，含 MVP 程式骨架與完整實作文件。

內建 **Textual TUI client** 為正式玩家介面（`look`／`go`／`sit`／`rest`／`help`／`quit` 與起始世界）。

**預設語系為英文**；遊戲內輸入 `lang zh` 可切換繁體中文。雙語慣例見 [docs/LOCALIZATION.zh.md](docs/LOCALIZATION.zh.md)。

## 玩家指南（GitHub 閱讀）

```text
  ◈ 神經連結文件 ── 連線前先讀
```

| 指南 | 用途 |
|------|------|
| **[docs/player/README.zh.md](docs/player/README.zh.md)** | 從這裡開始 |
| [快速上手](docs/player/GETTING_STARTED.zh.md) | 安裝、登入 |
| [新手訓練場](docs/player/TUTORIAL.zh.md) | 訓練場攻略 |
| [指令參考](docs/player/COMMANDS.zh.md) | 完整指令 |
| [Client](docs/player/CLIENT.zh.md) | 快捷鍵與 `/` 指令 |

English: [docs/player/README.md](docs/player/README.md)

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
| [docs/WORLD_TOOLS.zh.md](docs/WORLD_TOOLS.zh.md) | 世界格點／人口／任務編寫 CLI |

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

## 授權

| 層級 | 授權 | 範圍 |
|------|------|------|
| **程式碼** | [Apache 2.0](LICENSE) | `server/`、`client/`、`commands/`、測試、腳本 |
| **世界文案** | [CC BY 4.0](LICENSE-CONTENT.md) | `data/` 敘事、`data/locale/` 文案、世界觀文件 |

貢獻方式：[CONTRIBUTING.md](CONTRIBUTING.md)。歡迎 AI 輔助開發；提交者需審閱並接受上述授權。