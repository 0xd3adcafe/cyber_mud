# 安全性（OWASP ASVS）

**English (canonical):** [SECURITY.md](SECURITY.md)

本文件追蹤 cyber_mud 與 **OWASP 應用程式安全驗證標準（ASVS）** 的對齊狀況。本專案為內建 Textual 客戶端的愛好型 MUD，並保留純文字 TCP 協定供除錯，並非正式上線的 Web 應用；控制措施依此威脅模型務實取捨。

**範圍：** 先達成 Level 1（L1）；Level 2 項目列於 backlog。

## 威脅模型（摘要）

| 資產 | 風險 |
|------|------|
| 玩家存檔 JSON（`data/saves/`） | 密碼雜湊外洩、存檔竄改 |
| TCP 登入／註冊 | 暴力破解、帳號列舉、過大輸入 |
| 客戶端憑證儲存（`~/.config/cyber_mud/credentials.json`） | 本機明文密碼重放（另列 backlog） |

**L1 範圍外：** 本機迴圈 TLS、WAF、集中式身分提供者。

## ASVS L1 — 已交付（2026-06）

| ID | ASVS 主題 | 實作 | 測試 |
|----|-----------|------|------|
| ASVS.1 | 密碼儲存 | PBKDF2-HMAC-SHA256、60 萬次迭代（`persistence/passwords.py`）；舊版 SHA-256 驗證 + 登入時自動升級 | `tests/test_security_auth.py` |
| ASVS.2 | 認證錯誤訊息 | 登入失敗統一回傳 `auth.invalid_credentials`（避免帳號列舉） | `tests/test_security_auth.py`、`tests/test_auth.py` |
| ASVS.3 | 存檔路徑安全 | `validate_character_name` + `save_name_allowed`；拒絕 `..`、`/`、`\`、控制字元 | `tests/test_security_auth.py` |
| ASVS.4 | 輸入驗證 | 名稱 2–24 字元；密碼 8–128 字元；`split(maxsplit=1)` 支援含空格的密碼；單行上限 4 KiB | `tests/test_security_auth.py` |
| ASVS.5 | 暴力破解防護 | 每連線 `AuthRateLimiter`：60 秒內 5 次失敗 → 封鎖 5 分鐘 | `tests/test_security_auth.py` |
| ASVS.7（部分） | 檔案權限 | 存檔寫入 `chmod 0o600` | `tests/test_security_auth.py` |

## ASVS backlog（尚未實作）

| ID | 項目 | 說明 |
|----|------|------|
| ~~ASVS.6~~ | ~~閒置／連線上限~~ | ✅ `server/connection_limits.py`；每 IP 上限（預設 3）；訪客 600s／已登入 1800s 閒置斷線；`tests/test_security_auth.py` |
| ASVS.8 | 傳輸加密 | TLS 包裝或僅 VPN 部署文件 |
| ASVS.9 | 重連不重送密碼 | 以 token 恢復工作階段 |
| ASVS.10 | `changepass` 指令 | 已登入變更密碼並重新雜湊 |
| ASVS.11 | 帳號鎖定 | 多次失敗後持久鎖定（存檔層） |
| ASVS.12 | 安全稽核日誌 | 結構化記錄認證失敗／管理操作 |
| ASVS.13 | 客戶端憑證衛生 | 選用：不儲存明文密碼；僅 PIN 解鎖伺服器 token |
| ASVS.14 | 迴歸測試擴充 | 速率限制整合與協定邊界案例 |

**建議順序：** ASVS.6 已交付 → ASVS.10 → ASVS.9 → ASVS.11 → ASVS.12 → ASVS.13 → ASVS.8 → ASVS.14。

## 開發者檢查清單

- 新的認證相關字串 → `data/locale/en.yaml` 與 `zh.yaml` 的 `auth.*`
- 密碼雜湊僅透過 `persistence/passwords.py`
- 任何存檔 I/O 前先以 `shared/security.py` 驗證名稱
- 已交付項目記錄於 [`PHASES.md`](PHASES.md) **Security (ASVS)** 區段

## 參考

- [OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/)
- [`docs/LOCALIZATION.zh.md`](LOCALIZATION.zh.md)
- [`docs/PHASES.zh.md`](PHASES.zh.md)