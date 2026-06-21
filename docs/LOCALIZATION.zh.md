# 語系與雙語慣例

> **English:** [LOCALIZATION.md](LOCALIZATION.md)

> **預設語系：English (`en`)**  
> 遊戲文案、日誌、文件與 commit 採 **英文主述 + 繁體中文對照**。

## 專案規則（強制）

**本專案預設語系為英文。** 硬性規定見 [`CLAUDE.zh.md`](../CLAUDE.zh.md) § 專案規則（強制）。

- 執行時預設：`Player.locale == "en"`、client 登入 `en`、存檔缺 `locale` 遷移為 `"en"`、`CYBER_MUD_SERVER_LOCALE=en`。
- **不得**在未經維護者明確決策與完整測試／文件更新下，將專案預設改為 `zh`。
- 新增文案：先 `en.yaml` 再 `zh.yaml`；新增文件：先英文 `*.md` 再 `*.zh.md`。
- 中文為遊戲內**選用**（`lang zh`），非出廠預設。

## 文件對照

| 英文（GitHub 預設） | 中文 |
|---------------------|------|
| [README.md](../README.md) | [README.zh.md](../README.zh.md) |
| [CLAUDE.md](../CLAUDE.md) | [CLAUDE.zh.md](../CLAUDE.zh.md) |
| [docs/WORLD.md](WORLD.md) | [docs/WORLD.zh.md](WORLD.zh.md) |
| [docs/ARCHITECTURE.md](ARCHITECTURE.md) | [docs/ARCHITECTURE.zh.md](ARCHITECTURE.zh.md) |
| [docs/IMPLEMENTATION.md](IMPLEMENTATION.md) | [docs/IMPLEMENTATION.zh.md](IMPLEMENTATION.zh.md) |
| [docs/BOOTSTRAP.md](BOOTSTRAP.md) | [docs/BOOTSTRAP.zh.md](BOOTSTRAP.zh.md) |
| [docs/PHASES.md](PHASES.md) | [docs/PHASES.zh.md](PHASES.zh.md) |
| [docs/CLIENT_UI_DEBUG.md](CLIENT_UI_DEBUG.md) | [docs/CLIENT_UI_DEBUG.zh.md](CLIENT_UI_DEBUG.zh.md) |
| [docs/LOCALIZATION.md](LOCALIZATION.md) | [docs/LOCALIZATION.zh.md](LOCALIZATION.zh.md) |
| [docs/MATURE_CONTENT.md](MATURE_CONTENT.md) | [docs/MATURE_CONTENT.zh.md](MATURE_CONTENT.zh.md) — **18+ 遊戲掛鉤（主 repo）** |
| [docs/player/*.md](player/README.md) | [docs/player/*.zh.md](player/README.zh.md) — **玩家指南** |

**限制級內容包（`cyber_mud_mature` submodule）：** 英文 `*.md` + `*.zh.md` 見 [github.com/0xd3adcafe/cyber_mud_mature](https://github.com/0xd3adcafe/cyber_mud_mature) — `README`、`CLAUDE`、`CONTRIBUTING`、`LOCALIZATION`；語系檔 `data/mature/locale/mature_en.yaml`（權威）+ `mature_zh.yaml`。

變更專案文件時，請同步維護英文與中文版本。

**ASCII 圖示：** ` ```text ` 區塊內用 `+---+`／`|` 框線且**每行等長**；框內標籤用 ASCII，中文說明放在區塊**下方**（框內混中文會在 GitHub 錯位）。

## 範圍

| 區域 | 機制 | 預設 |
|------|------|------|
| 遊戲內文案 | `data/locale/en.yaml`、`zh.yaml`，`t(locale, key)` | `en` |
| 世界內容 | `data/*.yaml` 的 `*_en` / `*_zh` | `locale == "en"` 時英文 |
| 伺服器終端日誌 | `server.*` + 環境變數 `CYBER_MUD_SERVER_LOCALE` | `en` |
| Client TUI | `client.*`；跟隨 `player.locale` | `en` |
| 文件 | 英文 `*.md` 為 GitHub 預設；中文 `*.zh.md` 對照 | 英文 |
| Commit | `<type>: 英文簡述` + 可選 ` / 中文` | 英文 |
| **授權** | 程式：[Apache 2.0](../LICENSE)；文案：[CC BY 4.0](../LICENSE-CONTENT.md) | 見 [CONTRIBUTING.md](../CONTRIBUTING.md) |

## 遊戲內切換

```
lang       # 顯示目前語系
lang en    # 英文
lang zh    # 繁體中文
```

## 測試

`tests/conftest.py` 的 `make_player()` 仍預設 `zh` 以通過舊測試。新測試與正式行為請用 `make_player(locale="en")` 或直接 `Player()`。見 `tests/test_default_locale.py`。

## 新增文案

1. **同時**加入 `en.yaml` 與 `zh.yaml`。
2. 伺服器用 `t(player.locale, …)`。
3. Client 用 `t(locale, "client.…")`。
4. 邏輯層避免硬編碼單語字串。

範例（生活指令）：`life.sit_ok`、`life.sleep_ok`、`help_cmds.sit`、`pda.life` 須**同時**寫入兩份 YAML；玩家文件同步 [COMMANDS.md](player/COMMANDS.md) 與 [COMMANDS.zh.md](player/COMMANDS.zh.md)。

## Commit 格式

```
feat: add lang command for locale switching / 新增 lang 語系切換指令
feat: add life commands sit/rest/sleep / 新增生活指令 sit/rest/sleep
docs: split EN/ZH markdown docs / 中英文文件分離
```

交付遊戲功能時，**英文與中文文件須一併更新**：`PHASES.md`＋`PHASES.zh.md`、玩家指南、`en.yaml`＋`zh.yaml`。

主述用英文；需要時以 ` / ` 接繁中簡述。