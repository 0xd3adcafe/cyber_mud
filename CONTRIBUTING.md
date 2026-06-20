# Contributing

> **中文：** 協作慣例亦見 [CLAUDE.zh.md](CLAUDE.zh.md)（Agent 行為準則）。

Thank you for contributing to **cyber_mud** — human or AI-assisted.

## Licenses

By contributing, you agree that:

| What you contribute | License |
|---------------------|---------|
| **Code** (Python, shell, tests, config) | [Apache 2.0](LICENSE) |
| **World copy** (`data/`, locale narrative, lore docs) | [CC BY 4.0](LICENSE-CONTENT.md) |

See [README.md](README.md) § License for the split.

## AI-assisted development

**Agentic engineering is welcome.** This project is designed for collaboration with Claude, Cursor, Grok, and similar tools.

When opening a PR or committing:

1. **You** (the human submitter) confirm you have the right to contribute the change and accept the licenses above.
2. **Review agent output** — you are responsible for the diff, not the model.
3. Follow **[CLAUDE.md](CLAUDE.md)** § Project rules — especially **English default locale**.
4. Prefer **surgical changes**; do not merge unrelated refactors.

## Before you commit

```bash
./admin.sh validate    # world data + pytest
```

1. Update **[docs/PHASES.md](docs/PHASES.md)** backlog (completed or pending).
2. Sync **[CLAUDE.md](CLAUDE.md)** backlog summary if it is a major item.
3. Maintain **bilingual** game strings (`data/locale/en.yaml` + `zh.yaml`) when adding player-facing text.
4. Maintain **English + Chinese docs** (`*.md` + `*.zh.md`) when changing project documentation.

## Commit messages

```
<type>: English summary / 可選中文簡述
```

Examples:

```
feat: add shop restock tick / 商店補貨 tick
fix: sidebar reopen after F6 / 修正 F6 後側欄重開
docs: clarify CC BY scope for data/ / 釐清 data CC BY 範圍
```

One **major item** per commit (see [CLAUDE.md](CLAUDE.md) § Version control).

## Pull requests

- Describe what changed and how you verified it.
- Note if an AI agent generated all or part of the patch.
- Link related backlog / issue if any.

## Questions

Open a GitHub issue or discuss in your fork. For architecture and phases, start with [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) and [docs/PHASES.md](docs/PHASES.md).