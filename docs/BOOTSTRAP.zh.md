# 新專案啟動（Bootstrap）

> **English:** [BOOTSTRAP.md](BOOTSTRAP.md)

## 目錄

- [環境](#環境)
- [建議目錄骨架](#建議目錄骨架)
- [最小可玩版本（MVP）](#最小可玩版本mvp)
- [驗證清單](#驗證清單)

## 環境

- Python **3.13**（建議 pyenv virtualenv，例如 `cyber-mud-3.13.12`）
- 主要依賴：`textual`、`rich`、`pyyaml`、`pytest`
- 啟動腳本：`setup.sh`、`run.sh`、`admin.sh`（可從原專案慣例複製結構）

```bash
# 首次
./setup.sh

# 開發（熱重載）
./run.sh --dev

# 內建 TUI client
./run.sh --client
```

## 建議目錄骨架

```text
cyber_mud/
├── client/           # Textual TUI（主要玩家介面）
├── server/           # TCP 連線、遊戲迴圈、session
├── shared/           # 協定常數、i18n、protocol
├── world/            # 地圖、房間、時鐘、天氣、tick
├── entities/         # Player、NPC、Item
├── commands/         # 指令處理（一指令一檔）
├── combat/           # 即時戰鬥 encounter
├── persistence/      # 存檔、world_state
├── data/             # YAML/JSON 世界定義
├── locale/           # 繁中／英文案
├── tests/
├── docs/
├── setup.sh
├── run.sh
└── admin.sh
```

## 最小可玩版本（MVP）

依序實作，每步都有可驗證結果：

### 1. 協定與連線

- `shared/protocol.py`：換行文字協定、`@meta`、`@panel`、`@ui`、`MOTD_PREFIX` 等
- `server/main.py`：accept → `readline` → `handle_command`（**每連線依序處理**）
- `client/`：連線、讀取迴圈、主 log 輸出

**驗證**：client 連上後看到 MOTD，輸入 `look` 有房間描述。

### 2. 世界載入

- `data/world.yaml`（或拆分多檔）：rooms、exits、items、npcs
- `world/state.py`：`WorldState` 載入與 `room_items` 等執行期狀態
- `commands/look.py`、`commands/go.py`

**驗證**：`go north` 換房，`look` 內容正確。

### 3. 玩家與登入

- `entities/player.py`：`hp`、`gold`、`inventory`、`equipment`、`named`
- `commands/login` / `register`（或合併 auth 流程）
- `persistence/save.py`：登出／定期存檔

**驗證**：註冊後重連，位置與背包保留。

### 4. 指令註冊

- `commands/registry.py`：`register()`、`dispatch()`、`ok()` / `ok_panel()` / `ok_document()`
- `commands/aliases.py`：`expand_line()`（`l`→`look`、`eq`→`equipment` 等）

**驗證**：`pytest tests/test_registry.py`（或同等測試）通過。

### 5. 內建 Client 基礎 UI

- 狀態列：`room`、`hp`、`gold`（來自 `@meta`）
- 輸入框、Tab 自動完成（`shared/completion.py`）；輸入歷史（上下鍵）待補
- F2–F5 側邊欄骨架（可先只做 PDA）

**驗證**：`./run.sh --client` 可遊玩 MVP，不需 `nc`。

## 驗證清單

| 項目 | 指令／操作 |
|------|------------|
| 伺服器啟動 | `./run.sh` |
| Client 連線 | `./run.sh --client` |
| 世界資料合法 | `./admin.sh validate` |
| 測試 | `pytest tests/` |
| 熱重載 | `./run.sh --dev` 改 `data/` 或 `commands/` 後仍正常 |

完成 MVP 後，依 [PHASES.md](PHASES.md) 擴充 Phase A–D 功能。世界設定與區域文案見 [WORLD.md](WORLD.md)。