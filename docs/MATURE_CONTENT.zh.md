# 限制級內容撰寫指南（18+）

> **English（canonical）：** [MATURE_CONTENT.md](MATURE_CONTENT.md)

**cyber_mud** 的限制級／NSFW 相關內容皆為**自願啟用**，預設玩家分級為 `teen`。

## 目錄

- [玩家啟用方式](#玩家啟用方式)
- [內容包（private submodule，M.18）](#內容包private-submodulem18)
  - [內容包文件（`cyber_mud_mature`）](#內容包文件)
- [世界資料](#世界資料)
- [浪漫機制骨架](#浪漫機制骨架)
- [成熟氛圍掛鉤（look／scan／interact）](#成熟氛圍掛鉤lookscaninteract)
- [成熟社交與戰鬥（M.13–M.17）](#成熟社交與戰鬥m13m17)
- [雙聲線、persona、scene 與 whisper（M.19–M.26）](#雙聲線personascene-與-whisperm19m26)
- [規劃 spotlight NPC（BB）](#規劃-spotlight-npcbb)
  - [雙聲線引擎（M.20）](#雙聲線引擎m20)
  - [人設 persona（M.21，SFW）](#人設-personam21sfw)
  - [scene 與 whisper（M.22）](#scene-與-whisperm22)
  - [Client Rich 排版（M.23）](#client-rich-排版m23)
- [驗證](#驗證)
- [Help 與 client](#help-與-client)

## 玩家啟用方式

| 方式 | 說明 |
|------|------|
| 註冊 | `register <名稱> <密碼> mature`，或 client 註冊模式勾選 18+ |
| 設定 | `settings mature on`／`settings mature off` |
| 存檔欄位 | `Player.content_rating` — `teen` 或 `mature` |

`teen` 玩家無法進入 `tags: [mature]` 房間、使用 `flirt`／`spend_time`、接限制級委託或體驗限制級腦舞。

## 內容包（private submodule，M.18）

限制級 YAML 位於 **`data/mature/`**，預定為 **private** git submodule（`cyber_mud_mature`）。無 submodule 權限的公開 clone 僅能 teen 模式。

| 檔案 | 用途 |
|------|------|
| `data/mature/locale/mature_en.yaml` | 英文血腥、創傷、浪漫、成人對話 |
| `data/mature/locale/mature_zh.yaml` | 繁中鏡像（鍵名須同步） |
| `data/mature/quests_mature.yaml` | 限制級委託 |
| `data/mature/braindances_mature.yaml` | 限制級腦舞 |
| `data/mature/romance.yaml` | 浪漫機制骨架 |

```bash
git submodule update --init data/mature
```

### 內容包文件（`cyber_mud_mature`）

英文 `*.md` 為 canonical；繁中鏡像為 `*.zh.md`（與 **cyber_mud** 相同政策）。

| 英文 | 繁中 |
|------|------|
| [README.md](https://github.com/0xd3adcafe/cyber_mud_mature/blob/master/README.md) | [README.zh.md](https://github.com/0xd3adcafe/cyber_mud_mature/blob/master/README.zh.md) |
| [CLAUDE.md](https://github.com/0xd3adcafe/cyber_mud_mature/blob/master/CLAUDE.md) | [CLAUDE.zh.md](https://github.com/0xd3adcafe/cyber_mud_mature/blob/master/CLAUDE.zh.md) |
| [CONTRIBUTING.md](https://github.com/0xd3adcafe/cyber_mud_mature/blob/master/CONTRIBUTING.md) | [CONTRIBUTING.zh.md](https://github.com/0xd3adcafe/cyber_mud_mature/blob/master/CONTRIBUTING.zh.md) |
| [LOCALIZATION.md](https://github.com/0xd3adcafe/cyber_mud_mature/blob/master/LOCALIZATION.md) | [LOCALIZATION.zh.md](https://github.com/0xd3adcafe/cyber_mud_mature/blob/master/LOCALIZATION.zh.md) |

**維護者：** 於上述 private 內容包編輯 YAML；推送後於 **cyber_mud** bump `data/mature` submodule。拆分／清 history（主 repo）：`scripts/mature-submodule-split.sh`、`scripts/mature-history-purge.sh`。

程式使用 `shared.mature_i18n.tm(locale, "combat.crit_1")`，會自動加上 `mature.` 前綴。

## 世界資料

| 標籤／欄位 | 用途 |
|------------|------|
| 房間 `tags: [mature]` | `teen` 無法 `go` 進入 |
| NPC `tags: [mature]` | `teen` 無法 `talk`；已啟用者讀 `mature.talk.<talk_key>` |
| 委託 `rating: mature` | 來自 `data/mature/quests_mature.yaml`；`teen` 的 `gigs` 不顯示 |
| 腦舞 `rating: mature` | 來自 `data/mature/braindances_mature.yaml` |

## 浪漫機制骨架

`data/mature/romance.yaml` 定義 NPC 的 `flirt`／`spend_time` 好感階段；文案在 mature locale 的 `mature.romance.*`。

多階段台詞使用 `_2`、`_3` 後綴（如 `kabuki_flirt_2`）。`world/mature_flavor.romance_line()` 依好感階段選最高可用鍵，否則回退基底鍵。

## 成熟氛圍掛鉤（look／scan／interact）

| 掛鉤 | 模組 | 語系鍵 |
|------|------|--------|
| `look`／`scan` 房間氛圍 | `world/mature_flavor.mature_room_flavor()` | `mature.room.<room_id>`（`kabuki_lounge`、`kabuki_vip`、`bd_den`） |
| `look <npc>` 細節 | `world/mature_flavor.mature_npc_detail()` | `mature.npc.<npc_id>` |
| 互動訊息覆寫 | `world/interactables.perform_interact()` | `mature.interact.<interactable_id>` |

僅 `content_rating=mature` 且在成熟標記房間／NPC 時顯示。

## 成熟社交與戰鬥（M.13–M.17）

| 功能 | 指令 | 模組／語系 |
|------|------|-----------|
| 房間 `say` 氛圍 | 成熟房間 `say <訊息>` | `commands/say.py`；`mature.social.say_ok/say_broadcast.<room>` |
| 進出氛圍 | 成熟房間 `go` | `server/game.py`；`mature.social.presence_enter/leave.<room>` |
| 浪漫送禮 | `give <物品> <NPC>`（浪漫檔） | `world/mature_give.py`；`mature.give.<npc>.<item>` |
| 血腥廣播 | 戰鬥勝敗（同房觀察者） | `broadcast_mature_key`；`mature.combat.victory/defeat_broadcast_*` |
| 嘲諷 | `taunt <npc>`（戰鬥中、18+） | `commands/taunt.py`；`mature.combat.taunt_*` |
| 終結 | `finish`（敵人 ≤30% HP、18+） | `combat/finish.py`；`mature.combat.finish_*` |

同房廣播依觀察者分級：mature 看成熟文案，teen 看預設語系。

## 雙聲線、persona、scene 與 whisper（M.19–M.26）

已交付（2026-06）：**雙聲線**、SFW **persona**、成熟 **scene**／**whisper**、Client Rich 排版。機制在主 repo；文案在 **`cyber_mud_mature`**。見 [PHASES.zh.md](PHASES.zh.md) **成熟／NSFW 內容**。

### 雙聲線引擎（M.20）

成熟敘事在執行期擇一聲線（非 LLM 生成）：

| 聲線 | 程式鍵 | 風格 |
|------|--------|------|
| **noir** | `noir` | 預設——直球賽博龐克；減少重複色情措辭 |
| **lewd** | `lewd` | 露骨 Slutbunny 風 RP（鍵名 `lewd`，非 `slutbunny`） |

`world/mature_voice.py` 提供 `resolve_mature_voice(player, state, room) → "noir" | "lewd"`。觸發為 **OR**（任一符合可切 `lewd`）：

- 成熟標記房間（`bd_den`、`kabuki_vip` 等）
- 進行中的成熟腦舞
- 玩家狀態：`overheat`、`bleed` 或 `humanity ≤ 25`
- 特定消耗品（內容包定義 item ID）
- NETRUN 追蹤值過高
- `data/mature/romance.yaml` 內 NPC 的 `voice_override`／`voice_triggers`

語系鍵：`mature.noir.*`、`mature.lewd.*`（`mature_en.yaml`／`mature_zh.yaml` 同步）。語言跟 **`player.locale`**。英文 **lewd** 對齊 [Slutbunny Lewd RP Preset](https://chub.ai/presets/bleachbunny/slutbunny-lewd-roleplay-preset-15458f06c7fd)：直白解剖用語、不用委婉、擬聲 SFX、禁用陳腔（M.26 驗證）。

**M.19** 於內容包新增 `docs/STYLE.md`／`STYLE.zh.md`——聲線規則、禁用詞、`{persona}`／`{player}` 模板慣例。

### 人設 persona（M.21，SFW）

**所有玩家**（`teen`／`mature`）可用；文案 SFW，存於存檔。

| 指令 | 說明 |
|------|------|
| `persona` | 顯示目前人設 |
| `persona set <文字>` | 設定公開描述（≤200 字） |
| `persona clear` | 清除自訂文字 |

| 欄位 | 說明 |
|------|------|
| `Player.persona` | `str`，寫入存檔 JSON |
| `look <玩家>` | 向他人顯示**完整** persona（公開） |
| `look me` | 保留 HP／姿態／數值；persona 另列 |
| NPC 模板 `{persona}` | 成熟對話用的**外觀一行摘要**——有自訂則用之，否則由裝備＋姿態自動摘要 |

`teen` 可設 persona，仍無法進 `tags: [mature]` 房間。`lewd` 聲線僅在**渲染時**改寫 persona 敘事，**不**另存 lewd 人設欄位。

### scene 與 whisper（M.22）

| 指令 | 分級 | 閘門 | 備註 |
|------|------|------|------|
| `scene`／`scene status` | `mature` | 僅浪漫**階段**（無時間冷卻） | `romance.yaml`＋語系腳本 |
| `whisper <目標> <訊息>` | 對成熟目標需 `mature` | 同房 | 玩家或 NPC；**不**推進浪漫階段 |

浪漫階段僅靠既有 `flirt`／`spend_time` 推進（已確認）。對 NPC `whisper` 為私密氛圍，非好感進度。

`data/mature/romance.yaml` 擴充 `scene_min_stage`、`voice_default`、`voice_triggers`、階段 4–5 台詞、persona／權力模板。首批 NPC：`kabuki_host`、`bd_den_clerk`、VIP 舞者。

### Client Rich 排版（M.23）

`client/mature_format.py` 為成熟 log 套用 Rich：

- `*動作*`——斜體強調
- `"對白"`——引號對話
- `>環境`——旁白／環境塊
- 擬聲／SFX——獨立色盤

新 log channel 與可選 `@meta mature_voice` 晶片（`noir`／`lewd`）於狀態列。

**M.24** 將消耗品、腦舞、賽博精神病觸發接入 `resolve_mature_voice`。**M.25** 於內容包交付雙聲線 NPC 文案。**M.26** 擴充 `mature_validate`：禁用詞與 `noir`／`lewd` 雙語鍵同步。

## 規劃 spotlight NPC（BB）

Backlog：[PHASES.zh.md](PHASES.zh.md) **Bleachbunny 風 spotlight NPC（BB）**。借 [Bleachbunny](https://bleachbunny.net/) 原型，不複製卡內劇情。

| 已定規則 | 說明 |
|----------|------|
| 浪漫階段 | 僅 `flirt`／`spend_time` 推階段；`whisper` 不推 |
| Lewd 密度 | 新成熟浪漫 NPC 約 **50%** 預設或覆寫 `lewd` 聲線 |
| 塔羅抽牌 | **每遊戲時段**一次；teen SFW hint；mature noir／lewd 抽牌文案 |
| `watson_flatmate_rin` | `scene` 須已租／`home` 於 `watson_flat` |

實作順序：**BB.Arcana＋BB.2 Trauma** → BB.3 偶像 → BB.1 Kabuki → BB.4 Tyrell → BB.5 合租 → BB.6 Wintr → BB.7 Little China → BB.8 深化舊三角。

## 驗證

```bash
./admin.sh validate
```

`world/mature_validate.py` 檢查 mature 語系鍵、浪漫 NPC、成熟房間出口、委託／腦舞分級。

## Help 與 client

- 未啟用 18+ 時，`help` 不顯示「18+ 內容」分類。
- Client 註冊模式才顯示 18+ 勾選框。
- `content_rating=mature` 時，Focus 區塊戰鬥使用血色樣式。
