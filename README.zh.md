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

霓虹夜城 · 賽博龐克文字 MUD

[![GitHub](https://img.shields.io/badge/GitHub-0xd3adcafe%2Fcyber__mud-181717?logo=github)](https://github.com/0xd3adcafe/cyber_mud)
[![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)](.python-version)
[![Textual](https://img.shields.io/badge/Client-Textual_TUI-00D4AA)](https://textual.textualize.io/)
[![Cyberpunk MUD](https://img.shields.io/badge/Genre-Cyberpunk_MUD-FF00FF)](docs/WORLD.zh.md)
[![Locale](https://img.shields.io/badge/Locale-en+zh-00D4AA)](docs/LOCALIZATION.zh.md)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-2563EB)](LICENSE)
[![Content: CC BY 4.0](https://img.shields.io/badge/Content-CC_BY_4.0-7C3AED)](LICENSE-CONTENT.md)
[![English](https://img.shields.io/badge/English-README.md-blue)](README.md)

> **English（canonical）：** [README.md](README.md)

賽博龐克文字 MUD，背景為**夜城**——接入神經連結、接委託、駭入節點、在霓虹與黑市中活下去。由原 **mud** 專案 fork；**263 房**、**109 NPC**、內建 **Textual TUI**，不必另裝傳統 MUD 客戶端。

**預設語系為英文**；遊戲內輸入 `lang zh` 可切換繁體中文。雙語慣例見 [docs/LOCALIZATION.zh.md](docs/LOCALIZATION.zh.md)。

## 為什麼要接入？

原創夜城劇情，帶著你熟悉的**致敬氛圍**——霓虹雨與企業反烏托邦（**銀翼殺手**）、街頭聲望、義體與快速破解（**電馭叛客 2077**），以及 **看門狗**風格的監控駭客路線圖（Profiler、ctOS、數位足跡）。非官方授權；目的是重現你已在其他媒介愛上的那種賽博感。

### 玩法亮點

| | |
|---|---|
| **探索** | 區域、屋頂／地下、大眾運輸、載具、租屋與藏匿處 |
| **戰鬥** | 即時戰鬥、2077 武器類型、快速破解、嘲諷／終結技、屍體與掠奪 |
| **網路跑** | NETRUN 節點、`hack`／`probe`、RAM、跑酷中仍可 `look`／`scan` |
| **街頭人生** | 委託與日誌、街頭聲望、商店、製作、腦舞、NCPD 通緝、派系 AI |
| **成長** | 等級、天賦、九格義體、`sit`／`rest`／`sleep` 與生命恢復 |

新手訓練場 → 沃森公寓 → 歌舞伎俱樂部與企業中樞。輸入 `look`、`scan`、`go`、`talk`、`gigs`——城市會回應你。

### 可選 18+（自願啟用）

限制級內容**預設關閉**（`teen`）。註冊時選 `mature` 或 `settings mature on` 可解鎖 18+ 場域、浪漫劇情、限制級委託／腦舞與更血腥的戰鬥文案——登入與指令層雙重門檻。內容包在 private **`cyber_mud_mature`**；公開 clone 維持 teen 安全。見 [docs/MATURE_CONTENT.zh.md](docs/MATURE_CONTENT.zh.md)。

### 給玩家與開發者

- **Textual TUI** — 側欄 PDA、即時地圖、裝備、委託追蹤、Tab 補全、`/theme`（含 ctOS／DedSec／Profiler 主題）、自動重連  
- **資料驅動世界** — 房間、NPC、任務、語系皆 YAML；`./run.sh --dev` 熱重載資料與程式  
- **雙語** — 預設 `en`，`zh` opt-in；玩家指南見 [docs/player/](docs/player/README.zh.md)  
- **利於協作** — [CLAUDE.zh.md](CLAUDE.zh.md)、階段清單 [PHASES.zh.md](docs/PHASES.zh.md)、`./admin.sh validate`

```bash
./setup.sh && ./run.sh          # 伺服器
./run.sh --client               # 接入——這才是正式遊玩方式
```

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

首次遊玩？請讀 [快速上手](docs/player/GETTING_STARTED.zh.md)——註冊、`look`、離開訓練場。

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