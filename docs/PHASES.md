# 分階段實作清單

對應原 **mud** 專案開發歷程，供 **cyber_mud** 排程與驗收。每階段完成後跑 `pytest` 並 commit 一次大項。

## 目錄

- [Phase 0：MVP](#phase-0mvp)
- [Phase A：時間、Tick、屬性](#phase-a時間tick屬性)
- [Phase B：NPC、天氣](#phase-bnpc天氣)
- [Phase C：即時戰鬥](#phase-c即時戰鬥)
- [Phase D：批量與 UI 拋光](#phase-d批量與-ui-拋光)
- [Phase E：維護與體驗](#phase-e維護與體驗)
- [Backlog](#backlog)

## Phase 0：MVP

| # | 項目 | 驗收 |
|---|------|------|
| 0.1 | TCP server + 單行協定 | `nc` 可連、收 MOTD |
| 0.2 | 世界載入 + look/go | 可在 3+ 房間移動 |
| 0.3 | 登入註冊 + 存檔 | 重連保留進度 |
| 0.4 | take/drop/inventory | 物品可撿可丟 |
| 0.5 | Textual client 主 log + 狀態列 | `./run.sh --client` 可玩 |
| 0.6 | help 指令 | 列出可用指令 |

## Phase A：時間、Tick、屬性

| # | 項目 | 關鍵檔案 | 驗收 |
|---|------|----------|------|
| A.1 | 世界時鐘 | `world/clock.py`, `data/time.yaml` | `time` 指令、meta `time`/`period` |
| A.2 | Server tick loop | `world/tick.py`, `server/game.py` | 時鐘隨現實時間推進 |
| A.3 | CP2077 五維 + 人性聲望 | `entities/player.py` | `pda` 顯示完整 vitals |
| A.4 | RAM／義體基礎 | `commands/install.py`, cyber helpers | 安裝義體影響屬性 |

**原專案 commit 參考**：`52aeccc`（含 A/B/C 一批交付）

## Phase B：NPC、天氣

| # | 項目 | 關鍵檔案 | 驗收 |
|---|------|----------|------|
| B.1 | 區域天氣 | `world/weather.py` | `look` 或狀態列見天氣 |
| B.2 | NPC tick 移動 | `world/tick.py`, NPC 資料 | NPC 會換房 |
| B.3 | 進出察覺 | 廣播 / look 訊號 | 同房可見 NPC 進出 |
| B.4 | NPC 閒置動作 | tick + 節流 | 不洗版但有氛圍 |

## Phase C：即時戰鬥

| # | 項目 | 關鍵檔案 | 驗收 |
|---|------|----------|------|
| C.1 | Encounter 狀態 | `combat/encounter.py` | 開戰後 `in_combat` 成立 |
| C.2 | 玩家指令 | `attack`, `defend`, `flee`, `quickhack` | 戰鬥中可下指令 |
| C.3 | Tick 推進 | `process_tick` | NPC 依 CD 反擊 |
| C.4 | Client 戰鬥 UI | `hint_bar`, meta `combat_*` | 狀態列／hint 顯示戰況 |

## Phase D：批量與 UI 拋光

| # | 項目 | 驗收 |
|---|------|------|
| D.1 | take/drop/equip/unequip all | `全部`、`*` 可用 |
| D.2 | F2–F5 側邊欄 | pda/help/map/equipment |
| D.3 | `@ui` JSON 側欄 | 結構化段落 |
| D.4 | Prompt token 擴充 | `%` token 與 client `/prompt` |
| D.5 | scan + search 合併 | 探索體驗一致 |
| D.6 | give、appraise | 交易與估價 |
| D.7 | look 輸出修正 | 主 log 顯示房間（非側欄、非 JSON 洩漏） |

**原專案 commit 參考**：`3cf9466`, `7623666`

## Phase E：維護與體驗

| # | 項目 | 驗收 |
|---|------|------|
| E.1 | Client 自動重連 | 斷線後恢復 |
| E.2 | `./run.sh --dev` 熱重載 | 改 code/data 可重載 |
| E.3 | 側欄裝備自動刷新 | equip 後 F2/F5 即時更新 |
| E.4 | 文件 GitHub 風格 + TOC | `docs/` 一致格式 |

**原專案 commit 參考**：`34d5525`（側欄刷新）

## Backlog

尚未實作或僅部分實作，新專案可選做：

- Prompt 完整版（更多 token、即時預覽、CP2077 範本）
- NPC 依任務／敵意追蹤 flee
- 天氣影響戰鬥／移動數值
- 被動技能與義體自動觸發
- 時間驅動店鋪開閉、NPC 作息表
- pyenv 原生編譯 Python（非必要）

---

建議路線：**0 → A → D.2/D.7（可玩性）→ B → C → D 其餘 → E**；若新 MUD 偏社交探索，可先做 B 再做 C。

世界觀與區域、派系設定見 [WORLD.md](WORLD.md)。