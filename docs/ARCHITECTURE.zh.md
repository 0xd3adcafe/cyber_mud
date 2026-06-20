# 架構說明

> **English:** [ARCHITECTURE.md](ARCHITECTURE.md)

> cyber_mud 文件 fork。描述原 mud 專案之系統架構（已實作 + 規劃）。

## 目錄

- [世界觀](#世界觀)
- [總覽](#總覽)
- [執行時架構](#執行時架構)
- [資料流](#資料流)
- [模組依賴](#模組依賴)
- [已實作功能](#已實作功能)
- [規劃中](#規劃中)

## 世界觀

原 **mud** 設定為賽博龐克**夜城**：企業、幫派、義體與黑市並存；玩家經**神經連結**進入，並可在 **NETRUN** 駭入層與實體街頭間切換。完整設定見 **[WORLD.md](WORLD.md)**。

## 總覽

```text
                    ┌─────────────┐
                    │ Textual TUI │  client/（正式介面）
                    └──────┬──────┘
                           │ TCP 換行文字
                    ┌──────▼──────┐
                    │ server/     │  asyncio、Session、Game
                    │  game.py    │
                    └──────┬──────┘
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
    ┌────────────┐  ┌────────────┐  ┌────────────┐
    │ commands/  │  │ world/     │  │ combat/    │
    │ registry   │  │ tick/clock │  │ encounter  │
    └─────┬──────┘  └─────┬──────┘  └────────────┘
          │               │
          ▼               ▼
    ┌────────────┐  ┌────────────┐
    │ entities/  │  │ data/      │
    │ Player…    │  │ YAML 世界  │
    └────────────┘  └────────────┘
          │
          ▼
    ┌────────────┐
    │persistence/│  saves/、world_state.json
    └────────────┘
```

## 執行時架構

### 連線模型

- 一玩家一 `ClientSession`（含 `StreamWriter`、`Player`、分頁狀態）
- `server/main.py`：`readline` → `handle_command`（**阻塞至處理完**）
- 背景 `tick_loop`：週期性 `process_tick`，與指令處理共用 `WorldState`（需注意並發／鎖或單執行緒 asyncio）

### Game 職責

- 維護 `sessions` 列表
- `dispatch` 玩家指令
- `broadcast_localized` 同房／全服訊息
- `tick_loop` 驅動世界
- `reload_world`（dev 模式）
- 優雅關閉：存檔、通知離線

## 資料流

### 指令下行（Client → Server）

```text
玩家輸入 "equip blade"
  → client 送 "equip blade\n"
  → server dispatch
  → 修改 Player.equipment
  → 回傳文字行 + @meta 多行
  → （若側欄開著）client 再送 "equipment" 刷新
```

### Meta 下行（狀態同步）

```text
@meta hp=80/100
@meta hint=▸ 任務提示…
@meta combat=1
```

Client 更新狀態列、hint_bar、prompt token 來源。

### 面板下行

```text
@meta ui_panel=pda
@panel …
@meta ui_panel_end=1
```

## 模組依賴

| 模組 | 依賴 | 不可依賴 |
|------|------|----------|
| `shared/` | 標準庫 | server、client |
| `entities/` | shared | commands、server |
| `world/` | entities、data 載入 | client |
| `commands/` | world、entities、combat | client |
| `server/` | commands、world、persistence | client |
| `client/` | shared | server、commands |
| `combat/` | entities、world | client |

## 已實作功能

### 核心

- [x] 多人 TCP 伺服器
- [x] 指令註冊制與別名
- [x] 世界 YAML 載入與驗證
- [x] 玩家存檔與 world_state
- [x] Textual client（log、狀態、側欄、Tab 補全、快捷鍵列、即時旋轉 spinner、主題）
- [x] i18n（zh/en）
- [x] 分頁長文（look、help 等）

### 遊戲系統

- [x] 物品 take/drop/equip/unequip（含 all）
- [x] 裝備槽與武器模組
- [x] 義體 install、技能 learn
- [x] 世界時鐘與 tick
- [x] CP2077 風格屬性欄位
- [x] 天氣（區域）
- [x] NPC tick 移動／閒置
- [x] 即時戰鬥 encounter（`combat_cd` 秒級 meta、client 即時倒數）
- [x] NETRUN 子 shell（server `net` + client `net_shell` meta）
- [x] PDA／地圖／說明／裝備側欄
- [x] 生活指令 — `sit`／`stand`／`lie`／`rest`／`sleep`／`wake`；姿態與疲勞（`world/life.py`、`data/life.yaml`）
- [x] Prompt 自訂（server + client 覆寫）
- [x] 開發熱重載（`data/*.yaml` + 程式碼 `reload_application_code`）、client 自動重連與 `/reconnect`
- [x] 側欄裝備自動刷新

### 工具

- [x] `admin.sh validate` / `saves` / `delete-save` / `quests`
- [x] `tools/generate_world.py` — 單區域房間格點 YAML
- [x] `tools/merge_world_grid.py` — 八區格點併入 `data/world.yaml`
- [x] `tools/expand_world_population.py` — 程序 NPC／物品覆蓋層
- [x] `tools/quest_author.py` — 任務驗證／腳手架（`./admin.sh quests`）
- [x] pytest

完整用法：**[WORLD_TOOLS.zh.md](WORLD_TOOLS.zh.md)**（[English](WORLD_TOOLS.md)）。

## 規劃中

變更紀錄與待辦以 [PHASES.md — Backlog](PHASES.md#backlog) 為準；**每次交付前須更新**（見 [Backlog 維護慣例](PHASES.md#backlog-維護慣例)）。

節錄：

- 天氣／時段對玩法數值修正
- 完整被動技能與義體觸發
- NPC 任務驅動 AI
- NPC 任務驅動追擊與 flee 進階行為
- 店鋪作息、任務編排工具

---

細部實作步驟見 [IMPLEMENTATION.md](IMPLEMENTATION.md)；新專案啟動見 [BOOTSTRAP.md](BOOTSTRAP.md)。