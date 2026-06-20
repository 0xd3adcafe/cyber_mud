# 分階段實作清單

> **English:** [PHASES.md](PHASES.md)

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
| E.4 | 中英文文件分離 + README ASCII banner | `*.zh.md` 對照；GitHub 預設英文 | ✅ |

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
| 目標消歧 TD.1–TD.5 | `shared/target_resolve.py`；`target.*` locale；look／物品／NPC／戰鬥／環境／商店指令統一序號與範圍；`tests/test_target_resolve.py` |
| quit 登出回登入畫面 | `quit` 改為登出（保持連線、不觸發重連）；client `auth=0` 回到登入 UI |
| 側欄 stack 焦點修正 | 側欄不可搶焦點、點擊回 prompt；panel 刷新序列化避免 PDA+地圖並行卡住 |
| Client 連線狀態列 | `#link_status_bar` 顯示連線／等待／延遲；log 增量 append、spinner 不再每 0.2s 全量重繪 |
| NPC 屍體與搜刮 | 擊倒留屍體、`take <物品> from <屍體>`、`look`／`scan` 顯示；tick 腐化掉落地上；`world/corpses.py`、`entities/corpse.py`、`tests/test_corpses.py` |
| 屍體英文後綴 | `corpse_label` 顯示 `(Street Thug)`／`(corpse)` 方便指令；`tests/test_corpses.py` |
| 新手區擴充 | `data/world.yaml` 訓練場 9 房、10 NPC（含 `patrol_dummy`）；簡報室／餐廳／障礙道／模擬診所；`trainee_ration`／`training_smartgun`；`data/interactables.yaml` 4 互動點；`data/shops.yaml` tutorial_supply；locale `talk.*`；`tests/test_tutorial_zone.py` |
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
| 遊戲狀態列可見性 | `#info_bar` `min-height:1`；移除 `max-height:1`（Textual `size.height=0` 終端空白）；`tests/test_client_app.py` 斷言 `info.size.height` |
| 地圖側欄效能 | `_render_sidebar` 延遲至 `ui_panel_end`；meta 狀態列合併刷新；`map` 僅送 `@ui`（不重複 `@panel` 行）；`test_panel_stream_defers_sidebar_render_until_end` |
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
| CP2077 熟練度（2026-06） | `data/proficiencies.yaml`；`world/proficiencies.py` 使用升級 1–60（五屬性樹）；戰鬥／駭入／製作／移動給 XP；傷害／快速破解加成；`stats` 熟練度面板；`tests/test_proficiencies.py` |
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
| NPC 派系動機 AI | `faction`／`motivation`；`data/npc_ai.yaml`；`world/npc_ai.py` 同房交戰／社交／追獵；`tests/test_npc_ai.py` |
| 登入 banner MOTD 動態展示 | `client/login_motd.py`；`motd.tips` locale；`#login_title` 輪播提示＋spinner；MOTD 不再覆寫 `#login_status`；`tests/test_login_motd.py` |
| Prompt 完整版（client 即時預覽） | `client/prompt_preview.py`；`#prompt_preview` 輸入時展開 token；`/prompt template`／`show`／`reset`；meta `prompt_template`／`xp`；`tests/test_prompt_preview.py` |
| NPC 任務編排工具 | `world/quest_author.py`；`tools/quest_author.py`；`./admin.sh quests list/show/validate/npc/scaffold`；`tests/test_quest_author.py` |
| 完整任務系統 | `world/quests.py` `accept`／`abandon`／`requires_quest`／`reward_items`；目標 `defeat_npc`／`have_item`；`gigs accept`／`journal`；`alley_clearance`；`tests/test_quest_system.py` |
| Help log 區 dropdown | `client/help_overlay.py`；`#help_dropdown` 覆蓋 `#scrollback_wrap`；F3／`help`／Esc 切換；不再進側欄 stack；`tests/test_help_overlay.py` |
| 新手區二次擴充 | 簡報室 `rookie_fixer`／餐廳 `canteen_tech`／靶場 `range_officer`／義體診所 `clinic_tutor`／障礙道 `course_guide`＋`patrol_dummy`；互動委託板／儲物櫃／掃描柱／示範主機；`tests/test_tutorial_zone.py` 10 項 |
| Gigs 側邊欄追蹤 | `gigs`／`journal` → `ok_panel`；`commands/gigs_helpers.py`；F7 快捷鍵；`quest`／`hint` meta 自動刷新；`tests/test_gigs.py` |
| Help 指令分類 | `commands/help_cmd.py` `HELP_CATEGORIES`；locale `help.category.*`；overlay 分類標題；`tests/test_help_cmd.py` |
| Focus 追蹤區塊 | `client/focus_block.py` prompt 上方；委託／戰鬥／執行中；漸層 accent＋計時；`focus_palette_for_theme`；`tests/test_focus_block.py` |
| 雙語英文預設 | 預設 `locale=en`；`lang` 指令；`server.*`／`client.*` locale；`docs/LOCALIZATION.md`；commit 英文主述；`tests/test_lang.py` |
| Client chrome 語系 | `client/ui_format.py` 側欄標題／快捷鍵列；`lang` meta 刷新 chrome；`client.ui.*` locale；`tests/test_ui_format.py` |
| Prompt 輸入提示語系 | `#prompt` placeholder `client.ui.prompt_placeholder`；`_refresh_prompt_placeholder` |
| Client clear 清除 log | `/clear` 本機指令；`AnimatedLogBuffer.clear()`；Tab 補全；`tests/test_client_app.py` |
| 中英文文件分離 | 英文 `*.md` GitHub 預設；中文 `*.zh.md` 對照；README ASCII banner |
| 英文預設語系寫入專案規則 | `CLAUDE.zh.md` § 專案規則（強制）；`LOCALIZATION.zh.md` § 專案規則；README 核心原則 #1 |
| 專案授權 | `LICENSE` Apache 2.0（程式）；`LICENSE-CONTENT.md` CC BY 4.0（文案）；README badge；`CONTRIBUTING.md` |
| 玩家指南（GitHub） | `docs/player/` ASCII 風格 tutorial／commands／client；中英對照；README 玩家區 |
| 成人／NSFW 內容 M.0–M.17 | `mature_social.py`、戰鬥廣播、mature say/presence、浪漫送禮、`taunt`/`finish`；`docs/MATURE_CONTENT.md` |
| Kabuki 與區域擴充（2026-06） | `kabuki_vip`、`kabuki_bazaar`、小中國街、企業區樞紐；`velvet_job`；`tests/test_world_districts.py` |
| Client 版面測試 helper | `tests/client_ui_helpers.py`；`test_client_app.py` 側欄／help overlay 穩定斷言 |
| 生活指令 L.1–L.8（2026-06） | `sit`／`stand`／`lie`／`rest`／`sleep`／`wake`；`world/life.py`、`data/life.yaml`；互動休息錨點；生命徵象／RAM 回復；移動／說話／戰鬥喚醒；PDA＋`%posture`；help 分類 **生活與生命徵象**；`tests/test_life_commands.py` |
| 生活指令後續補齊（2026-06） | 活動累積疲勞（`move`／`combat`／`netrun`）；區域 `safety` 戶外睡眠門檻；休息時段／天氣倍率於 `world/modifiers.py`；毒素禁止睡眠；高疲勞降低回血；`tests/test_life_commands.py`、`tests/test_modifiers.py` |
| 世界擴充 W.4–W.5、W.11（2026-06） | 主線錨點 `crypt`、`data_vault`；NPC `guard`／`priest`／`rat`；`plaza_terminal`／`vault_terminal`；`hack_core` 任務＋`hack_net` 目標；net 節點 `crypt_node`／`vault_core`；`tests/test_story_anchors.py`、`tests/test_net_story.py` |
| 世界擴充 W.1、W.2、W.14 規模（2026-06） | `tools/merge_world_grid.py`；8 區生成格點→**263 房**；樞紐 `tyrell_plaza`、`combat_zone_gate`；樞紐↔格點連接；`tests/test_world_scale.py`；`admin.sh validate` 統計 |
| 世界擴充 W.3、W.6、W.7（2026-06） | `data/districts.yaml` 安全／氛圍；`look` 敘事；巡邏／aggro／天氣權重；`help tutorial`；`tyrell_intel`＋派系商店／對話／區域門檻；`tests/test_districts.py`、`tests/test_help_tutorial.py`、`tests/test_factions.py` |
| 世界擴充 W.8–W.10（2026-06） | `data/schedule.yaml` 商店營業＋時段巡邏倍率；NPC schedule（`bazaar_fixer`、`dock_smuggler`、`corp_guard`）；`docks_gray` 灰市＋`gray_market` 任務（`give_npc`）；企業／街頭 `appraise`；`give <物品> <NPC>`；`go` 觸發 `presence.enter`／`leave`；`say`／`give` 廣播排除發送者；`tests/test_schedule.py`、`tests/test_black_market.py`、`tests/test_multiplayer.py` |
| 世界擴充 W.12–W.13（2026-06） | `poison` tick＋`antidote` 消耗品；玩家 `overheat` debuff（快速破解反噬）；`world/reactions.py` 聲望變動（宣誓／駭入／戰鬥）；經紀人聲望／通緝對話；tick `ambient_tick`＋`trauma_tick` 廣播；`tests/test_status_effects.py`、`tests/test_world_reactions.py` |
| 世界擴充 W.14（2026-06） | `tools/expand_world_population.py`＋`data/world_population.yaml` 覆蓋層；**109 NPC**、**45 物品**（263 房格點）；loader 合併；`tests/test_world_scale.py` |
| 內容深度 D.1–D.6（2026-06） | 原型 `talk.*`＋重產 population；任務 WARN 修復＋`hub_briefing`；樞紐 NPC；格點戰利品 craft/disassemble＋商店；8 區 net 節點＋互動物；`tests/test_content_depth.py`；[WORLD_TOOLS.zh.md](WORLD_TOOLS.zh.md) |
| 內容深度 D.7–D.10（2026-06） | 八區聚光 NPC；`district.grid.*` look 敘事；四條區域委託；完整 `world.ambient.*`；`tests/test_content_depth.py` |
| Client 單獨 `/` 輸入修復 | `is_local_command("/")` 不再 IndexError；顯示 `client.local_command.usage`；未知 `/foo` 留本機；`tests/test_client_meta.py`、`tests/test_client_app.py` |
| Validate 加速（2026-06） | 快取 `load_world`／`default_room_items`／時段與天氣 YAML；`pytest-xdist` 平行 pytest；dev reload 呼叫 `clear_world_cache()`；約 6 分鐘→約 50 秒 |
| 安全性 ASVS L1 ASVS.1–5（2026-06） | PBKDF2 密碼＋舊版自動升級；統一 `invalid_credentials`；存檔路徑驗證；輸入邊界；每連線認證速率限制；存檔 `0600`；`docs/SECURITY.md`；`tests/test_security_auth.py` |
| 新手教學區 T.2–T.7（2026-06） | `tutorial_debrief`；3 NPC；8 互動物；3 物品；`tutorial_rotation` 委託；`tests/test_tutorial_zone.py` 13 案例 |
| PDA 整合成長面板（2026-06） | 單一 `pda` 合併生存、熟練度、協定、完整天賦目錄；`build_pda_ui` 側欄區塊；`stats`／`talents` 不變；`tests/test_pda.py` |
| 側欄刷新效能（2026-06） | `client/sidebar_refresh.py` 防抖抓取（2s）+ 15s 定時；meta 局部更新 PDA；合併 `_render_sidebar`；`tests/test_sidebar_refresh.py` |

## 多 session 開發（必做）

新對話或平行 session **動手改程式前**先與 repo 對齊：

```bash
git fetch origin 2>/dev/null || true
git status -sb
git log --oneline -15
git log origin/master..HEAD --oneline 2>/dev/null
pytest tests/ -q --tb=no || true
./admin.sh validate 2>/dev/null | tail -3 || true
```

接著讀本檔 **Backlog** 與 [`CLAUDE.md`](../CLAUDE.md) 近期完成表；`git log` 或「已完成」已有的項目勿重複實作。

## Backlog 維護慣例

**每次修正或功能變更完成後**，在合併／commit 前更新本檔：

1. **已完成** → 加入「已完成（原 Backlog）」表格（項目 + 驗收／模組）
2. **待做／後續** → 加入下方「Backlog」清單；做完則移入已完成並刪除
3. **摘要** → 同步更新 [`CLAUDE.md`](../CLAUDE.md) Backlog 一節（近期完成表）

Agent／協作者亦同：交付前若改動遊戲或 client 行為，**必須**更新 backlog，不得僅改程式不留紀錄。

## Backlog

尚未實作或僅部分實作。

### 環境

- pyenv 原生編譯 Python（環境設定，非遊戲功能）

### 架構（增量）

**目標：** 借鏡 Evennia 有用模式，不做全面 Entity 遷移——在現有 `world/tick.py` 上疊加 YAML 權限與延遲排程。

| 階段 | 項目 | 模組／驗收 |
|------|------|------------|
| ~~ARCH.1~~ | ~~Lock 簡化版（YAML 條件）~~ | ✅ `shared/locks.py`；`commands/lock_helpers.py`；房間／物品／節點／互動物 `locks:`；`go`／`use`／`hack`／`interact`；`data_vault`＋`vault_core` 範例；`tests/test_locks.py` |
| ~~ARCH.2~~ | ~~Scheduler 薄層~~ | ✅ `world/scheduler.py`；`tick_count` 單次／間隔＋取消；`world_state.json` 恢復；安裝義體 `side_effect_minutes`；`tests/test_scheduler.py` |

**建議順序：** ARCH.1–2 已交付。**延後實作**（承接已刪除 `TODO.md` 的 Phase 1.2–1.3 範圍）。

### 監控駭客（Watch Dogs 致敬）

**原則：** 致敬 **全連網城市監控** 玩法（ctOS 式城市 OS、Profiler 情報、基礎設施入侵）——非 Ubisoft IP、角色或芝加哥地理。夜城維持 Blade Runner + CP2077 調性；借 **系統與氛圍**，不搬劇情正典。

**Watch Dogs 分析（可借鏡項）：**

| 層次 | Watch Dogs（育碧） | 夜城現況 | 缺口 |
|------|-------------------|----------|------|
| **世界** | Blume **ctOS** 統管交通、橋樑、蒸汽、監視；**DedSec** 對抗企業 | 區域、企業 tag、`data_vault`、泰瑞監控氛圍 | 缺少城市級 OS 層；駭客仍以節點／戰鬥為主 |
| **Profiler** | 掃描路人→職業、收入、特質、前科；解鎖社交／戰鬥駭入 | `scan` 列實體；`look <npc>` 看數值 | 無持久 **情報檔** 與特質閘門 |
| **駭入** | 對 **連網物件** 情境駭入（斷電、交通、干擾、橋樑） | NETRUN `hack`/`probe`；戰鬥 `quickhack` | 房間 **基礎設施** 互動少 |
| **經濟／委託** | **Fixer** 合約、隱私入侵、車隊 | `gigs`／多階段任務、街頭聲望 | 少 **先掃描再行動** 目標 |
| **熱度** | 犯罪與駭入失敗引警方 | `wanted_level`（NCPD） | 監控區無 **數位足跡** |
| **成長** | 駭客／戰鬥／駕駛技能樹 | 技能、天賦、專精、義體 | 缺 **環境控制** 駭客枝 |

**目標：** 以文字 MUD 呈現 Profiler 情報、基礎設施駭入、監控熱度——複用 NETRUN、`scan`、`wanted`、gigs、ARCH.1 鎖、ARCH.2 排程。

**Client（2026-06 已交付）：** `/theme` 與登入下拉 — `ctos`（城市 OS 監控青）、`dedsec`（駭客行動洋紅／青）、`profiler`（情報琥珀／青）；`client/themes.py`、`login_art.py`；`tests/test_themes.py`。

| 階段 | 項目 | 模組／驗收 |
|------|------|------------|
| WD.1 | Profiler 資料模型 | `data/profiler.yaml` NPC `profile:`；`Player.profiled_npcs`；`scan <npc>` 快取情報；`profiler.*` locale；`tests/test_profiler.py` |
| WD.2 | 基礎設施房間 tag | `power_grid`、`traffic`、`surveillance`、`steam`；`look`/`scan` 顯示 ctOS 連線物件 |
| WD.3 | 環境駭入（NETRUN） | `blackout`、`jam_signals`、`overload` 等；`world/modifiers.py` 時段／天氣；RAM＋聲望消耗；`tests/test_ctos_hacks.py` |
| WD.4 | 數位足跡與監控熱度 | `Player.footprint`；企業區駭入累積；拉高通緝／企業 NPC 敵意；PDA 列；`tests/test_footprint.py` |
| WD.5 | Profiler 社交工程 | `talk` 依已掃描特質分支；賄賂物品；任務 flag；`tests/test_profiler_talk.py` |
| WD.6 | Fixer Profiler 合約 | `scan_npc`、`profile_trait`、`hack_infra` 目標；`tests/test_profiler_gigs.py` |
| WD.7 | 干擾巡邏 NPC | `jam`/`distract` 跳過巡邏或降敵意；`tests/test_ctos_distract.py` |
| WD.8 | ctOS 節點連線圖 | `net_nodes.yaml` `links:`；`probe`／側欄顯示已發現網路；`tests/test_ctos_mesh.py` |
| WD.9 | 排程城市事件 | ARCH.2 觸發區域斷電／交通鎖；`scheduler.ctos_*` 廣播；`tests/test_ctos_events.py` |
| WD.10 | DedSec 派系與教學 | `dedsec` `pledge`；教程 Profiler 關卡；help **City OS**；`tests/test_dedsec.py` |

**建議順序：** WD.1 → WD.2 → WD.3 → WD.4（系統核心）→ WD.8 → WD.5 → WD.6 → WD.7 → WD.9 → WD.10（內容）。

**延後（文字 MUD 不適合）：** 開放世界駕駛、跑酷、手機 UI 複製、即時多人 ctOS 入侵。

### 成人／NSFW 內容（18+）

**原則：** 原創致敬風賽博龐克；所有成熟內容 **預設關閉、玩家 opt-in**（`content_rating`／`mature_enabled`），登入與指令層閘門；文案放 **`data/locale/mature_en.yaml`、`mature_zh.yaml`**，不混入預設 MOTD／help。

| 階段 | 項目 | 模組／驗收 |
|------|------|------------|
| ~~M.0~~ | ~~分級與 opt-in~~ | ✅ `Player.content_rating`；`settings mature on\|off`；註冊 `mature`；`world/mature.py`；`tests/test_content_rating.py` |
| ~~M.1~~ | ~~血腥戰鬥~~ | ✅ `combat/gore.py`；擊殺／暴擊／屍體描述；Focus gore 色；`tests/test_gore.py` |
| ~~M.2~~ | ~~傷殘與創傷敘事~~ | ✅ `world/trauma.py`；流血狀態；進診所治療；tick 失血 |
| ~~M.3~~ | ~~成人場景與 NPC~~ | ✅ `kabuki_lounge`、`bd_den`、`kabuki_host`；`tags: [mature]`；mature `talk` |
| ~~M.4~~ | ~~浪漫與親密機制~~ | ✅ `data/romance.yaml`；`flirt`／`spend_time`；`romance_flags` 存檔 |
| ~~M.5~~ | ~~成人腦舞與委託~~ | ✅ `braindances_mature.yaml`、`quests_mature.yaml`；teen 的 `gigs`／`bd` 過濾 |
| ~~M.6~~ | ~~Client 警示與 UI~~ | ✅ 登入 18+ 勾選；help 隱藏 mature 分類；Focus 血色樣式 |
| ~~M.7~~ | ~~編寫與管理~~ | ✅ `mature_validate.py`；`docs/MATURE_CONTENT.md`；CONTRIBUTING 說明 |
| ~~M.8~~ | ~~成熟 look/scan 氛圍~~ | ✅ `world/mature_flavor.py`；`look`/`scan` 房間描述；`look <npc>` 細節 |
| ~~M.9~~ | ~~多階段浪漫台詞~~ | ✅ `romance_line()` `_2`/`_3` 階；擴充 host/dancer/clerk `mature.romance.*` |
| ~~M.10~~ | ~~成熟互動文案~~ | ✅ `world/interactables.py` 覆寫；`lounge_chrome_bar`、`vip_preview_pod`、`bd_den_archive` |
| ~~M.11~~ | ~~密艙櫃台與 chrome_mirage~~ | ✅ `bd_den_clerk` NPC；`chrome_mirage` 腦舞；`chrome_pull` 委託；clerk 浪漫檔 |
| ~~M.12~~ | ~~測試與文件~~ | ✅ `tests/test_mature_content.py` 深度案例；`docs/MATURE_CONTENT.md` 補充 |
| ~~M.13~~ | ~~成熟戰鬥廣播~~ | ✅ 依觀察者 `broadcast_mature_key`；`combat.victory/defeat_broadcast_*` |
| ~~M.14~~ | ~~成熟 say 社交~~ | ✅ `social.say_ok/say_broadcast.<room>` 夜總會／密艙 |
| ~~M.15~~ | ~~成熟 presence 氛圍~~ | ✅ `social.presence_enter/leave.<room>` 進出成熟場景 |
| ~~M.16~~ | ~~浪漫送禮反應~~ | ✅ `world/mature_give.py`；送禮給浪漫 NPC 成熟文案 |
| ~~M.17~~ | ~~戰鬥嘲諷與終結~~ | ✅ `taunt <npc>`；`finish` 弱敵終結技；help 18+ 分類 |

**建議順序：** M.0 → M.1 → M.3 → M.4 → M.5 → M.6 → M.2 → M.7 → M.8–M.17。**全階段已交付（2026-06）。**

### 世界擴充（[WORLD.md](WORLD.md)）

**現況（2026-06）：** **263 房**、**109 NPC**、**45 物品**——已達 WORLD.md 規模目標；區域 `safety`／`atmosphere`；`help tutorial`；派系深度；作息＋灰市；中毒／過熱＋動態世界回饋。**世界擴充 W.1–W.14 已交付**——後續手寫深度見下方 **內容深度**。

| 階段 | 項目 | 模組／驗收 |
|------|------|------------|
| ~~W.1~~ | ~~程序生成區域格點~~ | ✅ `tools/merge_world_grid.py`；區域前綴 ID；`grid_x`/`grid_y`；樞紐↔格點；`tests/test_world_scale.py` |
| ~~W.2~~ | ~~八區房間群~~ | ✅ 8 區併入→**263 房**；`map` 格點；locale `*_en`/`*_zh` |
| ~~W.3~~ | ~~區域安全與氛圍~~ | ✅ `data/districts.yaml`；`look` 氛圍；巡邏／敵意／天氣；`tests/test_districts.py` |
| ~~W.4~~ | ~~主線核心房間~~ | ✅ `crypt`、`data_vault`；地下城圖；新手路徑 |
| ~~W.5~~ | ~~主線錨點 NPC 與戰利品~~ | ✅ `guard`、`priest`、`rat`；`tests/test_story_anchors.py` |
| ~~W.6~~ | ~~`help tutorial` 新手引導~~ | ✅ `help tutorial`；`tests/test_help_tutorial.py` |
| ~~W.7~~ | ~~派系玩法深度~~ | ✅ `pledge tyrell`；派系 talk／商店；`tests/test_factions.py` |
| ~~W.8~~ | ~~區域天氣與作息~~ | ✅ `data/schedule.yaml` 全店營業＋時段巡邏倍率；NPC schedule（`broker`、`bazaar_fixer`、`dock_smuggler`、`corp_guard`）；`patrol_period_multiplier`；`tests/test_schedule.py` |
| ~~W.9~~ | ~~社會與黑市~~ | ✅ `docks_gray` 商店、`dock_smuggler` NPC、`gray_market` 任務（`give_npc`）；企業／街頭 `appraise`；`give <物品> <NPC>`；`tests/test_black_market.py` |
| ~~W.10~~ | ~~多人同屏存在感~~ | ✅ `go` 觸發 `presence.enter`／`leave`；`say`／`give` 廣播排除發送者；同室 `look` 列出玩家；`tests/test_multiplayer.py` |
| ~~W.11~~ | ~~NETRUN 主線節點~~ | ✅ `crypt_node`、`vault_core`；`hack_core`；`tests/test_net_story.py` |
| ~~W.12~~ | ~~延伸狀態效果~~ | ✅ `poison` tick＋`antidote`（`cures_status`）；玩家 `overheat` debuff（快速破解反噬，≠ NPC `burn`）；戰鬥傷害懲罰；`tests/test_status_effects.py` |
| ~~W.13~~ | ~~動態世界回饋~~ | ✅ `world/reactions.py` 聲望變動（宣誓／NETRUN 駭入／戰鬥／快速破解）；經紀人聲望／通緝對話；tick `ambient_tick`；`trauma_tick` client 廣播；`tests/test_world_reactions.py` |
| ~~W.14~~ | ~~世界規模里程碑~~ | ✅ **263 房**、**109 NPC**、**45 物品**；`tools/expand_world_population.py`；`data/world_population.yaml` loader 覆蓋；`tests/test_world_scale.py` |

**建議順序：** W.4 → W.5 → W.11（主線錨點）→ W.1 → W.2 → W.3（地理規模）→ W.6 → W.7 → W.8 → W.9 → W.10 → W.12 → W.13 → W.14。

### 內容深度（W.14 規模之後）

**目標：** 程序格點規模（W.14）達標後，以**手寫**對話、任務、樞紐、經濟與區域掛鉤取代模板填充，讓夜城有生活感而不只是數字達標。

**現況（2026-06）：** **113 NPC**（27 手寫＋86 程序覆蓋）。程序 NPC 使用 21 種原型 `talk.*`。`./admin.sh quests validate` 0 警告。**內容深度 D.1–D.6 已交付。**

| 階段 | 項目 | 模組／驗收 |
|------|------|------------|
| ~~D.1~~ | ~~格點 NPC 對話~~ | ✅ 原型 `talk.*`；`tools/expand_world_population.py`；重產 `data/world_population.yaml`；locale 中英 |
| ~~D.2~~ | ~~格點任務與任務整潔~~ | ✅ `gray_market`／`tyrell_intel`／`velvet_job` 交件 `talk_npc`；`hub_briefing`；`./admin.sh quests` 0 WARN |
| ~~D.3~~ | ~~手寫區域樞紐~~ | ✅ `tyrell_liaison`、`zone_warden`、`plaza_handler`、`gate_herbalist`；樞紐 `look` 敘事 |
| ~~D.4~~ | ~~物品敘事與經濟~~ | ✅ `street_stim`／`gutter_blade` craft；`combat_scrap` 等 disassemble；`kabuki_bazaar`／`docks_gray` 庫存 |
| ~~D.5~~ | ~~格點互動物與 NETRUN~~ | ✅ 7 個格點互動物；8 區 `*_grid_node`；`tests/test_content_depth.py` |
| ~~D.6~~ | ~~人口工具工作流~~ | ✅ [WORLD_TOOLS.zh.md](WORLD_TOOLS.zh.md)／[WORLD_TOOLS.md](WORLD_TOOLS.md) |

**建議順序：** D.2 → D.1 → D.3 → D.4 → D.5 → D.6。**全階段已交付（2026-06）。**

#### 內容深度第二輪（D.7–D.10）

| 階段 | 項目 | 模組／驗收 |
|------|------|------------|
| ~~D.7~~ | ~~區域格點 look 敘事~~ | ✅ `district.grid.*`；程序格點 `look` 附加 `grid_flavor_line()` |
| ~~D.8~~ | ~~區域委託鏈~~ | ✅ 四條區域委託；`./admin.sh quests` 0 WARN |
| ~~D.9~~ | ~~區域聚光 NPC~~ | ✅ 八區具名格點 NPC；專屬 `talk.*` |
| ~~D.10~~ | ~~區域環境 tick 文案~~ | ✅ 八區 `world.ambient.*`；`tests/test_content_depth.py` |

**建議順序：** D.9 → D.8 → D.7 → D.10。**全階段已交付（2026-06）。**

### 生活指令（姿態、休息與環境）

**目標：** `sit`、`stand`、`rest`、`sleep`、`wake` 等會改變**身體狀態**（姿態、疲勞、HP／RAM 恢復），並受**房間、天氣、時段、互動物**影響——不是純敘事 emote。

**既有掛鉤：** `world/vitals.py` tick 回血；`world/trauma.py` `player_status`；`world/modifiers.py` 時段／天氣；`data/interactables.yaml`；`home`／`rent`；房間 `tags`。

| 階段 | 項目 | 模組／驗收 |
|------|------|------------|
| ~~L.1~~ | ~~姿態與疲勞模型~~ | ✅ `Player.posture`；`fatigue` 0–100；`world/life.py`；`persistence/save.py` |
| ~~L.2~~ | ~~核心生活指令~~ | ✅ `commands/life.py`：`sit`、`stand`、`lie`、`rest`、`sleep`、`wake`；戰鬥／NETRUN／追擊禁止；locale `life.*` 中英 |
| ~~L.3~~ | ~~環境休息規則~~ | ✅ `data/life.yaml`；房間 `tags`＋區域 `safety` 限制 `sleep`；時段／天氣倍率於 `world/modifiers.py`＋`world/life.py` |
| ~~L.4~~ | ~~互動物休息錨點~~ | ✅ `canteen_bench`、`flat_bunk`、`clinic_bed`、`lounge_booth`；`world/interactables.py` |
| ~~L.5~~ | ~~生命徵象與狀態整合~~ | ✅ `world/vitals.py` HP／RAM 回復；休息 tick 降疲勞、活動累積疲勞；流血／毒素禁止睡眠；高疲勞減慢回血；低 `humanity` 懲罰 |
| ~~L.6~~ | ~~風險與社交存在感~~ | ✅ `look`／`scan` 顯示姿態；睡眠打斷 tick；`go`／`say`／`talk`／戰鬥喚醒 |
| ~~L.7~~ | ~~Client 與 PDA~~ | ✅ meta `posture`／`fatigue`；PDA 列；`%posture` prompt token |
| ~~L.8~~ | ~~測試、help、教程~~ | ✅ `tests/test_life_commands.py`；help 分類 **生活與生命徵象**；餐廳長椅＋教官示範 |

**建議順序：** L.1 → L.2 → L.3 → L.4 → L.5 → L.6 → L.7 → L.8。**全階段已交付（2026-06）。**

### Client 主 log 可讀性（頻道辨識）

**目標：** 主畫面 `#log`／`#scrollback_wrap` 可快速掃讀——戰鬥、探索、社交、成長、系統訊息應**一眼可辨**，不必逐字閱讀。

**現況（2026-06）：** `client/animated_log.py`＋`client/output_prefix.py` 僅分 `motd`／`sys`／`err`／`text`／`echo`；`client/env_format.py` 在 `text` 內為 look／scan 實體上色；戰鬥 CD 倒數會改寫行；`/clear` 可清緩衝。多數遊戲輸出仍共用暗淡 `›` 前綴。

| 階段 | 項目 | 模組／驗收 |
|------|------|------------|
| ~~CL.1~~ | ~~Log 種類分類~~ | ✅ `client/log_classifier.py`；自動辨識 combat／quest／social／progression／ambient／env；`app._append_log` |
| ~~CL.2~~ | ~~各類視覺識別~~ | ✅ `client/log_styles.py`；`themes.py` `LogPalette`；`/theme` 重繪 log |
| ~~CL.3~~ | ~~戰鬥頻道~~ | ✅ 戰鬥色盤＋CD 歸 `combat`；回合間 `───` 分隔；保留 `cd_display.py` |
| ~~CL.4~~ | ~~環境區塊~~ | ✅ `env_format.py` 描述／風味層級；新 look 前 `───`；scan／實體上色 |
| ~~CL.5~~ | ~~社交與存在感~~ | ✅ `say`／`talk`／presence 中英標記 → `social` |
| ~~CL.6~~ | ~~成長與委託 feed~~ | ✅ XP／升級／聲望／熟練度＋`◈` 委託行 → `progression`／`quest` |
| ~~CL.7~~ | ~~環境 tick 與世界回饋~~ | ✅ `ambient` 淡化斜體 |
| ~~CL.8~~ | ~~測試與文件~~ | ✅ `tests/test_log_classifier.py`；`CLIENT_UI_DEBUG.md`；`docs/player/CLIENT.md` 圖例；client UI 測試修復 |
| ~~CL.9~~ | ~~精簡顯示模式~~ | ✅ `/log compact on|off`；統一 `›` 前綴；無 `───` 分隔；`settings.json` |
| ~~CL.10~~ | ~~頻道開關~~ | ✅ `/log hide`／`show`／`show all`；渲染時過濾 ambient／social／combat 等 |
| ~~CL.11~~ | ~~匯出與測試~~ | ✅ `/log export [path]`；`plain_lines()`；`tests/test_log_settings.py` |

**建議順序：** CL.1 → CL.2 → CL.3＋CL.4 → CL.5＋CL.6 → CL.7 → CL.8 → CL.9 → CL.10 → CL.11。**全階段已交付（2026-06）。**

### 安全性（OWASP ASVS L1）

**目標：** 依 [OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/) Level 1 強化認證與存檔 I/O。完整對照表：[`SECURITY.md`](SECURITY.md)／[`SECURITY.zh.md`](SECURITY.zh.md)。

| 階段 | 項目 | 模組／驗收 |
|------|------|------------|
| ~~ASVS.1~~ | ~~密碼雜湊~~ | ✅ PBKDF2-HMAC-SHA256 60 萬次迭代；舊版 SHA-256 驗證＋登入升級；`persistence/passwords.py` |
| ~~ASVS.2~~ | ~~統一登入錯誤~~ | ✅ 錯誤名稱／密碼皆回 `auth.invalid_credentials`；`commands/auth_helpers.py` |
| ~~ASVS.3~~ | ~~存檔路徑驗證~~ | ✅ 拒絕 `..`、`/`、`\`、控制字元；`shared/security.py`、`persistence/save.py` |
| ~~ASVS.4~~ | ~~輸入邊界~~ | ✅ 名稱／密碼長度；`maxsplit=1` 支援含空格密碼；單行 4 KiB 上限 |
| ~~ASVS.5~~ | ~~認證速率限制~~ | ✅ 每連線 60 秒內 5 次失敗→封鎖 5 分鐘；`server/rate_limit.py` |
| ~~ASVS.6~~ | ~~閒置／連線上限~~ | ✅ `server/connection_limits.py`；每 IP 連線上限＋訪客／已登入閒置斷線；`tests/test_security_auth.py` |
| ASVS.7 | 存檔檔案權限 | ✅ 寫入 `chmod 0o600`（部分——目錄強化待做） |
| ASVS.8 | 傳輸加密 | TLS 包裝或 VPN 部署文件 |
| ASVS.9 | 重連不重送密碼 | Token 恢復工作階段 |
| ASVS.10 | `changepass` 指令 | 已登入變更密碼 |
| ASVS.11 | 帳號鎖定 | 多次失敗後持久鎖定 |
| ASVS.12 | 安全稽核日誌 | 結構化認證失敗／管理日誌 |
| ASVS.13 | 客戶端憑證衛生 | 選用 PIN 解鎖；不儲存明文密碼 |
| ASVS.14 | 安全迴歸測試 | 速率限制整合與協定邊界；`tests/test_security_auth.py` |

**建議順序：** ASVS.1–6（已交付）→ ASVS.10 → ASVS.9 → ASVS.11 → ASVS.12 → ASVS.13 → ASVS.8 → ASVS.14。

### 新手教學區（入門深度）

**目標：** 訓練場以 NPC、地面戰利品、互動物與多階段輪值委託，教會移動、裝備、戰鬥、NETRUN、義體、生活指令與 gigs，再進入霓虹廣場。

**基線（2026-06）：** **10 房**、**13 NPC**、**8 互動物**（第三輪擴充）、`tutorial_rotation` 委託；`tests/test_tutorial_zone.py`。

| 階段 | 項目 | 模組／驗收 |
|------|------|------------|
| ~~T.1~~ | ~~前兩輪擴充~~ | ✅ 簡報室／餐廳／靶場／障礙道／模擬診所；10 NPC；4 互動物；`tutorial_supply` |
| ~~T.2~~ | ~~畢業檢定室~~ | ✅ `tutorial_debrief`；`grad_warden`；簡報室東向 |
| ~~T.3~~ | ~~裝備與戰鬥 NPC~~ | ✅ `armor_tech`、`combat_referee`；talk en/zh |
| ~~T.4~~ | ~~情境互動物~~ | ✅ 武器架、全息鏡、戰術全息、檢查閘、射擊標線、神經座、急救吊臂、結業台 |
| ~~T.5~~ | ~~訓練物品~~ | ✅ `field_bandage`、`training_tech_pistol`、`tutorial_badge` |
| ~~T.6~~ | ~~輪值委託~~ | ✅ `tutorial_rotation`；`gigs accept`；`grad_warden` 交件 |
| ~~T.7~~ | ~~測試與玩家指南~~ | ✅ `tests/test_tutorial_zone.py` 13 案例；`docs/player/TUTORIAL.md` |

**建議順序：** T.1 → T.2 → T.3 → T.4 → T.5 → T.6 → T.7。**全階段已交付（2026-06）。**

---

建議路線：**0 → A → D.2/D.7（可玩性）→ B → C → D 其餘 → E**；若新 MUD 偏社交探索，可先做 B 再做 C。

世界觀與區域、派系設定見 [WORLD.md](WORLD.md)。