# CLAUDE.md

本檔為 Claude Code、Cursor 與 Grok 在本 repo 協作時的行為指引。  
**行為準則**參考 [Andrej Karpathy Skills](https://github.com/multica-ai/andrej-karpathy-skills/blob/main/CLAUDE.md)（上層目錄 `andrej-karpathy-skills.md` 為連結）；以下合併 **cyber_mud** 專案專屬說明。

**取捨：** 準則偏向謹慎而非速度；瑣碎任務可自行判斷。

## 目錄

- [Claude 協作準則](#claude-協作準則)
  - [1. 先思考再動手](#1-先思考再動手)
  - [2. 簡單優先](#2-簡單優先)
  - [3. 手術式修改](#3-手術式修改)
  - [4. 目標導向執行](#4-目標導向執行)
- [專案說明](#專案說明)
- [安裝與執行](#安裝與執行)
- [架構說明](#架構說明)
- [開發慣例](#開發慣例)
- [版本控制](#版本控制)
- [管理工具](#管理工具)
- [Backlog](#backlog)
- [注意事項](#注意事項)

## Claude 協作準則

### 1. 先思考再動手

**不假設、不隱藏疑惑、主動點出取捨。**

實作前：

- 明確說明假設；若不確定，直接發問。
- 若存在多種解讀，全部列出，不要靜默選擇。
- 若有更簡單的做法，說出來；必要時提出反駁。
- 若有不清楚的地方，停下來，說明哪裡不清楚，再發問。

### 2. 簡單優先

**最少的程式碼解決問題，不做任何推測性實作。**

- 不實作未被要求的功能。
- 單次使用的程式碼不抽象化。
- 不加入未被要求的「彈性」或「可設定性」。
- 不對不可能發生的情況加錯誤處理。
- 若寫了 200 行但 50 行就夠，重寫。

自問：「資深工程師會說這過度複雜嗎？」如果是，就簡化。

### 3. 手術式修改

**只動必須動的部分，只清理自己製造的亂。**

修改現有程式碼時：

- 不「順便改善」鄰近程式碼、註解或格式。
- 不重構沒有損壞的東西。
- 沿用現有風格，即使你會用不同方式寫。
- 發現無關的死碼時，提出來，不要自行刪除。

當你的修改產生孤兒：

- 移除**因你的修改**而變成未使用的 import / 變數 / 函式。
- 不移除原本就存在的死碼，除非被要求。

檢驗標準：每一行修改都能直接追溯至使用者的需求。

### 4. 目標導向執行

**定義成功標準，循環直到驗證完成。**

將任務轉化為可驗證的目標：

- 「新增驗證」→「為無效輸入寫測試，再讓測試通過」
- 「修復 bug」→「寫出能重現 bug 的測試，再讓它通過」
- 「重構 X」→「確保重構前後測試均通過」

多步驟任務應先陳述簡短計畫：

```text
1. [步驟] → 驗證：[檢查點]
2. [步驟] → 驗證：[檢查點]
3. [步驟] → 驗證：[檢查點]
4. 更新 backlog → 驗證：PHASES.md「已完成」或「Backlog」已反映變更
```

---

**這些準則有效時：** diff 中不必要變更少、因過度設計而重寫的次數少、釐清問題發生在實作前而非做錯之後。

## 專案說明

**cyber_mud** 是文字型多人冒險遊戲（MUD），世界背景為賽博龐克**夜城**（致敬 Blade Runner + Cyberpunk 2077 氛圍的原創敘事）。玩家透過文字指令探索、與 NPC 互動、解謎與戰鬥。

本 repo 由原 **mud** 專案 fork 而來：含 MVP 程式骨架與完整實作文件（見 `docs/`）。

**核心原則：內建 client，不依賴外部 MUD 客戶端。**

- 主要玩家介面是本 repo 的 `client/`（Textual TUI）。
- 不使用 MUDlet、TinTin++、`nc` 等作為正式遊玩方式。
- 伺服器保留 TCP 換行文字協定供除錯；產品體驗以內建 client 為準。

**目前已具備：** 登入存檔、物品、戰鬥、NETRUN、tick、側欄（PDA／地圖／裝備）、Tab 補全、自動重連、`--dev` 熱重載等——完整清單見 [`docs/PHASES.md`](docs/PHASES.md)「已完成」。  
**待擴充：** Phase E.4 文件格式等——見 [`docs/PHASES.md`](docs/PHASES.md#backlog)。

## 安裝與執行

環境：Python **3.13**；優先 **pyenv** virtualenv `cyber-mud-3.13.12`（見 `.python-version`），否則 `setup.sh` 會嘗試建立 `.venv`。

```bash
# 首次設定
./setup.sh

# 啟動伺服器
./run.sh

# 內建 TUI client（另開終端）
./run.sh --client

# 開發模式（data + 程式碼熱重載）
./run.sh --dev
```

## 架構說明

| 模組 | 職責 |
|------|------|
| `server/` | 連線管理、指令解析、遊戲迴圈 |
| `client/` | Textual TUI 客戶端（主要玩家介面） |
| `shared/` | client/server 共用協定與常數 |
| `world/` | 地圖、房間、時鐘、天氣、tick（部分規劃中） |
| `entities/` | 玩家、NPC、物品 |
| `commands/` | 指令處理（look、go、take、say 等） |
| `data/` | 世界定義（YAML）與 `locale/` 文案 |
| `combat/` | 即時戰鬥（規劃中） |
| `persistence/` | 存檔（規劃中） |

完整文件索引：

| 文件 | 用途 |
|------|------|
| [`docs/WORLD.md`](docs/WORLD.md) | 世界觀、區域、派系 |
| [`docs/IMPLEMENTATION.md`](docs/IMPLEMENTATION.md) | 實作藍圖 |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | 系統架構 |
| [`docs/BOOTSTRAP.md`](docs/BOOTSTRAP.md) | MVP 啟動步驟 |
| [`docs/PHASES.md`](docs/PHASES.md) | 分階段實作清單 |

## 開發慣例

- 語言：Python 3.13（virtualenv `cyber-mud-3.13.12` 或 `.venv`）
- UI：Textual + Rich（`client/`）
- 通訊：TCP 換行文字協定（`shared/protocol.py`）
- 世界資料與程式碼分離；新增房間優先改 `data/`，不硬編在程式裡
- 指令處理採註冊制；每個指令一個模組，放在 `commands/`
- 回應文字使用繁體中文（`data/locale/zh.yaml` 為主）
- 測試：`pytest tests/`；修改指令或世界邏輯後必跑相關測試
- 執行時：`PYTHONPATH` 指向 repo 根目錄（`run.sh`／`admin.sh` 已處理）

## 版本控制

本專案使用 git（本機 repo；可自訂 remote）。

### Commit 慣例

**一個大項目完成就 commit 一次**——不要把多個獨立功能混在同一個 commit。

大項目範例：

- 完成 Phase 0 某一子項（如登入存檔）
- 新增一組指令（如 `take` / `drop` / `inventory`）
- 完成 client TUI 功能（側欄、自動完成）
- 擴充世界資料與機制
- 測試補齊且 `pytest` 全過

流程：

1. 完成一個大項目 → 跑 `pytest tests/` 或 `./admin.sh validate`
2. **更新 backlog** → [`docs/PHASES.md`](docs/PHASES.md)「已完成」或「Backlog」；本檔 Backlog 摘要表同步
3. 通過後 `git add` 相關檔案 → `git commit`
4. 需要時 `git push`

Commit message 格式：`<type>: <簡述>`（如 `feat: 新增物品系統`、`test: 補齊移動測試`）。

**Backlog 為必做步驟**：任何修正、client／server 行為變更，交付前都要寫入 PHASES，不得只改程式。

## 管理工具

```bash
./admin.sh validate      # 驗證世界資料 + 跑測試
```

（原 mud 的 `saves`／`delete-save` 等待 persistence 實作後補上。）

## Backlog

主清單在 [`docs/PHASES.md`](docs/PHASES.md)。近期已完成（2026-06）摘要：

| 項目 | 模組／驗收 |
|------|------------|
| Client 主介面現代化 | `client/tui_styles.py`、`client/ui_format.py` |
| 登入／版面修正 | 輸入框可見、art 高度、RichLog 不搶焦點 |
| 側欄修正 | `room_id` 刷新 map、優先 `@ui` JSON |
| 物品／NPC 英文後綴 | `shared/locale_content.py` → `look`／`scan`／`inventory` |
| Tab 自動補全 | `shared/completion.py`、`client/completion.py`、`@meta complete_*` |
| 快捷鍵列 | `#hotkey_bar`（Tab、F2–F6、`/reconnect`） |
| 輸出動畫前綴 | `client/output_prefix.py`（Braille spinner） |
| Client 重新連線 | `client/reconnect.py`、斷線退避、`/reconnect`、重送 auth |
| Server 程式碼熱重載 | `server/code_reload.py`、`server/dev_reload.py`、`./run.sh --dev` |
| Client spinner 執行中指示 | 僅執行中指令列動畫；完成後停止 |
| Client 狀態動畫指示 | 戰鬥／任務／低 HP／NETRUN 進行中時狀態列圖示旋轉 |
| 戰鬥 CD 秒數倒數 | `client/cd_display.py`、`combat_cd` 秒級 meta、hint／log 即時倒數 |
| NPC 離房結束戰鬥 | `npc_in_player_room`、`resolve_npc_departed`；敵人巡邏離開時結束 encounter |
| Tab 補全修正 | `MudPrompt` 攔截 Tab、`_apply_prompt_completion` 同步 fallback |
| 戰鬥節奏加速 | `combat_tick_loop` 每 3s；攻擊 CD 3s、NPC 反擊 6s |
| 效能優化 | 靜默 CD tick、精簡戰鬥 meta、client spinner 降頻 |
| 側欄 stack | `sidebar_stack` 同時顯示 PDA＋地圖；F2–F5 切換疊加 |
| 啟動狀態 | `StartupReport` 載入耗時；server 終端＋client hint |
| Client 輸入歷史 | ↑↓ 指令歷史、Esc 還原、`command_history.json` 持久化 |

### 待做（節錄）

維護規則見 [`docs/PHASES.md`](docs/PHASES.md#backlog-維護慣例)——**之後所有修正或變動都要更新 backlog**。

- Tab 補全多候選輪替
- Phase E.4 文件 GitHub 風格 + TOC
- NPC 任務驅動 AI、玩法數值深度平衡等（見 PHASES Backlog）

世界觀與區域擴充見 [`docs/WORLD.md`](docs/WORLD.md)。

## 注意事項

- 世界觀為致敬風格之原創內容，非官方 Cyberpunk／Blade Runner 劇情。
- 擴充功能前先看 `docs/PHASES.md` 與 `docs/IMPLEMENTATION.md`，避免與既有協定衝突。
- 新增可重複流程時，可封裝為 skill（`.grok/skills/` 或 `.claude/skills/`），格式可參考 [andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills)。