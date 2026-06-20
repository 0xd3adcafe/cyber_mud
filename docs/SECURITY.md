# Security (OWASP ASVS)

**中文：** [SECURITY.zh.md](SECURITY.zh.md)

This document tracks **OWASP Application Security Verification Standard (ASVS)** alignment for cyber_mud. The game is a hobby MUD with a built-in Textual client and a plaintext TCP protocol for debugging—not a production web app. Controls are pragmatic for that threat model.

**Scope:** Level 1 (L1) first; Level 2 items remain backlog.

## Threat model (summary)

| Asset | Risk |
|-------|------|
| Player save JSON (`data/saves/`) | Credential hash theft, save tampering |
| TCP login/register | Brute force, user enumeration, oversized input |
| Client credential store (`~/.config/cyber_mud/credentials.json`) | Local plaintext password replay (separate backlog) |

**Out of scope for L1:** TLS on loopback, WAF, centralized identity provider.

## ASVS L1 — shipped (2026-06)

| ID | ASVS theme | Implementation | Tests |
|----|------------|----------------|-------|
| ASVS.1 | Password storage | PBKDF2-HMAC-SHA256, 600k iterations (`persistence/passwords.py`); legacy SHA-256 verify + auto-rehash on login | `tests/test_security_auth.py` |
| ASVS.2 | Authentication errors | Login failures return unified `auth.invalid_credentials` (no user enumeration) | `tests/test_security_auth.py`, `tests/test_auth.py` |
| ASVS.3 | Save path safety | `validate_character_name` + `save_name_allowed`; reject `..`, `/`, `\`, control chars (`shared/security.py`, `persistence/save.py`) | `tests/test_security_auth.py` |
| ASVS.4 | Input validation | Name 2–24 chars; password 8–128 chars; `split(maxsplit=1)` for passwords with spaces; max line 4 KiB (`shared/protocol.py`, `server/main.py`) | `tests/test_security_auth.py` |
| ASVS.5 | Brute-force resistance | Per-connection `AuthRateLimiter`: 5 failures / 60s → 5 min block (`server/rate_limit.py`, `server/game.py`) | `tests/test_security_auth.py` |
| ASVS.7 (partial) | File permissions | Save files written `chmod 0o600` | `tests/test_security_auth.py` |

## ASVS backlog (not yet implemented)

| ID | Item | Notes |
|----|------|-------|
| ~~ASVS.6~~ | ~~Idle / connection limits~~ | ✅ `server/connection_limits.py`; `CYBER_MUD_MAX_CONNECTIONS_PER_IP` (default 3); guest 600s / auth 1800s idle; `tests/test_security_auth.py` |
| ASVS.8 | Transport encryption | TLS wrapper or documented VPN-only deployment |
| ASVS.9 | Reconnect without password replay | Token-based session resume instead of resending password |
| ASVS.10 | `changepass` command | Authenticated password change + rehash |
| ASVS.11 | Account lockout | Persistent lockout after repeated failures (save-backed) |
| ASVS.12 | Security audit log | Structured server log for auth failures / admin actions |
| ASVS.13 | Client credential hygiene | Optional: never store raw password; PIN-only unlock of server token |
| ASVS.14 | Regression suite | Expand `tests/test_security_auth.py` for rate-limit integration and protocol edge cases |

**Suggested order:** ASVS.6 shipped → ASVS.10 → ASVS.9 → ASVS.11 → ASVS.12 → ASVS.13 → ASVS.8 → ASVS.14.

## Developer checklist

- New auth-facing strings → `data/locale/en.yaml` + `zh.yaml` under `auth.*`
- Password hashing only via `persistence/passwords.py`
- Name validation via `shared/security.py` before any save I/O
- Record shipped items in [`PHASES.md`](PHASES.md) **Security (ASVS)** section

## References

- [OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/)
- [`docs/LOCALIZATION.md`](LOCALIZATION.md) — locale policy
- [`docs/PHASES.md`](PHASES.md) — delivery checklist