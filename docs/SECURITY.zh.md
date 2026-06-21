# 安全性（OWASP ASVS）

**English (canonical):** [SECURITY.md](SECURITY.md)

本文件追蹤 cyber_mud 與 **OWASP 應用程式安全驗證標準（ASVS）** 的對齊狀況。本專案為內建 Textual 客戶端的愛好型 MUD，並保留純文字 TCP 協定供除錯，並非正式上線的 Web 應用；控制措施依此威脅模型務實取捨。

**範圍：** 先達成 Level 1（L1）；Level 2 項目列於 backlog。

## 目錄

- [威脅模型（摘要）](#威脅模型摘要)
- [ASVS L1 — 已交付（2026-06）](#asvs-l1-已交付2026-06)
- [ASVS backlog（尚未實作）](#asvs-backlog尚未實作)
- [傳輸加密（ASVS.8）](#傳輸加密asvs8)
- [開發者檢查清單](#開發者檢查清單)
- [參考](#參考)

## 威脅模型（摘要）

| 資產 | 風險 |
|------|------|
| 玩家存檔 JSON（`data/saves/`） | 密碼雜湊外洩、存檔竄改 |
| TCP 登入／註冊 | 暴力破解、帳號列舉、過大輸入 |
| 客戶端憑證儲存（`~/.config/cyber_mud/credentials.json`） | 本機 PIN 加密的工作階段權杖重放 |

**L1 範圍外：** WAF、集中式身分提供者。

## ASVS L1 — 已交付（2026-06）

| ID | ASVS 主題 | 實作 | 測試 |
|----|-----------|------|------|
| ASVS.1 | 密碼儲存 | PBKDF2-HMAC-SHA256、60 萬次迭代（`persistence/passwords.py`）；舊版 SHA-256 驗證 + 登入時自動升級 | `tests/test_security_auth.py` |
| ASVS.2 | 認證錯誤訊息 | 登入失敗統一回傳 `auth.invalid_credentials`（避免帳號列舉） | `tests/test_security_auth.py`、`tests/test_auth.py` |
| ASVS.3 | 存檔路徑安全 | `validate_character_name` + `save_name_allowed`；拒絕 `..`、`/`、`\`、控制字元 | `tests/test_security_auth.py` |
| ASVS.4 | 輸入驗證 | 名稱 2–24 字元；密碼 8–128 字元；`split(maxsplit=1)` 支援含空格的密碼；單行上限 4 KiB | `tests/test_security_auth.py` |
| ASVS.5 | 暴力破解防護 | 每連線 `AuthRateLimiter`：60 秒內 5 次失敗 → 封鎖 5 分鐘 | `tests/test_security_auth.py` |
| ASVS.6 | 閒置／連線上限 | `server/connection_limits.py`；每 IP 上限（預設 3）；訪客 600s／已登入 1800s 閒置斷線 | `tests/test_security_auth.py` |
| ASVS.7 | 存檔權限 | 存檔目錄 `chmod 0o700`；存檔檔案 `chmod 0o600`（`persistence/save.py`） | `tests/test_security_auth.py` |
| ASVS.8 | 傳輸加密 | 選用 TLS（`--tls-cert`／`--tls-key`）；VPN 部署文件見下文 | `server/main.py`、本文件 |
| ASVS.9 | 重連不重送密碼 | 伺服器工作階段權杖 + `resume <token>`；恢復時輪換；`@meta session_token` | `server/session_tokens.py`、`commands/resume.py` |
| ASVS.10 | `changepass` 指令 | 已登入變更密碼並 PBKDF2 重新雜湊；撤銷舊權杖 | `commands/changepass.py` |
| ASVS.11 | 帳號鎖定 | 存檔層鎖定：10 次失敗 → 15 分鐘（`persistence/account_lockout.py`） | `tests/test_security_auth.py` |
| ASVS.12 | 安全稽核日誌 | stderr JSON 行：`[audit] {...}`（`server/audit_log.py`） | `tests/test_security_auth.py` |
| ASVS.13 | 客戶端憑證衛生 | PIN 加密儲存僅保留工作階段權杖（不存明文密碼）；舊版密碼 blob 仍可解密 | `client/credentials.py`、`tests/test_credentials.py` |
| ASVS.14 | 迴歸測試擴充 | 速率限制整合、協定邊界、changepass／resume／鎖定／稽核 | `tests/test_security_auth.py` |

## ASVS backlog（尚未實作）

上述 L1 項目均已交付。後續為 **Level 2** 強化（例如 MFA、集中式日誌、正式滲透測試節奏）。

## 傳輸加密（ASVS.8）

### 本機／迴圈（預設）

開發時使用 `127.0.0.1:4000` 純文字 TCP 可接受——威脅模型視迴圈為可信。

### 選用 TLS

```bash
PYTHONPATH=. python -m server.main --host 0.0.0.0 --port 4000 \
  --tls-cert /path/to/cert.pem --tls-key /path/to/key.pem
```

以 OpenSSL 產生開發用憑證：

```bash
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem \
  -days 365 -nodes -subj "/CN=cyber_mud"
```

Textual 客戶端目前以純 TCP 連線；TLS 適用於**遠端部署**（TLS 終止代理或未來客戶端 SSL 選項）。

### 僅 VPN 遠端部署

若遊戲埠未啟用 TLS：

1. 僅在 VPN（WireGuard、Tailscale 等）內綁定私有介面或 `0.0.0.0`。
2. **勿**在公網路由器上轉發 `4000`，除非有 TLS 或 VPN。
3. 主機上 `data/saves/` 維持目錄 `0700`、檔案 `0600`（寫入時強制）。

## 開發者檢查清單

- 新的認證相關字串 → `data/locale/en.yaml` 與 `zh.yaml` 的 `auth.*`
- 密碼雜湊僅透過 `persistence/passwords.py`
- 任何存檔 I/O 前先以 `shared/security.py` 驗證名稱
- 安全事件透過 `server/audit_log.log_security_event`
- 工作階段權杖透過 `server/session_tokens.py`（記憶體內；伺服器重啟後失效）

## 參考

- [OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/)
- [`docs/LOCALIZATION.zh.md`](LOCALIZATION.zh.md)
- [`docs/PHASES.zh.md`](PHASES.zh.md)