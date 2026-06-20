# 實作藍圖（Implementation）

> 本文件整理自原 **mud** 專案（commit 約 `34d5525`），供 **cyber_mud** 從零重建或改題材 fork 使用。  
> 不含可執行原始碼；細節以「模組職責 + 資料結構 + 協定 + 行為」描述。

## 目錄

- [設計原則](#設計原則)
- [技術棧](#技術棧)
- [模組總覽](#模組總覽)
- [通訊協定](#通訊協定)
- [指令系統](#指令系統)
- [實體與狀態](#實體與狀態)
- [世界與資料](#世界與資料)
- [世界觀文件](#世界觀文件)
- [伺服器流程](#伺服器流程)
- [Client TUI](#client-tui)
- [遊戲子系統](#遊戲子系統)
- [持久化](#持久化)
- [測試策略](#測試策略)
- [Fork 新 MUD 時改什麼](#fork-新-mud-時改什麼)

## 設計原則

1. **內建 Textual client 為唯一正式介面**；TCP 純文字協定僅供除錯。
2. **資料驅動**：房間、NPC、物品、技能、天氣等放 `data/`，程式只解讀與執行。
3. **指令一檔一案**：`commands/<verb>.py` 註冊至 `registry`。
4. **單連線指令序列化**：server 對每個 client `await handle_command` 後才讀下一行（client 可依此在指令後安全追發 refresh）。
5. **English 為預設語系**（`lang en`／`lang zh` 切換），文案放 `locale/en.yaml` + `locale/zh.yaml`，以 key 查表（`shared/i18n.py`）；慣例見 [`LOCALIZATION.md`](LOCALIZATION.md)。

## 技術棧

| 項目 | 選型 |
|------|------|
| 語言 | Python 3.13 |
| 環境 | pyenv + virtualenv（`setup.sh`） |
| Client UI | Textual + Rich |
| 世界資料 | YAML（房間、物品、NPC…） |
| 測試 | pytest（目標 150+ 測試） |
| 通訊 | asyncio TCP，`readline` 換行協定 |

## 模組總覽

```text
server/          Game、ClientSession、tick_loop、廣播
server/main.py   accept 連線、逐行讀取、優雅關閉
client/          MudClientApp（Textual）、連線、側邊欄、自動完成
shared/          protocol 常數、i18n、completion、ui_json
world/           World、Room、WorldState、clock、weather、tick
entities/        Player、NPC、Item 資料類別
commands/        所有玩家指令 + registry + helpers
combat/          Encounter 即時戰鬥狀態
persistence/     玩家存檔、world_state.json
data/            靜態世界定義
locale/          zh / en 字串表
tests/           單元與整合測試
```

## 通訊協定

定義於 `shared/protocol.py`。每行一則訊息，UTF-8 換行結尾。

### 前綴一覽

| 前綴 | 用途 | 消費端 |
|------|------|--------|
| （無前綴） | 一般遊戲文字 | Client 主 log |
| `@meta key=value` | 狀態同步（房間、HP、hint、側欄觸發等） | Client `_apply_meta` |
| `@panel ` | 側邊欄逐行內容 | Client `_write_panel_line` |
| `@ui ` | JSON 結構化 UI（panel/sections） | Client `_apply_ui_json` |
| MOTD / SYS / ERR 前綴 | 橫幅、系統、錯誤 | Client 著色輸出 |

### 側邊欄串流協定

面板指令（`pda`、`help`、`map`、`equipment`）使用 `ok_panel()`：

```text
@meta ui_panel=pda
@ui {"panel":"pda","title":"...","sections":[...]}   # 可選
@panel ═══ ...
@panel 內容行...
@meta ui_panel_end=1
```

Client 以 `_sidebar_pending_panel` / `_sidebar_stream_panel` 避免舊回應污染新面板。

### Client → Server 控制 meta

- `@meta rows=<終端列數>`：分頁器 `take_page` 用

### 輸出類型（CommandResult）

| 類型 | 函式 | 行為 |
|------|------|------|
| 一般 | `ok(lines)` | 多行文字進主 log |
| 文件 | `ok_document(lines)` | 長文分頁（`c`/`q` 續讀） |
| 面板 | `ok_panel(lines, panel=..., ui_json=...)` | 側邊欄 + 可選 JSON |

**注意**：`look` 應使用 `ok_document`，內容進主 log；不要用 `ok_panel`，否則玩家看不到房間描述。

## 指令系統

### 註冊與派發

```python
# commands/registry.py
register("look", handle)
dispatch(line, player, state, peers, all_players)
```

流程：

1. `expand_line()` 解析別名（`l`→`look`、`eq`→`equipment`）
2. 拆 `verb` + `args`
3. 組 `CommandContext(player, state, args, peers, all_players)`
4. handler 回傳 `CommandResult`
5. `server/game.py` 依 result 送輸出、`send_meta`、廣播、存檔

### player_meta

幾乎每個指令成功後附 `meta=player_meta(ctx)`，欄位含：

- `room`, `room_id`, `hp`, `gold`, `name`, `locale`, `auth`
- `hint`, `time`, `period`, `ram`, `humanity`, `reputation`
- `prompt_mud`, `prompt_netrun`
- `combat`, `combat_log`, `combat_cd`（戰鬥中）
- `comp_*`（自動完成用）
- `net_shell`, `net_prompt`（駭入模式）

### 已實作指令分類（原專案）

**移動／感知**：`look`, `go`, `map`, `scan`, `search`, `probe`  
**物品**：`take`, `drop`, `inventory`, `equip`, `unequip`, `use`, `give`, `appraise` + `all` 批次  
**戰鬥**：`attack`, `quickhack`, `defend`, `flee`  
**義體／模組**：`install`, `mod`, `learn`  
**社交**：`say`, `tell`, `talk`  
**系統**：`help`, `pda`/`status`, `equipment`, `time`, `save`, `quit`, `prompt`, `lang`, `alias`  
**駭入**：`net` shell（`net_shell` 子系統）  
**認證**：`login` / `register`（未命名玩家 gate）

### 別名

`commands/aliases.py`：`DEFAULT_ALIASES` + 玩家 `custom_aliases`。

## 實體與狀態

### Player（`entities/player.py`）

核心欄位：

| 類別 | 欄位 |
|------|------|
| 身份 | `name`, `named`, `locale`, `room_id` |
| 生存 | `hp`, `max_hp`, `gold` |
| CP2077 屬性 | `body`, `reflex`, `tech`, `cool`, `intelligence`, `humanity`, `reputation` |
| 駭客 | `ram`, `max_ram`, `skills[]`, `net_shell` |
| 背包／裝備 | `inventory[]`, `equipment{slot: item_id}` |
| 義體 | `implants[]`（或等價結構） |
| 戰鬥 | `in_combat`, `status_effects[]` |
| 自訂 | `prompt_mud`, `prompt_netrun`, `custom_aliases` |

### Item / NPC

- Item：`slot`, `takeable`, `weapon_damage`, `defense`, 價值、描述（多語 key）
- NPC：`hp`, `hostile`, `room_id`, 對話、掉落；tick 時可移動／閒置動作

### WorldState（`world/state.py`）

- 靜態：`world`（房間圖、物品表、NPC 表…）
- 動態：`room_items`（各房地面物品）、`clock`、`weather`、`combat_encounters`、NPC 執行期位置

## 世界與資料

### 目錄建議

```text
data/
  world.yaml      # 或 rooms.yaml + 索引
  items.yaml
  npcs.yaml
  skills.yaml
  implants.yaml
  weather.yaml
  time.yaml
```

### 房間

- `id`, `name`, `description`（locale key）
- `exits`: `{direction: room_id}`
- `district`, `tags`（安全等級、室內／室外）
- grid 座標（地圖用）

### 裝備槽

`shared/equipment.py` 定義 `EQUIP_SLOTS`（如 weapon、armor、head…）。`equip` 依 `item.slot` 穿戴。

### 世界觀文件

設定、區域、派系、敘事錨點與玩法對照見 **[WORLD.md](WORLD.md)**（Blade Runner + Cyberpunk 2077 致敬的「夜城」）。

## 伺服器流程

```text
main.py: readline loop
  → @meta rows → apply_client_meta
  → 其他 → game.handle_command
       → dispatch
       → send_output / send_meta
       → broadcast / notify
       → persist player + world_state（若 world_changed）

game.tick_loop (背景):
  → process_tick(state, sessions)
       → 時鐘前進、天氣、NPC 移動／閒置、戰鬥 tick
       → 對在線玩家 push meta / 訊息
```

**熱重載**（`./run.sh --dev`）：程式變更重啟 server；`world` / `locale` 可 reload 而不踢玩家。

## Client TUI

### 版面

- Header、狀態列（房間／HP／金錢／時間／RAM…）
- `hint_bar`（戰鬥 log、任務 hint）
- 主 `RichLog` + 可收合 `GameSidebar`
- Prompt 列（支援密碼遮罩、歷史、Tab 完成）

### 快捷鍵

| 鍵 | 面板 |
|----|------|
| F2 | PDA（vitals + 裝備 + 義體 + 技能） |
| F3 | Help |
| F4 | Map |
| F5 | Equipment |

### 側邊欄刷新

- 開面板：`_refresh_panel` → 送 `pda` / `equipment` 等
- **裝備變更後自動刷新**（原專案 `34d5525`）：若側欄開著 `pda` 或 `equipment`，在 `equip`/`unequip`/`drop`/`install`/`mod` 指令送出後自動 `_refresh_panel`

### 自動重連

斷線後指數退避重連；若曾登入則重送 auth line。

### 本機指令（`/` 開頭）

`/prompt`, `/theme`, `/reconnect`, `/quit` 等——不送 server。

## 遊戲子系統

### A. 時間與 Tick（Phase A）

- `world/clock.py`：`TimeConfig`、`day`、`period`（晨／午／夜…）
- `world/tick.py`：每 N 秒 `process_tick`
- `commands/time.py` 查詢世界時間
- `@meta time` / `period` 更新 client 狀態列

### B. 屬性（Phase A）

五維屬性影響戰鬥／檢定；`pda` 顯示。與 `hp`/`ram`/`humanity`/`reputation` 並列。

### C. 天氣（Phase B）

- `world/weather.py`：依 district 或全域；`look` / 狀態列可顯示
- 資料在 `data/weather.yaml`

### D. NPC 移動與閒置（Phase B）

- tick 內依 district、個性、時段決定巡邏／駐守
- 進出同房：廣播或 `look` 可見訊號
- 閒置動作（抽菸、吆喝）節流避免洗版

### E. 即時戰鬥（Phase C）

- `combat/encounter.py`：`Encounter` 含雙方 CD、回合佇列
- 玩家：`attack`, `defend`, `flee`, `quickhack`
- tick 推進 NPC 行動；`@meta combat=1`, `combat_log`, `combat_cd`
- 被動技能／義體可掛條件觸發（擴充點）

### F. 批量物品與 UI 拋光（Phase D）

- `commands/bulk_helpers.py`：`take/drop/equip/unequip all`（含 `全部`、`*`）
- `shared/ui_json.py`：結構化側欄
- `scan` + `search` 合併顯示邏輯
- `give`, `appraise` 估價

### G. Prompt 自訂

- Server `prompt` 指令 + client `/prompt` 本機覆寫
- Token：`%n` 名稱、`%r` 房間、`%h` hp…（可擴充）

### H. NETRUN 子 shell

- `player.net_shell` 切換 tema／提示符
- `commands/net_shell.py` 獨立 dispatch
- Client 阻擋一般 MUD 指令（除 `/reconnect` 等）

## 持久化

| 檔案 | 內容 |
|------|------|
| `saves/<name>.json` | 玩家進度 |
| `world_state.json` | 動態世界（地面物品、時鐘、天氣…） |

`admin.sh validate`：驗證 `data/` + 跑 pytest。

## 測試策略

| 區域 | 範例測試檔 |
|------|------------|
| 指令 | `test_look.py`, `test_equip.py`, `test_bulk.py` |
| 戰鬥 | `test_combat.py` |
| Tick／時間 | `test_tick.py`, `test_time.py` |
| Client 邏輯 | `test_client_sidebar.py`（純函式，不開 TUI） |
| 協定／meta | `test_hint.py`, `test_prompt.py` |

慣例：修改指令或世界邏輯 → 跑相關測試 → 全量 `pytest tests/`。

## Fork 新 MUD 時改什麼

| 優先 | 項目 | 說明 |
|------|------|------|
| 1 | `data/` | 新世界、新 NPC、新劇情——**主要工作量** |
| 2 | `locale/` | 世界觀文案、指令說明 |
| 3 | `client/theme` | 配色、橫幅 ASCII |
| 4 | `shared/` 常數 | 埠號、標題、裝備槽命名 |
| 5 | `commands/` | 只加「新玩法」指令；其餘複用架構 |
| 6 | `CLAUDE.md` / agent skills | 改專案名與世界觀描述 |

**不必重寫**：`server` 連線模型、`registry` 派發、`protocol`、`persistence` 骨架、Textual client 框架。

---

下一步：依 [BOOTSTRAP.md](BOOTSTRAP.md) 建 MVP，再照 [PHASES.md](PHASES.md) 逐階段補齊。