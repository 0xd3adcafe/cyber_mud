# CLAUDE.md

> **English:** [CLAUDE.md](CLAUDE.md)

本檔為 Claude Code、Cursor 與 Grok 在本 repo 協作時的行為指引。  
**行為準則**參考 [Andrej Karpathy Skills](https://github.com/multica-ai/andrej-karpathy-skills/blob/main/CLAUDE.md)（上層目錄 `andrej-karpathy-skills.md` 為連結）；以下合併 **cyber_mud** 專案專屬說明。

**取捨：** 準則偏向謹慎而非速度；瑣碎任務可自行判斷。

## 專案規則（強制）

**以下規則對 Agent 與協作者為硬性要求，不得忽略。**

### 英文為預設語系

| 範圍 | 規則 |
|------|------|
| **遊戲內** | 新玩家、存檔無 `locale`、client 登入、所有 `or "en"` 後備皆為 **`locale=en`**。中文需主動 `lang zh`。 |
| **文案** | `data/locale/en.yaml` 為權威來源；**同時**維護 `zh.yaml`。世界 YAML 維護 `*_en`／`*_zh`；`player.locale == "en"` 時顯示英文。 |
| **伺服器日誌** | `CYBER_MUD_SERVER_LOCALE` 預設 `en`；使用 `server.*` locale key，邏輯層不硬編碼中英文。 |
| **Client UI** | `client.*` key；`lang zh` meta 前，chrome／placeholder 預設英文。 |
| **文件** | 英文 `*.md` 為 GitHub 預設；`*.zh.md` 對照維護。 |
| **Commit** | 主述必須英文：`<type>: EN summary` — 可選 ` / 中文`。 |
| **測試** | 新測試用 `Player()` 或 `make_player(locale="en")`，除非明確測 `zh`。 |

**禁止：** 將專案預設改為 `zh`、無 locale key 僅寫中文使用者文案、遊戲文案變更卻只改 `zh.yaml` 而不改 `en.yaml`。

完整政策：[`docs/LOCALIZATION.zh.md`](docs/LOCALIZATION.zh.md)。

## 目錄

- [專案規則（強制）](#專案規則強制)
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

**核心原則**

1. **英文為預設語系** — 見 [專案規則（強制）](#專案規則強制)；`lang zh` 為選用。
2. **內建 client** — 不依賴外部 MUD 客戶端。

- 主要玩家介面是本 repo 的 `client/`（Textual TUI）。
- 不使用 MUDlet、TinTin++、`nc` 等作為正式遊玩方式。
- 伺服器保留 TCP 換行文字協定供除錯；產品體驗以內建 client 為準。

**目前已具備：** 登入存檔、物品、戰鬥、NETRUN、tick、側欄（PDA／地圖／裝備）、Tab 補全、自動重連、`--dev` 熱重載等——完整清單見 [`docs/PHASES.md`](docs/PHASES.md)「已完成」。  
**待擴充：** 見 [`docs/PHASES.zh.md`](docs/PHASES.zh.md#backlog)。

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

**文件政策：** 專案文件分為英文 `*.md`（GitHub 預設）與中文 `*.zh.md` 對照。更新文件時請同步維護兩語版本。

完整文件索引（中文本檔；英文見同名無 `.zh` 路徑）：

| 文件 | 用途 |
|------|------|
| [`docs/WORLD.zh.md`](docs/WORLD.zh.md) | 世界觀、區域、派系 |
| [`docs/IMPLEMENTATION.zh.md`](docs/IMPLEMENTATION.zh.md) | 實作藍圖 |
| [`docs/ARCHITECTURE.zh.md`](docs/ARCHITECTURE.zh.md) | 系統架構 |
| [`docs/BOOTSTRAP.zh.md`](docs/BOOTSTRAP.zh.md) | MVP 啟動步驟 |
| [`docs/PHASES.zh.md`](docs/PHASES.zh.md) | 分階段實作清單 |
| [`docs/CLIENT_UI_DEBUG.zh.md`](docs/CLIENT_UI_DEBUG.zh.md) | Client 版面／側欄除錯案例與交付 checklist |
| [`docs/LOCALIZATION.zh.md`](docs/LOCALIZATION.zh.md) | 雙語政策 |
| [`docs/WORLD_TOOLS.zh.md`](docs/WORLD_TOOLS.zh.md) | 世界格點／人口／任務編寫 CLI |

## 開發慣例

- 語言：Python 3.13（virtualenv `cyber-mud-3.13.12` 或 `.venv`）
- UI：Textual + Rich（`client/`）
- 通訊：TCP 換行文字協定（`shared/protocol.py`）
- 世界資料與程式碼分離；新增房間優先改 `data/`，不硬編在程式裡
- 指令處理採註冊制；每個指令一個模組，放在 `commands/`
- **英文預設語系（強制）**：見 [專案規則](#專案規則強制)；`en.yaml` 與 `zh.yaml` 同步（[`docs/LOCALIZATION.zh.md`](docs/LOCALIZATION.zh.md)）
- **文件**：英文 `*.md` + 中文 `*.zh.md` 對照；變更時同步更新
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

Commit message 格式：**英文主述** `<type>: <EN summary>`，可選繁中後綴 ` / <中文簡述>`（如 `feat: add item system / 新增物品系統`）。

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
| 快捷鍵列 | `#hotkey_bar`（Tab、F2–F6、`/reconnect`）；chrome／hotkey `min-height:1`；輸入 panel 指令自動開側欄；F 鍵非阻塞 fetch |
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
| Client 記憶帳密／PIN | `client/credentials.py` 加密儲存、PIN 快速登入、F7 清除記憶 |
| look 目標察看 | `look <目標>` 察看物品／NPC／裝備狀態與數值 |
| NPC 屍體與搜刮 | `world/corpses.py` 擊倒留屍、loot、腐化掉落 |
| 屍體英文後綴 | `corpse_label` 顯示 `(English)`／`(corpse)` 方便指令 |
| 新手區擴充 | 訓練場 9 房、10 NPC、4 互動點；簡報室／餐廳／障礙道／模擬診所；`tests/test_tutorial_zone.py` |
| 商店與交易 | `shop`／`buy`／`sell`；`data/shops.yaml`；註冊送起始金錢 |
| 環境輸出著色 | `client/env_format.py` look／scan 分色顯示 |
| 環境色隨主題 | `client/themes.py` `EnvPalette`；`/theme` 切換同步環境色 |
| 消耗品系統 | `use`／`eat`／`drink`；食物／飲料／藥品；`world/consumables.py` |
| NETRUN 指令放行 | client 不再攔截 `hack`／`probe`／`status` |
| NPC 穿戴裝備 | `entities/npc.py` `equipment`；`look` 顯示；擊倒掉落 |
| 自然回血 | `world/vitals.py` 依 body／cool／時段 tick 回復 |
| NPC 重生 | `world/npc_respawn.py` 擊倒排程；`respawn_minutes`／`tier: boss` |
| 指令重複 | `10 punch`／`punch.10` 多次執行 |
| Server heartbeat | `server/heartbeat.py` 終端定期刷新運行狀態；dev 重載 log |
| CP2077 裝備槽與武器種類 | `shared/equipment.py` 七槽；CP2077 遠程武器種類＋power／tech／smart／melee；`armor` 存檔遷移 |
| NETRUN 英文後綴 | `net_node_label_with_id`；NETRUN 節點／地上物品 `(English)`；`hack` Tab 補全 |
| NETRUN 環境／NPC 互動 | NETRUN 中 `look`／`scan`／`talk`／`say` 放行；環境顯示可駭入節點 |
| 武器持握模式 | `weapon_primary`／`weapon_secondary`；`weapon_mode` 主要／次要／雙手／雙持 |
| 等級／技能／天賦 | `world/progression.py`；`stats`／`talents`／`improve`；`data/talents.yaml`；擊倒／駭入 XP |
| 街頭聲望與委託 | `street_cred`；`gigs`；`world/quests.py`；`broker_rumor` 交件獎勵 |
| CP2077 快速破解 | `data/quickhacks.yaml`；過熱／短路／光學重啟／突觸燒毀；戰鬥狀態效果 |
| 義體幻痛 | `world/cyberpsychosis.py` 低人性傷害懲罰 |
| CP2077 義體槽位 | 九槽 cyberware／install／uninstall；`data/implants.yaml` |
| 住宅與儲物 | `rent`／`home`／`stash`；`watson_flat` |
| 交通與載具 | `transit`；`vehicles buy`／`drive` |

### 待做

| 區域 | 項目 |
|------|------|
| 環境 | pyenv 原生編譯 Python |
| **世界擴充（WORLD.md）** | W.1–W.14 已交付（263 房／121 NPC／45 物品）；見 PHASES **世界擴充** |
| **內容深度** | D.1–D.10 已交付（聚光 NPC、區域委託、格點敘事）；見 PHASES **內容深度** |

維護規則見 [`docs/PHASES.md`](docs/PHASES.md#backlog-維護慣例)——**之後所有修正或變動都要更新 backlog**。



### 近期完成（2026-06 backlog 批次）

| 項目 | 模組／驗收 |
|------|------------|
| Tab 多候選輪替 | `complete_input_cycle`、`client/app.py` |
| 環境互動 | `interact`、`data/interactables.yaml`、`look`／`scan` |
| 上下移動 | `go up/down`、`u`/`d`、屋頂／地下區 |
| Prompt token | `%l` `%c` `%v` `%x`、`prompt template ncpd` |
| 多階段委託 | `dock_watch`、`world/quests.py` stages |
| 時段平衡 | `world/modifiers.py` period 修正 |
| 義體連鎖 | `passive_chains.yaml`、`combat/passives.py` |
| NCPD 通緝 | `world/wanted.py`、tick 衰減 |
| 載具車庫 | `vehicles buy/select`、`vehicles[]` |
| 製作拆解腦舞 | `craft`／`disassemble`／`braindance`、`tests/test_backlog_features.py` |
| NPC 派系動機 AI | `world/npc_ai.py`、`corp_scout`／`thug` 派系衝突、`tests/test_npc_ai.py` |
| 登入 banner MOTD 動態展示 | `client/login_motd.py`、`motd.tips` 輪播、`tests/test_login_motd.py` |
| Prompt 完整版（client 即時預覽） | `client/prompt_preview.py`、`#prompt_preview`、`tests/test_prompt_preview.py` |
| NPC 任務編排工具 | `world/quest_author.py`、`./admin.sh quests`、`tests/test_quest_author.py` |
| 完整任務系統 | `gigs accept`／`journal`、`defeat_npc`／`have_item`、`alley_clearance`、`tests/test_quest_system.py` |
| Help log 區 dropdown | `client/help_overlay.py`、`#help_dropdown` 覆蓋 log、`tests/test_help_overlay.py` |
| 新手區二次擴充 | 4 新房、6 教學 NPC、`patrol_dummy`、4 互動點、補給站新商品；`tests/test_tutorial_zone.py` |
| Gigs 側邊欄追蹤 | `gigs`／`journal` 側欄面板、F7 快捷鍵、任務進度自動刷新；`tests/test_gigs.py` |
| Help 指令分類 | `HELP_CATEGORIES` 15 類；F3 overlay 分類標題；`tests/test_help_cmd.py` |
| Focus 追蹤區塊 | prompt 上方 Grok 風漸層區塊；委託／戰鬥／指令執行；主題色＋圖示；`tests/test_focus_block.py` |
| Client clear 清除 log | `/clear` 本機指令；`AnimatedLogBuffer.clear()`；Tab 補全；`tests/test_client_app.py` |
| 中英文文件分離 | 英文 `*.md` GitHub 預設；中文 `*.zh.md` 對照；README ASCII banner |
| 英文預設語系寫入專案規則 | `CLAUDE.zh.md` § 專案規則（強制）；`LOCALIZATION.zh.md`；README 核心原則 #1 |
| 專案授權 | `LICENSE` Apache 2.0；`LICENSE-CONTENT.md` CC BY 4.0；`CONTRIBUTING.md` |
| 玩家指南（GitHub） | `docs/player/` — 上手、訓練場、指令、client（ASCII 風格） |
| 成人／NSFW 內容 M.0–M.7 | `world/mature.py`、`combat/gore.py`、`settings mature`、`flirt`、mature locale／YAML、client 18+ 登入 |
| Kabuki 與區域擴充 | `kabuki_vip`、`kabuki_bazaar`、小中國街、企業區樞紐；`velvet_job`；`tests/test_world_districts.py` |
| 世界擴充 W.8–W.10 | `data/schedule.yaml`；`docks_gray`／`gray_market`；企業／街頭 `appraise`；`give` 給 NPC；`go` 存在感廣播；`tests/test_black_market.py`、`tests/test_multiplayer.py` |
| 世界擴充 W.12–W.13 | `poison`／`antidote`；玩家 `overheat`；`world/reactions.py` 聲望＋環境 tick；`tests/test_status_effects.py`、`tests/test_world_reactions.py` |
| 世界擴充 W.14 | `tools/expand_world_population.py`；`world_population.yaml`；109 NPC／45 物品；`tests/test_world_scale.py` |
| 內容深度 D.1–D.6 | 原型 `talk.*`；任務 WARN＋`hub_briefing`；樞紐 NPC；格點 craft／商店；8 net 節點＋互動物；`tests/test_content_depth.py` |
| 內容深度 D.7–D.10 | 8 區域焦點 NPC；`district.grid.*` look 風味；4 區域任務；`world.ambient.*` 全區；`tests/test_content_depth.py` |
| Client 版面測試 helper | `tests/client_ui_helpers.py`；側欄／help overlay 穩定斷言 |
| 生活指令 L.1–L.8 | `sit`／`stand`／`lie`／`rest`／`sleep`／`wake`；`world/life.py`、`data/life.yaml`；互動錨點；vitals／RAM 回復；PDA＋`%posture`；`tests/test_life_commands.py` |

世界觀與區域擴充見 [`docs/WORLD.zh.md`](docs/WORLD.zh.md)。

## 注意事項

- 世界觀為致敬風格之原創內容，非官方 Cyberpunk／Blade Runner 劇情。
- 擴充功能前先看 `docs/PHASES.zh.md` 與 `docs/IMPLEMENTATION.zh.md`，避免與既有協定衝突。
- 改 `client/` 版面或側欄前先看 [`docs/CLIENT_UI_DEBUG.zh.md`](docs/CLIENT_UI_DEBUG.zh.md)；可搭配專案 skill `.grok/skills/cyber-mud-client-ui/`。
- 新增可重複流程時，可封裝為 skill（`.grok/skills/` 或 `.claude/skills/`），格式可參考 [andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills)。