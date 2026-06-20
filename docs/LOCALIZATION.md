# Localization

> **中文：** [LOCALIZATION.zh.md](LOCALIZATION.zh.md)

> **Default locale: English (`en`)**  
> User-facing text, logs, docs, and commits use **English primary + Traditional Chinese mirror**.

## Scope

| Area | Mechanism | Default |
|------|-----------|---------|
| In-game text | `data/locale/en.yaml`, `data/locale/zh.yaml` via `t(locale, key)` | `en` |
| World content | `*_en` / `*_zh` fields in `data/*.yaml` | `en` when `player.locale == "en"` |
| Server console logs | `server.*` keys + `CYBER_MUD_SERVER_LOCALE` (default `en`) | `en` |
| Client TUI chrome | `client.*` keys; follows `player.locale` / login locale | `en` |
| Documentation | English `*.md` on GitHub; Chinese `*.zh.md` mirrors | English |
| Commit messages | `<type>: EN summary` — optional ` / 中文` suffix | English |

## Documentation layout

| English (GitHub default) | Chinese mirror |
|--------------------------|----------------|
| [README.md](../README.md) | [README.zh.md](../README.zh.md) |
| [CLAUDE.md](../CLAUDE.md) | [CLAUDE.zh.md](../CLAUDE.zh.md) |
| [docs/WORLD.md](WORLD.md) | [docs/WORLD.zh.md](WORLD.zh.md) |
| [docs/ARCHITECTURE.md](ARCHITECTURE.md) | [docs/ARCHITECTURE.zh.md](ARCHITECTURE.zh.md) |
| [docs/IMPLEMENTATION.md](IMPLEMENTATION.md) | [docs/IMPLEMENTATION.zh.md](IMPLEMENTATION.zh.md) |
| [docs/BOOTSTRAP.md](BOOTSTRAP.md) | [docs/BOOTSTRAP.zh.md](BOOTSTRAP.zh.md) |
| [docs/PHASES.md](PHASES.md) | [docs/PHASES.zh.md](PHASES.zh.md) |
| [docs/CLIENT_UI_DEBUG.md](CLIENT_UI_DEBUG.md) | [docs/CLIENT_UI_DEBUG.zh.md](CLIENT_UI_DEBUG.zh.md) |
| [docs/LOCALIZATION.md](LOCALIZATION.md) | [docs/LOCALIZATION.zh.md](LOCALIZATION.zh.md) |

Edit both languages when changing project docs.

## Switching language in-game

```
lang       # show current locale
lang en    # English
lang zh    # Traditional Chinese
```

## Tests

`tests/conftest.py` `make_player()` still defaults to `zh` so legacy assertions pass. Production and new tests should use `make_player(locale="en")` or `Player()` directly. See `tests/test_default_locale.py`.

## Adding strings

1. Add the same key to **both** `data/locale/en.yaml` and `data/locale/zh.yaml`.
2. Use `t(player.locale, "section.key", **kwargs)` on the server.
3. Use `t(locale, "client.section.key")` in the client.
4. Never hardcode user-visible Chinese or English in logic when a locale key exists.

## Commit message format

```
feat: add lang command for locale switching / 新增 lang 語系切換指令
test: default locale en in fixtures / 測試預設改為 en
docs: split EN/ZH markdown docs / 中英文文件分離
```