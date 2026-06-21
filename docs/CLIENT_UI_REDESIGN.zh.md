# Client UI 重設計（Grok 風格 + NETRUN Terminal HUD）

> **English（canonical）：** [CLIENT_UI_REDESIGN.md](CLIENT_UI_REDESIGN.md)

**狀態：** 規格已定稿；實作 **CU.1–CU.5**，**CU.0** 獨立 commit。

**範圍：** 僅遊戲內 Textual UI。登入版面不變，除 **CU.0**（ASCII 場景輪巡）。

**參考：** [`CLIENT_UI_DEBUG.zh.md`](CLIENT_UI_DEBUG.zh.md)、[`PHASES.zh.md`](PHASES.zh.md) § Client UI modernization（CU）。

---

## 目標

1. **Grok 式精簡 chrome** — 單一 status strip，主 log + prompt 為焦點。
2. **Dropdown 雙模式（方案 B）** — 瀏覽器分頁列，覆蓋 log **上半 50%**。
3. **NETRUN terminal HUD** — trace 條、連線狀態、英文指令速查；`net` 後預設展開。
4. **側欄角色不變** — PDA、map、equipment、gigs、**mesh**；NETRUN 自動開 **mesh**。
5. **文案跟隨 locale；指令名固定英文**。

---

## 版面（遊戲內）

```text
┌─ #status_strip（CU.1：合併 info + link）──────────────────┐
├─ #scrollback_wrap ─────────────────────────────────────────┤
│  ┌─ #overlay_panel（約 50% 高，layer: dropdown）──────────┐ │
│  │ [⎈ NET]  [? Help]     trace ████░░ 67%    [−]  Esc     │ │
│  ├────────────────────────────────────────────────────────┤ │
│  │ 作用中分頁內容（NETRUN HUD 或 Help 分類）                │ │
│  └────────────────────────────────────────────────────────┘ │
│  #log（下半 50%，可捲動）                                     │
├────────────────────────────┬───────────────────────────────┤
│                            │ #sidebar_wrap（F11 開關）      │
│                            │ NETRUN 預設：mesh 面板         │
├─ #focus_block（1–2 行）────┴───────────────────────────────┤
│ #prompt_dock                                                │
│ #hotkey_bar（情境式；dim 時顯示 F1–F12 對照）                 │
└─────────────────────────────────────────────────────────────┘
```

---

## Overlay 分頁（CU.2–CU.3）

### 分頁列（瀏覽器風格）

| 分頁 | 標籤 | 顯示條件 |
|------|------|----------|
| `netrun` | `⎈ NET` | `net_shell=1` |
| `help` | `? Help` | 恆可選 |

- **作用中：** accent 底線 + 粗體；點擊 `#overlay_tab_*` 切換。
- **不用 Tab 鍵** — Tab 僅指令補全。

### 控制

| 控制 | 行為 |
|------|------|
| `[−]` | 收合 overlay；log 全高；NETRUN 連線不斷 |
| **Esc** | 關閉 overlay |
| **F12** | 開關 overlay；NETRUN 時預選 `⎈ NET` |
| **F2** | 開啟並切到 `? Help` |

### NETRUN 分頁內容

Meta：`net_shell`、`net_trace`、`net_prompt`、`complete_net_nodes` 等。

- Trace 條；≥80% 警示色。
- 連線節點（locale 名 + 英文 id）。
- 指令速查 — **名稱英文**：`connect`、`breach`、`exploit`、`probe`、`route`、`cat`、`cover`、`exit`；說明用 locale。

### Help 分頁

維持 `help_overlay.py` + 伺服器 `help` fetch。

### 生命週期

| 事件 | Overlay |
|------|---------|
| 進入 `net` | 展開，作用分頁 `⎈ NET` |
| `exit` / 強制斷線 | 關閉 |
| 使用者 `[−]` 收合 | 隱藏直至 F12 或再 `net` |

---

## 快捷鍵（F1–F12）

**側欄改 F11。** 面板由 **F1 起依序**。

| 鍵 | 遊戲內 | 對應 |
|----|--------|------|
| **F1** | PDA | `pda` |
| **F2** | Help overlay | `help` |
| **F3** | 地圖 | `map` |
| **F4** | 裝備 | `equipment` |
| **F5** | 委託 | `gigs` |
| **F6** | Mesh（ctOS 連結） | `mesh` |
| **F7–F10** | *保留* | 日後 client 功能 |
| **F11** | 開關側欄 | 原 F6 |
| **F12** | NETRUN overlay（`⎈ NET`） | 僅 NETRUN 相關 |

| 鍵 | 其他 |
|----|------|
| **Tab** | 指令補全 |
| **Esc** | 關 overlay |

### 登入畫面

| 鍵 | 僅登入 |
|----|--------|
| **F8** | 清除記憶帳密（由原 F7 登入行為遷移） |

實作時同步：`app.py` BINDINGS、`ui_format.py`、locale、`docs/player/CLIENT*.md`。

---

## 側欄 + NETRUN（CU.4–CU.5）

### Mesh 面板（CU.5）

- 新伺服器 **`mesh`** 面板指令 → `@ui`（`format_mesh_map_lines`）。
- Client `resolve_panel_command("mesh")`。
- 空狀態：locale 提示先 `probe`。

### NETRUN 自動開 mesh

`net_shell=1` 且 `netrun_sidebar_auto`（預設 on）：

1. 儲存側欄快照。
2. 開側欄並 fetch **mesh**。
3. 使用者 **F11** 關閉後不強制重開。
4. 離開 NETRUN 還原快照。

關閉自動：`/overlay netrun-sidebar off`（CU.5，可寫入 client settings）。

---

## Status strip（CU.1）

合併 `#info_bar` + `#chrome_bar` → `#status_strip`；連線狀態僅在 waiting / slow / reconnect 時顯示。遵守 `min-height: 1`。

---

## NETRUN log 樣式（CU.4）

NETRUN 輸出 cyan/magenta；實體 `look`/`scan` 維持 env channel；`net_shell=1` 時 scrollback 可選邊框 tint。

---

## 語系

| UI | 語言 |
|----|------|
| 分頁標籤 | 圖示 + 短 **英文**（`⎈ NET`、`? Help`） |
| 說明、警告、空狀態 | `locale` |
| HUD 指令名 | **僅英文** |

---

## 交付分期

| 階段 | 項目 | 驗收 |
|------|------|------|
| CU.1 | Status strip 合併 | 24 行終端可見 prompt |
| CU.2 | `#overlay_panel` + 分頁列 | F2 help；點擊切換 |
| CU.3 | NETRUN HUD | `net` 展開；trace 條 |
| CU.4 | Log 樣式 + F11/F12 + 側欄快照 | 進出 NETRUN 還原側欄 |
| CU.5 | `mesh` 面板 + 自動開 + 設定 | NETRUN 預設 mesh |
| CU.0 | 登入 ASCII 輪巡（8–12s） | **獨立 commit** |

**建議順序：** CU.1 → … → CU.5，再 CU.0。

---

## 風險

- Overlay 50% 高：實機驗證 `size.height`（見 CLIENT_UI_DEBUG）。
- F 鍵重編：玩家文件需同批更新。
- 登入 F8 清除帳密須 gated（僅未 `authenticated`）。