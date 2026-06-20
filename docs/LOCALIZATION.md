# Localization / 語系與雙語慣例

> **Default / 預設語系：English (`en`)**  
> All user-facing text, logs, docs, and commit messages follow **English primary + Traditional Chinese mirror**.

---

## English

### Scope

| Area | Mechanism | Default |
|------|-----------|---------|
| In-game text | `data/locale/en.yaml`, `data/locale/zh.yaml` via `t(locale, key)` | `en` |
| World content | `*_en` / `*_zh` fields in `data/*.yaml` | `en` when `player.locale == "en"` |
| Server console logs | `server.*` keys + `CYBER_MUD_SERVER_LOCALE` (default `en`) | `en` |
| Client TUI chrome | `client.*` keys; follows `player.locale` / login locale | `en` |
| Documentation | English section first; `## 中文` below | English |
| Commit messages | `<type>: EN summary` — optional ` / 中文` suffix | English |

### Switching language in-game

```
lang       # show current locale
lang en    # English
lang zh    # Traditional Chinese
```

### Tests

`tests/conftest.py` `make_player()` still defaults to `zh` so legacy assertions pass. Production and new tests should use `make_player(locale="en")` or `Player()` directly. See `tests/test_default_locale.py`.

### Adding strings

1. Add the same key to **both** `data/locale/en.yaml` and `data/locale/zh.yaml`.
2. Use `t(player.locale, "section.key", **kwargs)` on the server.
3. Use `t(locale, "client.section.key")` in the client.
4. Never hardcode user-visible Chinese or English in logic when a locale key exists.

### Commit message format

```
feat: add lang command for locale switching / 新增 lang 語系切換指令
test: default locale en in fixtures / 測試預設改為 en
docs: bilingual README and LOCALIZATION policy / 雙語 README 與語系文件
```

---

## 中文

### 範圍

| 區域 | 機制 | 預設 |
|------|------|------|
| 遊戲內文案 | `data/locale/en.yaml`、`zh.yaml`，`t(locale, key)` | `en` |
| 世界內容 | `data/*.yaml` 的 `*_en` / `*_zh` | `locale == "en"` 時英文 |
| 伺服器終端日誌 | `server.*` + 環境變數 `CYBER_MUD_SERVER_LOCALE` | `en` |
| Client TUI | `client.*`；跟隨 `player.locale` | `en` |
| 文件 | 英文在前、`## 中文` 在後 | 英文 |
| Commit | `<type>: 英文簡述` + 可選 ` / 中文` | 英文 |

### 遊戲內切換

```
lang       # 顯示目前語系
lang en    # 英文
lang zh    # 繁體中文
```

### 新增文案

1. **同時**加入 `en.yaml` 與 `zh.yaml`。
2. 伺服器用 `t(player.locale, …)`。
3. Client 用 `t(locale, "client.…")`。
4. 邏輯層避免硬編碼單語字串。

### Commit 格式

```
feat: add lang command for locale switching / 新增 lang 語系切換指令
```

主述用英文；需要時以 ` / ` 接繁中簡述。