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

## 文案檔（勿混入預設 locale）

| 檔案 | 用途 |
|------|------|
| `data/locale/mature_en.yaml` | 英文血腥、創傷、浪漫、成人對話 |
| `data/locale/mature_zh.yaml` | 繁中鏡像（鍵名須同步） |

程式使用 `shared.mature_i18n.tm(locale, "combat.crit_1")`，會自動加上 `mature.` 前綴。

## 世界資料

| 標籤／欄位 | 用途 |
|------------|------|
| 房間 `tags: [mature]` | `teen` 無法 `go` 進入 |
| NPC `tags: [mature]` | `teen` 無法 `talk`；已啟用者讀 `mature.talk.<talk_key>` |
| 委託 `rating: mature` | 來自 `data/quests_mature.yaml`；`teen` 的 `gigs` 不顯示 |
| 腦舞 `rating: mature` | 來自 `data/braindances_mature.yaml` |

## 浪漫機制骨架

`data/romance.yaml` 定義 NPC 的 `flirt`／`spend_time` 好感階段；文案在 mature locale 的 `mature.romance.*`。

## 驗證

```bash
./admin.sh validate
```

`world/mature_validate.py` 檢查 mature 語系鍵、浪漫 NPC、成熟房間出口、委託／腦舞分級。

## Help 與 client

- 未啟用 18+ 時，`help` 不顯示「18+ 內容」分類。
- Client 註冊模式才顯示 18+ 勾選框。
- `content_rating=mature` 時，Focus 區塊戰鬥使用血色樣式。