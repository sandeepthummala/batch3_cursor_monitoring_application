# Security notes (local demo)

This app is a **local demo**. Do not expose it beyond `127.0.0.1` without a full security review.

## Threats & mitigations

| Area | Mitigation |
|------|------------|
| Admin password | Stored only as Werkzeug hash in SQLite; never plaintext |
| Session | Flask signed cookie; `SESSION_COOKIE_HTTPONLY`; `SameSite=Lax` |
| Forms | Flask-WTF CSRF on mutating forms; logout via POST |
| SSH passwords | Fernet-encrypted at rest (key derived from `SECRET_KEY`); masked in UI; never logged |
| SSH keys | Path only (no private key material in DB); key files gitignored |
| Remote commands | Fixed command strings only (no user input in shell) |
| Host input | Validated charset (no whitespace / shell metacharacters) |
| Metrics JSON | Auth-required; no credentials in payloads |
| Errors | Sanitized SSH error messages (no password/key leakage) |
| Bind address | Defaults to `127.0.0.1` |

## Demo risks (accepted)

- Default admin password is documented for local use — change via `DEMO_ADMIN_PASSWORD` / re-seed if needed
- Paramiko `AutoAddPolicy` for host keys (convenient for demo; not for production)
- SQLite file and `.env` must stay out of git (see `.gitignore`)
- Encrypting SSH passwords with an app `SECRET_KEY` is only as strong as that key and local disk access

## Secrets hygiene

- Set `SECRET_KEY` via environment for any shared machine
- Do not commit `.env`, `*.db`, or private keys
- CI uses ephemeral in-memory DB and mocked SSH — no repository secrets required
