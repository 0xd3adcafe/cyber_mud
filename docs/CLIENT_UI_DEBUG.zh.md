# Client UI 除錯案例與慣例

> **English:** [CLIENT_UI_DEBUG.md](CLIENT_UI_DEBUG.md)

本檔記錄 **2026-06** Textual client 版面／側欄一連串「反覆修卻修不好」的根因與最終解法，供日後改 `client/` 時對照。

## 目錄

- [症狀摘要](#症狀摘要)
- [根因 1：Textual `region` vs `size`](#根因-1textual-vs)
- [根因 2：Dock 堆疊](#根因-2dock-堆疊)
- [根因 3：側欄狀態機（雙路徑）](#根因-3側欄狀態機雙路徑)
- [根因 4：非同步阻塞](#根因-4非同步阻塞)
- [交付前 Checklist（Client UI 變更必做）](#交付前-checklistclient-ui-變更必做)
- [測試慣例（避免假陽性）](#測試慣例避免假陽性)
- [反模式（日後避免）](#反模式日後避免)
- [相關測試](#相關測試)
- [變更歷史（摘要）](#變更歷史摘要)
- [Client 主 log 可讀性（已交付 — CL.1–CL.8）](#client-主-log-可讀性已交付-cl1cl8)

## 症狀摘要

| 現象 | 使用者觀察 | 實際根因 |
|------|------------|----------|
| 連線列／快捷鍵列／遊戲狀態列消失 | 頂底 `Static` 在終端空白 | 未設 `min-height:1` → `region.height≥1` 但 `size.height=0`，真實終端不繪製 |
| 輸入 `map`／`pda` 不開側欄 | F2–F5 可開（修復前後行為不一致） | Prompt 路徑未設 `sidebar_open`；`ui_panel_end` 需 `sidebar_open` 才入 stack |
| Stack 後狂按 F 鍵卡死 | UI 像當掉數十秒 | `action_*` 內 `await _fetch_panel()`（最多 15s）阻塞主迴圈 |
| F6 後側欄又彈回（舊問題） | 關閉後晚到 meta 重開 | `ui_panel_end` 無條件 append（已用 `sidebar_open` 閘門修復） |
| 誤以為存檔壞掉 | 換角色仍一樣 | 側欄狀態在記憶體；版面不讀 `data/saves/` |

**不是** model 問題、**多半不是**玩家存檔問題。

## 根因 1：Textual `region` vs `size`

Headless `run_test` 常見：

```text
#info_bar:   region.height=1  size.height=0  → 測試以為有高度，終端卻空白
#chrome_bar: region.height=1  size.height=0  → 同上
```

**錯誤修法**：只調 `dock`、搬家、改 `region` 斷言。  
**有效修法**：`#info_bar`／`#chrome_bar`／`#hotkey_bar` 使用 `height: auto; min-height: 1`；`#info_bar` 勿設 `max-height: 1`（見 `client/tui_styles.py`）。

Probe 範例（改動 client 後建議跑）：

```bash
.venv/bin/python -c "
import asyncio
from client.meta_handlers import apply_meta
from client.app import CyberMudApp

async def main():
    app = CyberMudApp('127.0.0.1', 4000)
    async with app.run_test(size=(120, 30)) as pilot:
        apply_meta(app.view, 'auth', '1')
        app._set_auth_ui(True)
        await pilot.pause()
        for wid in ('#info_bar', '#chrome_bar', '#hotkey_bar'):
            w = app.query_one(wid)
            print(wid, 'region', w.region.height, 'size', w.size.height)

asyncio.run(main())
"
```

驗收：`size.height >= 1` 且真實終端肉眼可見。

## 根因 2：Dock 堆疊

多個子 widget 同設 `dock: top`／`dock: bottom` 會**重疊**（例如 `info_bar` 與 `chrome_bar` 同 y）。

**有效結構**（`client/app.py` compose）：

```text
#top_dock (dock:top, vertical) → info_bar + chrome_bar
#main_row (1fr)
#bottom_dock (dock:bottom, vertical) → prompt_dock + hotkey_bar
```

單一 dock 容器 + 內部 vertical flow，不要用多個同向 dock 硬堆。

## 根因 3：側欄狀態機（雙路徑）

```text
F2–F5  → _send_panel_command → toggle_sidebar_panel → sidebar_open=True
      → pending_panel → _schedule_panel_fetch（背景）
      → server ui_panel / ui_panel_end → stack → _render_sidebar

輸入 map → on_game_input → resolve_panel_command
      → prepare_sidebar_for_panel + pending_panel（與 F 鍵對齊）
      → send_line → 同上 meta 串流
```

顯示條件：`sidebar_should_show()` = `sidebar_open` 且（`sidebar_stack` 或 `pending_panel`）。

| Meta／行為 | 說明 |
|------------|------|
| `ui_panel_end` 入 stack | 僅當 `sidebar_open`（F6 後為 False → 晚到回應不重開） |
| 載入中再按同 F 鍵 | 取消 fetch（`_cancel_panel_fetch`），勿再排隊 |
| F6 | 清空 stack、`sidebar_open=False`、bump `_panel_fetch_generation` |

相關模組：`client/meta_handlers.py`（`resolve_panel_command`、`prepare_sidebar_for_panel`、`sidebar_should_show`）、`client/app.py`（`_send_panel_command`、`_schedule_panel_fetch`）。

## 根因 4：非同步阻塞

**禁止**在 `action_panel_*` 內 `await _fetch_panel()`。  
Panel 請求應 `asyncio.create_task` + lock 序列化 + 可取消（generation）。

狂按 F 鍵時，舊行為會排 6×15s；新行為應在 <1s 內返回（見 `tests/test_client_app.py::test_panel_fetch_actions_do_not_block`）。

## 交付前 Checklist（Client UI 變更必做）

在 **Windows Terminal／常用終端** 與 `pytest` 雙邊驗證：

1. [ ] 登入後：`info_bar`、**連線列**（chrome）、**快捷鍵列**（hotkey）皆可見（24 行高亦可）
2. [ ] 輸入 `map`、`pda`、`h`（help）→ 側欄自動開啟
3. [ ] F2 + F4 stack → F6 全關；晚到 `ui_panel_end` 不重開
4. [ ] 連按 F2/F3/F4 → prompt 仍可輸入，不明顯凍結
5. [ ] `pytest tests/test_client_app.py tests/test_client_meta.py` 通過
6. [ ] 更新 [`docs/PHASES.md`](PHASES.md) Backlog／已完成

## 測試慣例（避免假陽性）

| 不要只測 | 應加測 |
|----------|--------|
| `widget.region.height == 1` | `widget.size.height >= 1` |
| 只設 `sidebar_open=True` 再餵 meta | 走 `prepare_sidebar_for_panel` 或 `_send_panel_command` 全路徑 |
| 單次 F2 | 連按、`test_f6_closes_sidebar_*`、typed map 測試 |

## 反模式（日後避免）

1. **症狀驅動**：只看到列消失就改顏色／搬家，未量 `size.height`
2. **單點修 F6**：`ui_panel_end` 加閘門卻未補 prompt 路徑的 `sidebar_open`
3. **過度 dock**：多個 `dock: top` 以為會自動堆疊
4. **action 長 await**：把網路／15s 等待放在按鍵 handler
5. **只信 headless**：未在真實終端確認

## 相關測試

- `tests/test_client_app.py`：`test_chrome_bar_*`、`test_hotkey_bar_*`、`test_typed_map_command_opens_sidebar`、`test_panel_fetch_actions_do_not_block`、`test_f6_closes_sidebar_*`
- `tests/test_client_meta.py`：`test_resolve_panel_command_aliases`、`test_sidebar_should_show_with_pending_panel`

## 變更歷史（摘要）

| 項目 | 模組 |
|------|------|
| dock 單一 top/bottom 容器 | `client/app.py`、`client/tui_styles.py` |
| chrome/hotkey `min-height:1` | `client/tui_styles.py` |
| prompt panel 自動開側欄 | `client/meta_handlers.py`、`client/app.py` |
| 非阻塞 fetch + 取消 | `client/app.py` |

完整 backlog 條目見 [`PHASES.md`](PHASES.md)「快捷鍵列可見性」。

## Client 主 log 可讀性（已交付 — CL.1–CL.8）

**問題：** 多數伺服器行共用暗淡 `›` 前綴（`client/output_prefix.py` 的 `text`）。僅 MOTD／SYS／ERR／echo 有差異；`env_format.py` 只為 look／scan 實體列上色，戰鬥、委託、社交、成長訊息仍難區分。

**改 log 樣式前：**

1. 先讀 PHASES **Client log UX** — 先實作 CL.1 分類器再調色盤。
2. 新增 `tests/test_log_classifier.py`（前綴 → kind）；擴充 `test_output_prefix`／`test_env_format`。
3. 主題切換須透過 `AnimatedLogBuffer`＋`LogPalette` 重繪 log（比照 `client/themes.py` 的 `EnvPalette`）。
4. 不可破壞 CD 倒數（`cd_display.py`）或進行中指令的 echo 旋轉前綴。

**關鍵檔案：** `client/animated_log.py`、`client/output_prefix.py`、`client/env_format.py`、`client/app.py`（`_append_log`、`_read_loop`）。
