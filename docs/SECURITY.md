# Security (OWASP ASVS)

**中文：** [SECURITY.zh.md](SECURITY.zh.md)

This document tracks **OWASP Application Security Verification Standard (ASVS)** alignment for cyber_mud. The game is a hobby MUD with a built-in Textual client and a plaintext TCP protocol for debugging—not a production web app. Controls are pragmatic for that threat model.

**Scope:** Level 1 (L1) first; Level 2 items remain backlog.

## Table of contents

- [Threat model (summary)](#threat-model-summary)
- [ASVS L1 — shipped (2026-06)](#asvs-l1-shipped-2026-06)
- [ASVS backlog (not yet implemented)](#asvs-backlog-not-yet-implemented)
- [Transport encryption (ASVS.8)](#transport-encryption-asvs8)
- [Developer checklist](#developer-checklist)
- [References](#references)

## Threat model (summary)

| Asset | Risk |
|-------|------|
| Player save JSON (`data/saves/`) | Credential hash theft, save tampering |
| TCP login/register | Brute force, user enumeration, oversized input |
| Client credential store (`~/.config/cyber_mud/credentials.json`) | Local PIN-encrypted session token replay |

**Out of scope for L1:** WAF, centralized identity provider.

## ASVS L1 — shipped (2026-06)

| ID | ASVS theme | Implementation | Tests |
|----|------------|----------------|-------|
| ASVS.1 | Password storage | PBKDF2-HMAC-SHA256, 600k iterations (`persistence/passwords.py`); legacy SHA-256 verify + auto-rehash on login | `tests/test_security_auth.py` |
| ASVS.2 | Authentication errors | Login failures return unified `auth.invalid_credentials` (no user enumeration) | `tests/test_security_auth.py`, `tests/test_auth.py` |
| ASVS.3 | Save path safety | `validate_character_name` + `save_name_allowed`; reject `..`, `/`, `\`, control chars (`shared/security.py`, `persistence/save.py`) | `tests/test_security_auth.py` |
| ASVS.4 | Input validation | Name 2–24 chars; password 8–128 chars; `split(maxsplit=1)` for passwords with spaces; max line 4 KiB (`shared/protocol.py`, `server/main.py`) | `tests/test_security_auth.py` |
| ASVS.5 | Brute-force resistance | Per-connection `AuthRateLimiter`: 5 failures / 60s → 5 min block (`server/rate_limit.py`, `server/game.py`) | `tests/test_security_auth.py` |
| ASVS.6 | Idle / connection limits | `server/connection_limits.py`; `CYBER_MUD_MAX_CONNECTIONS_PER_IP` (default 3); guest 600s / auth 1800s idle | `tests/test_security_auth.py` |
| ASVS.7 | Save permissions | Save directory `chmod 0o700`; save files `chmod 0o600` (`persistence/save.py`) | `tests/test_security_auth.py` |
| ASVS.8 | Transport encryption | Optional TLS via `--tls-cert` / `--tls-key`; VPN-only deployment documented below | `server/main.py`, this doc |
| ASVS.9 | Reconnect without password replay | Server session tokens + `resume <token>`; rotated on resume; `@meta session_token` | `server/session_tokens.py`, `commands/resume.py`, `tests/test_security_auth.py` |
| ASVS.10 | `changepass` command | Authenticated password change + PBKDF2 rehash; revokes old tokens | `commands/changepass.py`, `tests/test_security_auth.py` |
| ASVS.11 | Account lockout | Save-backed lockout: 10 failures → 15 min (`persistence/account_lockout.py`) | `tests/test_security_auth.py` |
| ASVS.12 | Security audit log | JSON lines on stderr: `[audit] {...}` (`server/audit_log.py`) | `tests/test_security_auth.py` |
| ASVS.13 | Client credential hygiene | PIN-encrypted store holds session token only (no raw password); legacy password blobs still decrypt | `client/credentials.py`, `tests/test_credentials.py` |
| ASVS.14 | Regression suite | Rate-limit integration, protocol bounds, changepass/resume/lockout/audit | `tests/test_security_auth.py` |

## ASVS backlog (not yet implemented)

All L1 items above are shipped. Remaining work is **Level 2** hardening (e.g. MFA, centralized logging, formal pen-test cadence).

## Transport encryption (ASVS.8)

### Loopback / local play (default)

Plain TCP on `127.0.0.1:4000` is acceptable for solo development—the threat model treats loopback as trusted.

### Optional TLS

```bash
PYTHONPATH=. python -m server.main --host 0.0.0.0 --port 4000 \
  --tls-cert /path/to/cert.pem --tls-key /path/to/key.pem
```

Generate a dev cert with OpenSSL:

```bash
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem \
  -days 365 -nodes -subj "/CN=cyber_mud"
```

The Textual client currently connects with plain TCP; TLS is intended for **remote deployment** behind a TLS-terminated proxy or with a future client SSL option.

### VPN-only remote deployment

For LAN/WAN play without TLS on the game port:

1. Bind the server to a private interface or `0.0.0.0` **only inside** a VPN (WireGuard, Tailscale, etc.).
2. Do **not** port-forward `4000` on a public router without TLS or VPN.
3. Keep `data/saves/` on the host filesystem with `0700` directory / `0600` file permissions (enforced on write).

## Developer checklist

- New auth-facing strings → `data/locale/en.yaml` + `zh.yaml` under `auth.*`
- Password hashing only via `persistence/passwords.py`
- Name validation via `shared/security.py` before any save I/O
- Security events via `server/audit_log.log_security_event`
- Session tokens via `server/session_tokens.py` (in-memory; lost on server restart)

## References

- [OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/)
- [`docs/LOCALIZATION.md`](LOCALIZATION.md) — locale policy
- [`docs/PHASES.md`](PHASES.md) — delivery checklist