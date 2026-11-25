# Demo Monitoring Infrastructure

Local web app for viewing live Linux server metrics (CPU, memory, network, ports) over SSH — no agent on hosts.

**Local only.** Bind defaults to `127.0.0.1`. Do not expose this as a production monitoring system.

[![CI](https://github.com/sandeepthummala/batch3_cursor_monitoring_application/actions/workflows/ci.yml/badge.svg)](https://github.com/sandeepthummala/batch3_cursor_monitoring_application/actions/workflows/ci.yml)

## Stack

- Python 3 / Flask / Jinja2
- Bootstrap 5 (CDN) in `templates/`
- SQLite (local file `monitoring.db`)
- Paramiko SSH for connection tests and metrics
- GitHub Actions CI runs `pytest` (+ ruff) on push/PR to `main` (`.github/workflows/ci.yml`)

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
export SECRET_KEY='change-me'   # optional; a demo fallback exists
python app.py
```

Open **http://127.0.0.1:5000**

### Login

| Field | Demo value |
|-------|------------|
| Username | `admin` |
| Password | `admin` (override with `DEMO_ADMIN_PASSWORD` before first run) |

Password is stored hashed (Werkzeug). Change the demo password via env before the DB is created, or delete `monitoring.db` and restart.

### How to demo

1. Sign in as `admin`
2. **Servers → Add server** (host, SSH user, password or key path, port)
3. Use **Test connection**, then **Save**
4. Open **Dashboard** / server detail — metrics refresh every **10 seconds**

## Layout

| Path | Purpose |
|------|---------|
| `app/` | Flask package (models, routes, SSH helpers) |
| `templates/` | Jinja templates (Bootstrap UI) |
| `static/` | CSS / JS (10s refresh poller) |
| `tests/` | pytest suite (SSH mocked in CI) |
| `docs/` | PRD, TODO, SECURITY |

## Routes

| Route | Access |
|-------|--------|
| `/login` | Public |
| `/logout` (POST) | Session |
| `/`, `/servers/*`, `/api/*` | Authenticated only |

## Server fields

Display name, host/IP, SSH username, auth method (`password` or `key`), SSH password (encrypted at rest) or private key **path**, SSH port (default 22).

## SSH metrics (read-only)

Fixed remote commands: `/proc/stat`, `free -b`, `/proc/net/dev`, `ss`. Failures show **unreachable** with a sanitized message. CI never opens real SSH.

## Tests

```bash
pip install -r requirements-dev.txt
pytest -q
```

## Docs

- Product scope: [`docs/requirements.md`](docs/requirements.md)
- Build checklist: [`docs/TODO.md`](docs/TODO.md)
- Security: [`docs/SECURITY.md`](docs/SECURITY.md)

## Limitations

Single seeded admin, local SQLite, SSH from this machine only, demo host-key policy (`AutoAddPolicy`).
