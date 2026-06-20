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

| # | 項目 | 驗收 | 狀態 |
|---|------|------|------|
| E.1 | Client 自動重連 | 斷線後恢復、重送 auth | ✅ |
| E.2 | `./run.sh --dev` 熱重載 | 改 code/data 可重載 | ✅ |
| E.3 | 側欄裝備自動刷新 | equip 後 F2/F5 即時更新 | ✅ |
| E.4 | 文件 GitHub 風格 + TOC | `docs/` 一致格式 | 待做 |

**原專案 commit 參考**：`34d5525`（側欄刷新）

## 已完成（原 Backlog）

| 項目 | 驗收 |
|------|------|
| `tools/generate_world.py` | `python -m tools.generate_world <district> <rows> <cols>` 輸出房間 YAML |
| `admin.sh delete-save <name>` | 刪除 `data/saves/<name>.json` |
| Prompt 擴充 token（`%w` `%g` `%p` `%f` `%m`）與 `prompt template` | `prompt show` 列出 token；`prompt template street` 套用 CP2077 範本 |
| Client NETRUN 模式 | `net_shell=1` meta 時阻擋一般指令；`/exit` 送 `exit` |
| NETRUN server 端 | `net`／`netrun` 進入駭入層；`hack`／`probe`／`exit` |
| `pledge`／`recall`／`talk`／`say`／`learn`／`mod` | 派系、任務、技能、武器模組 |
| NPC 敵意追擊 flee | `aggro` NPC 逃脫失敗後追擊、同房再開戰 |
| 天氣影響戰鬥／移動 | `world/modifiers.py` 修正傷害、flee、移動 |
| 被動技能與義體觸發 | `combat/passives.py`（義臂、breach_protocol） |
| 店鋪開閉、NPC 作息 | `data/shops.yaml`、`data/schedule.yaml`、`world/schedule.py` |
| Client 登入介面 | 半高隨機 ASCII、登入/註冊表單、密碼遮罩 |
| Client 主題（Themes） | 7 款致敬風格、`/theme`、`~/.config/cyber_mud/settings.json`、登入下拉選單 |
| Client 登入 ASCII 程序生成 | 12 種場景（天際線、矩陣雨、Tron 網格等），依主題加權、每次登入隨機 |
| Client 主介面現代化 | Grok CLI 風格 scrollback + prompt dock、`client/tui_styles.py` |
| Client 登入／遊戲版面修正 | 輸入框可見、art 高度、`VerticalScroll`、RichLog 不搶焦點 |
| Client 側欄修正 | `VerticalScroll`、`room_id` 觸發 map 刷新、優先 `@ui` JSON（防 PDA／map 重複） |
| 物品／NPC 英文後綴 | `look`／`scan`／`inventory` 顯示 `中文名 (EnglishName)`，方便打指令 |
| Tab 自動補全 | `shared/completion.py`、`MudSuggester`、`@meta complete_*`、Tab 接受建議 |
| 快捷鍵列 | `#hotkey_bar` 常駐顯示 Tab／F2–F6／`/reconnect`／Ctrl+C |
| 輸出動畫前綴 | `client/output_prefix.py`、Braille spinner（⠋⠙⠹…）、依 MOTD／SYS／ERR 著色 |
| Client 重新連線 | 斷線指數退避（最多 5 次）、`/reconnect` 手動重連、恢復後重送 auth、`client/reconnect.py` |
| Server 程式碼熱重載 | `server/code_reload.py`；`--dev` 監看 `commands/` 等 `.py` + `data/*.yaml`，廣播 SYS 並更新 meta |
| Client spinner 執行中指示 | 僅待回應的指令列（echo）旋轉；回應後改 `❯`；其餘 log 靜態 `›` |
| Client 狀態動畫指示 | `client/status_indicators.py`；戰鬥 ⚔、任務 ▸、低 HP ♥、NETRUN ⎈ 進行中旋轉 |
| 戰鬥 CD 秒數倒數 | `combat_cd` meta 改秒、`client/cd_display.py`；狀態列 `P:45s N:30s` 與 log 冷卻行每秒倒數 |
| NPC 離房結束戰鬥 | `combat/encounter.py` `npc_in_player_room`、`combat/actions.py` `resolve_npc_departed`；巡邏／作息移走敵人時 tick 或下指令皆結束 encounter |
| Tab 補全修正 | `client/completion.py` `MudPrompt` 攔截 Tab（避免 Textual `focus_next`）、`client/app.py` `_apply_prompt_completion` 同步 fallback |
| 戰鬥節奏加速 | `COMBAT_TICK_SECONDS=3` 獨立 `combat_tick_loop`；玩家 CD 3s、NPC CD 6s（不再綁 30s 世界 tick） |
| 效能優化 | 戰鬥 CD tick 靜默（不推 meta／存檔）；戰鬥事件只送 `combat_meta`；client spinner 0.2s；無 encounter 時戰鬥 loop 休眠 30s |
| 側欄 stack 多面板 | `sidebar_stack`／`sidebar_panels`；F2–F5 疊加 PDA＋地圖等；再按同鍵關閉該面板 |
| 啟動狀態／載入耗時 | `shared/startup.py` `StartupReport`；server 終端摘要＋client 登入 hint；連線後 SYS 推送伺服器就緒時間 |
| Client 輸入歷史 | `client/history.py` `CommandHistory`；`MudPrompt` ↑↓／Ctrl+P/N 瀏覽、Esc 還原草稿、可編輯後送出；`~/.config/cyber_mud/command_history.json` |
| Client 記憶帳密／PIN | `client/credentials.py` PBKDF2 + AES-GCM 加密；登入畫面 PIN 快速解鎖、勾選記住＋設定 PIN、F7 清除；`~/.config/cyber_mud/credentials.json`（0600）；修正登入成功文字先於 auth meta 時仍寫入憑證 |
| look 目標察看 | `look <物品|NPC|裝備槽|equipment>` 顯示描述、位置、數值與戰鬥 HP；Tab 補全 `complete_equipped` |
| quit 登出回登入畫面 | `quit` 改為登出（保持連線、不觸發重連）；client `auth=0` 回到登入 UI |
| 側欄 stack 焦點修正 | 側欄不可搶焦點、點擊回 prompt；panel 刷新序列化避免 PDA+地圖並行卡住 |
| Client 連線狀態列 | `#link_status_bar` 顯示連線／等待／延遲；log 增量 append、spinner 不再每 0.2s 全量重繪 |
| NPC 屍體與搜刮 | 擊倒留屍體、`take <物品> from <屍體>`、`look`／`scan` 顯示；tick 腐化掉落地上；`world/corpses.py`、`entities/corpse.py`、`tests/test_corpses.py` |
| 屍體英文後綴 | `corpse_label` 顯示 `(Street Thug)`／`(corpse)` 方便指令；`tests/test_corpses.py` |
| 新手區擴充 | `data/world.yaml` 訓練場 5 房、4 NPC、8 裝備物品；`tutorial_terminal`；`tests/test_tutorial_zone.py` |
| 商店與交易 | `shop`／`buy`／`sell`、`data/shops.yaml`、`world/trade.py`；註冊 ${STARTING_GOLD}；`tests/test_trade.py` |
| 環境輸出著色 | `client/env_format.py` 房間／出口／物品／NPC 分色；`tests/test_env_format.py` |
| 環境色隨主題 | `client/themes.py` `EnvPalette`／`env_palette_for_theme`；`/theme` 切換重繪 log |
| 出口顯示統一 | `format_room_exits` 僅方向中文＋`(英文)`；描述移除重複出口行；`tests/test_room_exits.py` |
| 消耗品系統 | `use`／`eat`／`drink`；食物／飲料／藥品回復 HP／RAM；`world/consumables.py`；`tests/test_consumables.py` |
| defend 裝備描述 | `combat/defend_style.py` 依護甲／頭盔／武器切換戰鬥與 help 文案 |
| NETRUN 指令放行 | `prepare_netrun_outbound` 正規化 `／probe`；`player_meta` 同步 `net_shell=0`；`tests/test_net_meta_sync.py` |
| 側欄 F6 收合修正 | F6 清空 stack／取消載入；`ui_panel_end` 不再強制重開；`#hotkey_bar` 樣式加強可見 |
| 玩家死亡屍體與重生 | 戰敗留屍、背包＋裝備掉落可搜刮；自動傳送至 `respawn_room`（義體診所）並回滿 HP；`tests/test_player_death.py` |
| 槍械與肉搏戰鬥 | `weapon_type`（gun／blade／blunt）；`shoot`／`slash`／`bash`／`punch`／`backstab`；`combat/styles.py`、`tests/test_strike.py` |
| 連線狀態列可見性 | `#link_status_bar` 加亮、`連線` 前綴、登入後刷新；`tests/test_client_app.py` |
| 快捷鍵列可見性 | `#top_dock`／`#bottom_dock` dock 堆疊；chrome／hotkey `min-height:1`；F 鍵非阻塞 fetch；輸入 `map`／`pda` 等自動開側欄；載入中 F2 再按取消；案例見 [`CLIENT_UI_DEBUG.md`](CLIENT_UI_DEBUG.md) |
| NPC 穿戴裝備 | `entities/npc.py` `equipment`；`look` 顯示穿戴；擊倒後與 `loot` 一併進屍體；`tests/test_npc_equipment.py` |
| 自然回血 | `world/vitals.py` 依 `body`／`cool`／時段 tick 回復；非戰鬥中推送 meta＋訊息；`tests/test_vitals.py` |
| NPC 重生 | `world/npc_respawn.py` 擊倒排程、tick 復活並廣播進房；`respawn_minutes`／`tier: boss`（預設 10 分、boss 60 分）；`tests/test_npc_respawn.py` |
| 指令重複 | `shared/repeat.py` `10 punch`／`punch.10`；每次間隔 `REPEAT_INTERVAL_SECONDS`（0.5s）；`tests/test_repeat.py` |
| Server heartbeat | `server/heartbeat.py` 終端單行定期刷新 tick／連線／戰鬥等狀態；dev 重載輸出 log；`tests/test_heartbeat.py` |
| CP2077 裝備槽與武器種類 | `shared/equipment.py` 七槽（weapon／head／inner_torso／outer_torso／legs／feet／cyber）；CP2077 遠程武器種類＋power／tech／smart／melee；`armor` 存檔遷移；`tests/test_equip.py` |
| NETRUN 英文後綴 | `net_node_label_with_id`；`net`／`probe`／`hack`／`status` 節點與地上物品顯示 `(English)`；`hack` Tab 補全節點 id；`tests/test_net.py` |
| NETRUN 環境／NPC 互動 | `look`／`scan`／`talk`／`say` 於 NETRUN 放行；`look`／`scan` 顯示節點；client 同步放行；`tests/test_net.py` |
| 武器持握模式 | `weapon_primary`／`weapon_secondary`；`weapon_mode` 主要／次要／雙手／雙持；`training_carbine`；`tests/test_equip.py` |
| 等級／技能／天賦 | `world/progression.py` XP 升級、屬性點／天賦點；`stats`／`talents`／`improve`／`learn` 等級前置；`data/talents.yaml`；擊倒 NPC／駭入成功給 XP；`tests/test_progression.py` |
| 街頭聲望與委託 | `street_cred`；`gigs` Fixer 委託板；`world/quests.py` 委託目標／交件／獎勵；`broker_rumor` 完整流程；`tests/test_gigs.py` |
| CP2077 快速破解 | `data/quickhacks.yaml` 過熱／短路／光學重啟／突觸燒毀；`quickhack <名稱>`；狀態效果灼燒／短路／致盲；`tests/test_quickhacks.py` |
| 義體幻痛 | `world/cyberpsychosis.py` 人性 ≤25 時輸出 -15% |
| CP2077 義體槽位 | 九槽 `cyberware`／`chrome`／`uninstall`；`data/implants.yaml` 擴充；ripperdoc 限定；`tests/test_cyberware.py` |
| 住宅與儲物 | `rent`／`home`／`stash`；`watson_flat`；`data/housing.yaml`；`tests/test_housing_transport.py` |
| 交通與載具 | `transit` NCART；`vehicles buy`／`drive`；`data/transit.yaml`／`vehicles.yaml` |
| Tab 補全多候選輪替 | `shared/completion.py` `complete_input_cycle`；client `_completion_cycle_index`；`tests/test_backlog_features.py` |
| 環境互動系統 | `interact`；`data/interactables.yaml`；`world/interactables.py`；整合 `look`／`scan`；`tests/test_backlog_features.py` |
| 上下方向移動 | `go up`／`go down`；`u`／`d` 別名；`square_rooftop`／`undercity`；locale `direction.up/down` |
| Prompt 擴充 token | `%l` `%c` `%v` `%x`；範本 `ncpd`／`runner`；`shared/prompt_tokens.py` |
| NPC 任務多階段 | `world/quests.py` `stages`；`dock_watch` 委託；`tests/test_backlog_features.py` |
| 天氣／時段玩法平衡 | `world/modifiers.py` 時段修正傷害／逃跑／移動；`tests/test_modifiers.py` 更新 |
| 被動技能樹與義體連鎖 | `data/passive_chains.yaml`；`combat/passives.py` `_active_chains`；XP 加成 |
| NCPD 通緝 | `world/wanted.py`；擊倒 NPC 升級；tick 衰減；`wanted` meta |
| 多載具車庫 | `world/vehicles_player.py`；`vehicles buy/select`；`vehicles[]` 存檔 |
| 製作／拆解 | `craft`／`disassemble`；`data/recipes.yaml`；`world/craft.py` |
| 腦舞 | `braindance`／`bd`；`data/braindances.yaml`；`world/braindance.py`；艙體互動 |

## Backlog 維護慣例

**每次修正或功能變更完成後**，在合併／commit 前更新本檔：

1. **已完成** → 加入「已完成（原 Backlog）」表格（項目 + 驗收／模組）
2. **待做／後續** → 加入下方「Backlog」清單；做完則移入已完成並刪除
3. **摘要** → 同步更新 [`CLAUDE.md`](../CLAUDE.md) Backlog 一節（近期完成表）

Agent／協作者亦同：交付前若改動遊戲或 client 行為，**必須**更新 backlog，不得僅改程式不留紀錄。

## Backlog

尚未實作或僅部分實作，新專案可選做：

- Prompt 完整版（client 即時預覽 UI）
- NPC 任務驅動 AI（進階追蹤、任務編排工具）
- 文件 GitHub 風格 + TOC（Phase E.4）
- pyenv 原生編譯 Python（環境設定，非遊戲功能）

---

建議路線：**0 → A → D.2/D.7（可玩性）→ B → C → D 其餘 → E**；若新 MUD 偏社交探索，可先做 B 再做 C。

世界觀與區域、派系設定見 [WORLD.md](WORLD.md)。