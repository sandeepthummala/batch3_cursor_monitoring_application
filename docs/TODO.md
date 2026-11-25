# TODO: Demo Monitoring Infrastructure (Linux)

Small, AI-friendly increments. Work top to bottom. Each step includes **implementation**, **security**, and **docs**.

Demo target: run locally where Cursor is running. Keep steps minimal.

---

## Phase 0 — Project initialization & basic UI

### 0.1 Repo skeleton
- [x] Create app layout: `app/` (or package root), `templates/`, `static/`, `tests/`, `docs/`
- [x] Add `requirements.txt` with Flask (pin versions)
- [x] Add `.gitignore` (venv, `__pycache__`, `.env`, `*.db`, secrets)
- [x] **Security:** Ensure `.env`, SQLite DB, and SSH key paths are gitignored
- [x] **Docs:** Short `README.md` — what the app is + “local only” note

### 0.2 Minimal Flask app
- [x] Create Flask app entry (`app.py` or `app/__init__.py`) that serves a home/placeholder page
- [x] Add `SECRET_KEY` from environment (fallback only for local demo; document it)
- [x] **Security:** Do not hardcode production secrets; use env var for `SECRET_KEY`
- [x] **Docs:** README — how to create venv, install deps, run `flask run` / `python app.py`

### 0.3 Basic UI shell (Jinja + Bootstrap/Tailwind)
- [x] Add base layout template (`base.html`) with nav placeholder
- [x] Load Bootstrap and/or Tailwind via CDN in base template
- [x] Add simple home/dashboard stub page (static content, no metrics yet)
- [x] **Security:** Set basic response headers later-ready (no inline secrets in templates)
- [x] **Docs:** Note in README which CSS framework is used and where templates live

### 0.4 Local run smoke check
- [x] Confirm app opens at `http://127.0.0.1:5000`
- [x] **Security:** Bind to localhost for demo (`127.0.0.1`) by default
- [x] **Docs:** One-line “open browser” instruction in README

---

## Phase 1 — Sign-in & unit tests

### 1.1 SQLite + user model
- [x] Add SQLite setup (SQLAlchemy or plain sqlite3) and `users` table
- [x] Store password as hash only (Werkzeug `generate_password_hash` / `check_password_hash`)
- [x] Seed default user `admin` with hashed password on first run
- [x] **Security:** Never store plaintext passwords; document default demo password only in local README (not committed secrets file if avoidable)
- [x] **Docs:** Document default username and how password is hashed

### 1.2 Login / logout routes
- [x] Login form page (Jinja + Bootstrap/Tailwind)
- [x] POST login: validate credentials, create session
- [x] Logout route: clear session
- [x] **Security:** Use Flask session cookies; set `SESSION_COOKIE_HTTPONLY`; use POST for logout if practical
- [x] **Docs:** Document login URL and session behavior

### 1.3 Auth guard
- [x] Protect all non-login pages (redirect to login if anonymous)
- [x] After login, redirect to dashboard stub
- [x] **Security:** Central `@login_required` (or equivalent); no monitoring routes without auth
- [x] **Docs:** Note which routes are public vs protected

### 1.4 Unit tests for auth
- [x] Add `pytest` (+ Flask test client) to `requirements.txt` / `requirements-dev.txt`
- [x] Test: login success with valid admin credentials
- [x] Test: login failure with wrong password
- [x] Test: protected route redirects when logged out
- [x] Test: logout clears access to protected routes
- [x] **Security:** Tests must not print or assert plaintext of production secrets; use test config / temp DB
- [x] **Docs:** README — how to run `pytest`

### 1.5 CI: GitHub Actions (auth + lint baseline)
- [x] Add `.github/workflows/ci.yml`
- [x] Job: checkout, set up Python, install deps, run `pytest`
- [x] Optional: lightweight lint (`ruff` or `flake8`)
- [x] **Security:** No secrets in workflow logs; use ephemeral test DB
- [x] **Docs:** Mention CI badge / “CI runs tests on push” in README

---

## Phase 2 — Server CRUD (config only, no live metrics yet)

### 2.1 Server model
- [x] Add `servers` table: display name, host, SSH user, auth method, password/key path, SSH port (default 22)
- [x] **Security:** Prefer storing SSH password encrypted or mark demo risk; never log credentials; prefer key path over embedding private key material when possible
- [x] **Docs:** Document server fields and auth method options

### 2.2 Add server form
- [x] UI form to add a Linux server
- [x] Validate required fields server-side
- [x] **Security:** CSRF protection (Flask-WTF) on forms; sanitize/validate host input (no shell injection later)
- [x] **Docs:** Document how to add a server

### 2.3 Edit & delete server
- [x] Edit form (pre-filled)
- [x] Delete with confirm in UI
- [x] **Security:** Only authenticated users; confirm delete; do not echo secrets back in HTML (mask password fields)
- [x] **Docs:** Document edit/delete flows

### 2.4 Server list page
- [x] List configured servers (name, host, port) — no live metrics yet
- [x] Links to edit/delete/detail stub
- [x] **Security:** Auth-required; do not display stored SSH passwords
- [x] **Docs:** Screenshot or short description of list page

### 2.5 Tests + CI update
- [x] Unit tests: create / edit / delete server (auth required)
- [x] Test: unauthenticated cannot mutate servers
- [x] **Security:** Assert passwords are not returned in list responses/HTML
- [x] **Docs:** Update test run notes if new markers/fixtures added
- [x] CI already runs `pytest` — ensure new tests pass in GitHub Actions

---

## Phase 3 — SSH connection test

### 3.1 SSH helper
- [x] Add Paramiko (or equivalent) dependency
- [x] Implement `test_connection(server)` → success/failure + message
- [x] **Security:** Timeouts; disable unknown-host auto-trust or document demo known_hosts policy; never log passwords/keys
- [x] **Docs:** Document SSH requirements on target Linux hosts

### 3.2 Wire “Test connection” in UI
- [x] Button on add/edit (or after save) shows success/failure flash
- [x] **Security:** Auth-required endpoint; rate-limit naively if easy (optional for demo)
- [x] **Docs:** Document expected success/failure messages

### 3.3 Tests
- [x] Unit test with mocked SSH (no real network in CI)
- [x] **Security:** Mocks must not require real credentials in CI
- [x] **Docs:** Note that CI uses mocks for SSH
- [x] Confirm GitHub Actions still green

---

## Phase 4 — Metric collection (SSH, no agent)

### 4.1 Collect CPU & memory
- [x] Remote commands over SSH for CPU % and memory used/total
- [x] Parse into a simple dict/struct
- [x] **Security:** Fixed command strings only (no user-controlled shell); timeouts
- [x] **Docs:** Document commands used and parsed fields

### 4.2 Collect network & listening ports
- [x] Network in/out via SSH commands
- [x] Listening ports (e.g. `ss`) and process if available
- [x] **Security:** Read-only commands; handle large output safely
- [x] **Docs:** Document network/port fields shown in UI

### 4.3 Unreachable handling
- [x] On SSH failure, return clear “unreachable” status + error message
- [x] **Security:** Sanitize error messages (no credential leakage)
- [x] **Docs:** Document unreachable behavior

### 4.4 Tests
- [x] Unit tests with mocked SSH command output for CPU/mem/network/ports
- [x] Test unreachable path
- [x] **Security:** No real SSH in CI
- [x] CI: keep GitHub Actions green

---

## Phase 5 — Dashboard, detail views & auto-refresh

### 5.1 Overview dashboard
- [x] Show all servers with reachable status + summary CPU/memory
- [x] Link to detail page
- [x] **Security:** Auth-required; read-only display
- [x] **Docs:** Describe dashboard fields

### 5.2 Server detail page
- [x] Show CPU, memory, network, listening ports (read-only)
- [x] Show unreachable error state clearly
- [x] **Security:** No remote shell UI; metrics display only
- [x] **Docs:** Describe detail page layout

### 5.3 Auto-refresh (10s)
- [x] Client poll or meta-refresh every 10 seconds on dashboard/detail
- [x] Prefer small JSON endpoint for metrics refresh if simple
- [x] **Security:** Refresh endpoints auth-required; no credential data in JSON
- [x] **Docs:** Document 10s refresh behavior

### 5.4 Polish UI
- [x] Consistent Bootstrap/Tailwind styling across login, dashboard, list, detail, forms
- [x] **Security:** Escape all user/server-provided strings in Jinja (default autoescape on)
- [x] **Docs:** Final UI page list in README

### 5.5 Tests + CI
- [x] Tests for dashboard/detail routes (auth + mocked metrics)
- [x] Test refresh/metrics endpoint rejects anonymous users
- [x] **Docs:** Final “how to demo” section in README (login → add server → view metrics)
- [x] Confirm full `pytest` suite passes in GitHub Actions

---

## Phase 6 — Hardening, docs wrap-up & CI polish

### 6.1 Security pass
- [x] Review: hashed passwords, session cookie flags, CSRF on forms, no secrets in git
- [x] Ensure localhost bind by default; document risk if exposing beyond localhost
- [x] Mask secrets in UI; confirm logs have no passwords/keys
- [x] **Docs:** Short `docs/SECURITY.md` (demo threats + mitigations)

### 6.2 Documentation pass
- [x] README: minimal local setup (venv, install, run, login, add server)
- [x] Link PRD (`docs/requirements.md`) and this TODO
- [x] **Docs:** Note demo limitations (single admin, local SQLite, SSH from this machine)

### 6.3 CI/CD finalize
- [x] GitHub Actions: test on push/PR to main
- [x] Cache pip dependencies
- [x] Fail CI on test failure
- [x] **Security:** No repository secrets required for demo CI (mocked SSH)
- [x] **Docs:** Document CI workflow path `.github/workflows/ci.yml`

---

## Suggested implement order (checklist summary)

1. [ ] Phase 0 — Init + basic UI  
2. [ ] Phase 1 — Sign-in + unit tests + CI  
3. [ ] Phase 2 — Server CRUD  
4. [ ] Phase 3 — SSH connection test  
5. [ ] Phase 4 — Metric collection  
6. [ ] Phase 5 — Dashboard / detail / auto-refresh  
7. [ ] Phase 6 — Security + docs + CI polish  

When implementing with AI assistance: complete **one checkbox group** (e.g. 1.2) per change set, run tests, update docs, then move on.
