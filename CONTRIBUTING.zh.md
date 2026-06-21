# 協作指南

> **English（GitHub 預設）：** [CONTRIBUTING.md](CONTRIBUTING.md)

感謝參與 **cyber_mud** 開發——無論是人類或 AI 輔助。

## 授權

| 貢獻內容 | 授權 |
|----------|------|
| **程式**（Python、shell、測試、設定） | [Apache 2.0](LICENSE) |
| **世界文案**（`data/`、locale 敘事、世界觀文件） | [CC BY 4.0](LICENSE-CONTENT.md) |

詳見 [README.zh.md](README.zh.md) 授權章節。

## AI 輔助開發

歡迎使用 Claude、Cursor、Grok 等工具協作。提交 PR 或 commit 前：

1. **你**（提交者）確認有權貢獻並接受上述授權。
2. **審閱 agent 產出**——你對 diff 負責，而非模型。
3. 遵守 **[CLAUDE.zh.md](CLAUDE.zh.md)** § 專案規則——尤其 **英文預設語系**。
4. 偏好**精準小改**，不要混入無關重構。

## 提交前

```bash
./admin.sh validate    # 世界資料 + pytest
```

1. 更新 **[docs/PHASES.zh.md](docs/PHASES.zh.md)** backlog。
2. 重大項目同步 **[CLAUDE.zh.md](CLAUDE.zh.md)** backlog 摘要。
3. 玩家可見文案維持 **`data/locale/en.yaml` + `zh.yaml`**。
4. 專案文件維持 **英文 `*.md` + 中文 `*.zh.md`**。
5. **18+ 成熟文案**放在 private **`cyber_mud_mature`** 內容包（`data/mature/`）——M.18 拆分後勿提交至公開 repo——見 [docs/MATURE_CONTENT.zh.md](docs/MATURE_CONTENT.zh.md)。

## Commit 訊息

```
<type>: English summary / 可選中文簡述
```

一個 **major item** 一個 commit（見 [CLAUDE.zh.md](CLAUDE.zh.md) § 版本控制）。

## 世界編寫工具

程序格點、人口覆蓋層、任務腳手架：**[docs/WORLD_TOOLS.zh.md](docs/WORLD_TOOLS.zh.md)**（[English](docs/WORLD_TOOLS.md)）。

調整原型或格點後快速重產：

```bash
python -m tools.expand_world_population
./admin.sh validate
```

## Pull request

- 說明變更與驗證方式。
- 註明是否由 AI 產生部分 patch。
- 連結相關 backlog／issue。

## 問題

可開 GitHub issue。架構與階段規劃請先讀 [docs/ARCHITECTURE.zh.md](docs/ARCHITECTURE.zh.md) 與 [docs/PHASES.zh.md](docs/PHASES.zh.md)。