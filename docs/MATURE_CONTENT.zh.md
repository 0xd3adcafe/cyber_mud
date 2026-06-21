# 限制級內容撰寫指南（18+）

> **English（canonical）：** [MATURE_CONTENT.md](MATURE_CONTENT.md)

**cyber_mud** 的限制級／NSFW 相關內容皆為**自願啟用**，預設玩家分級為 `teen`。

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

維護者：`scripts/mature-submodule-split.sh`、`scripts/mature-history-purge.sh`。

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

## 驗證

```bash
./admin.sh validate
```

`world/mature_validate.py` 檢查 mature 語系鍵、浪漫 NPC、成熟房間出口、委託／腦舞分級。

## Help 與 client

- 未啟用 18+ 時，`help` 不顯示「18+ 內容」分類。
- Client 註冊模式才顯示 18+ 勾選框。
- `content_rating=mature` 時，Focus 區塊戰鬥使用血色樣式。