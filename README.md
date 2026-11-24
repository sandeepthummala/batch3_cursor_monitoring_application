# Demo Monitoring Infrastructure

Local web app for viewing live Linux server metrics (CPU, memory, network, ports) without routine SSH logins. Manage monitored hosts and browse a simple dashboard.

**Local only.** This is a demo intended to run on your machine (e.g. where Cursor is running). Do not expose it to the network or use it as a production monitoring system.

## Layout

| Path | Purpose |
|------|---------|
| `app/` | Flask application package |
| `templates/` | Jinja templates |
| `static/` | CSS / JS assets |
| `tests/` | Automated tests |
| `docs/` | PRD, TODO, and design notes |

## Stack

Python, Flask, Jinja, SQLite (details in later phases).

See `docs/requirements.md` for the product scope and `docs/TODO.md` for the build plan.
