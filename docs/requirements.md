# PRD: Demo Monitoring Infrastructure (Linux Servers)

## 1. Overview

Local demo web app to view live Linux server metrics without SSH login for routine checks.

**Audience:** Internal L1 / L2 / L3, infrastructure, and application teams  
**Deploy:** Local machine (where Cursor runs)  
**Stack:** Python, Flask, Jinja templates + Bootstrap/Tailwind, SQLite

## 2. Problem

Teams must SSH into each server to check CPU, memory, network, and port usage. That is slow and error-prone for day-to-day monitoring.

## 3. Goals

- Read-only UI for live server metrics
- Add / edit / delete Linux servers to monitor
- Collect metrics over SSH (no agent on hosts)
- Simple local login (`admin` + hashed password)
- Attractive, easy-to-use UI

## 4. Users & access

| Role | Access |
|------|--------|
| Admin (default) | Sign in, manage servers, view all metrics (read-only) |

- Default username: `admin`
- Password stored hashed (e.g. Werkzeug / bcrypt)
- Login only — no change-password flow in this demo

## 5. Features

### 5.1 Sign in

- Login page with username + password
- Session-based auth after successful login
- Redirect unauthenticated users to login

### 5.2 Server management

Provision to manage Linux hosts:

| Field | Required | Notes |
|-------|----------|--------|
| Display name | Yes | Friendly label |
| Hostname / IP | Yes | Target host |
| SSH username | Yes | Remote user |
| Auth method | Yes | SSH password **or** private key path |
| SSH password / key | Yes | Matching auth method |
| SSH port | No | Default `22` |

Actions:

- **Add** server
- **Edit** server
- **Delete** server
- **Test connection** on save (or dedicated button) — report success/failure

### 5.3 Overview dashboard

- At-a-glance view of all monitored servers
- Show status (reachable / unreachable) and summary metrics (CPU, memory)
- Link through to server detail

### 5.4 Server list & detail (read-only metrics)

**List:** All configured servers with key status indicators.

**Detail (per server):**

| Metric | Display |
|--------|---------|
| CPU | Usage % |
| Memory | Used / total (and %) |
| Network | In / out rates or counters |
| Ports | Listening ports (and process/service if available) |

- UI is **read-only** for metrics (no remote shell, no config changes on hosts)
- **Auto-refresh** every **10 seconds**

### 5.5 Metric collection

- No agent on target hosts
- App connects via SSH and runs standard Linux commands (e.g. CPU/mem/network/`ss` or equivalent)
- On SSH failure: mark server unreachable and show a clear error on UI

## 6. UI requirements

- Flask + Jinja templates, styled with **Bootstrap and/or Tailwind** (CSS framework loaded inside Flask templates; no separate frontend app)
- Clean, attractive, user-friendly layout
- Pages: Login, Dashboard, Server list, Server detail, Add/Edit server
- Read-only presentation of live data

## 7. Technical requirements

| Item | Choice |
|------|--------|
| Language | Python 3 |
| Web | Flask |
| Templates | Jinja2 |
| CSS / UI kit | Bootstrap and/or Tailwind (served or CDN via templates) |
| DB | Local SQLite (users, servers) |
| Remote access | SSH (Paramiko or equivalent) |
| Auth | Session + hashed password |
| Refresh | Auto every 10s (client poll or equivalent) |

## 8. Local run (minimal)

1. Create/activate a Python venv and install dependencies (`requirements.txt`)
2. Initialize SQLite (auto on first run or simple script)
3. Seed default `admin` user with a hashed password
4. Start Flask app (e.g. `flask run` or `python app.py`)
5. Open browser to local URL (e.g. `http://127.0.0.1:5000`)
6. Sign in as `admin`, add a Linux server, view dashboard/detail

## 9. Acceptance criteria

- [ ] User can sign in with `admin` and hashed password
- [ ] Unauthenticated users cannot view monitoring pages
- [ ] User can add, edit, and delete Linux servers
- [ ] Connection test reports success or failure
- [ ] Dashboard shows all servers with summary status/metrics
- [ ] Detail page shows CPU, memory, network, and listening ports
- [ ] Metrics auto-refresh every 10 seconds
- [ ] Metrics UI is read-only
- [ ] Collection uses SSH only (no host agent)
- [ ] App runs locally with SQLite
- [ ] UI is Jinja templates inside Flask, styled with Bootstrap and/or Tailwind

## 10. Assumptions

- Target hosts are Linux and reachable over SSH from the demo machine
- Demo credentials and SSH secrets are for local use only
- Auto-refresh interval is 10 seconds unless changed later
