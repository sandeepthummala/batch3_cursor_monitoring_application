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
- [ ] Create Flask app entry (`app.py` or `app/__init__.py`) that serves a home/placeholder page
- [ ] Add `SECRET_KEY` from environment (fallback only for local demo; document it)
- [ ] **Security:** Do not hardcode production secrets; use env var for `SECRET_KEY`
- [ ] **Docs:** README — how to create venv, install deps, run `flask run` / `python app.py`

### 0.3 Basic UI shell (Jinja + Bootstrap/Tailwind)
- [ ] Add base layout template (`base.html`) with nav placeholder
- [ ] Load Bootstrap and/or Tailwind via CDN in base template
- [ ] Add simple home/dashboard stub page (static content, no metrics yet)
- [ ] **Security:** Set basic response headers later-ready (no inline secrets in templates)
- [ ] **Docs:** Note in README which CSS framework is used and where templates live

### 0.4 Local run smoke check
- [ ] Confirm app opens at `http://127.0.0.1:5000`
- [ ] **Security:** Bind to localhost for demo (`127.0.0.1`) by default
- [ ] **Docs:** One-line “open browser” instruction in README

---

## Phase 1 — Sign-in & unit tests

### 1.1 SQLite + user model
- [ ] Add SQLite setup (SQLAlchemy or plain sqlite3) and `users` table
- [ ] Store password as hash only (Werkzeug `generate_password_hash` / `check_password_hash`)
- [ ] Seed default user `admin` with hashed password on first run
- [ ] **Security:** Never store plaintext passwords; document default demo password only in local README (not committed secrets file if avoidable)
- [ ] **Docs:** Document default username and how password is hashed

### 1.2 Login / logout routes
- [ ] Login form page (Jinja + Bootstrap/Tailwind)
- [ ] POST login: validate credentials, create session
- [ ] Logout route: clear session
- [ ] **Security:** Use Flask session cookies; set `SESSION_COOKIE_HTTPONLY`; use POST for logout if practical
- [ ] **Docs:** Document login URL and session behavior

### 1.3 Auth guard
- [ ] Protect all non-login pages (redirect to login if anonymous)
- [ ] After login, redirect to dashboard stub
- [ ] **Security:** Central `@login_required` (or equivalent); no monitoring routes without auth
- [ ] **Docs:** Note which routes are public vs protected

### 1.4 Unit tests for auth
- [ ] Add `pytest` (+ Flask test client) to `requirements.txt` / `requirements-dev.txt`
- [ ] Test: login success with valid admin credentials
- [ ] Test: login failure with wrong password
- [ ] Test: protected route redirects when logged out
- [ ] Test: logout clears access to protected routes
- [ ] **Security:** Tests must not print or assert plaintext of production secrets; use test config / temp DB
- [ ] **Docs:** README — how to run `pytest`

### 1.5 CI: GitHub Actions (auth + lint baseline)
- [ ] Add `.github/workflows/ci.yml`
- [ ] Job: checkout, set up Python, install deps, run `pytest`
- [ ] Optional: lightweight lint (`ruff` or `flake8`)
- [ ] **Security:** No secrets in workflow logs; use ephemeral test DB
- [ ] **Docs:** Mention CI badge / “CI runs tests on push” in README

---

## Phase 2 — Server CRUD (config only, no live metrics yet)

### 2.1 Server model
- [ ] Add `servers` table: display name, host, SSH user, auth method, password/key path, SSH port (default 22)
- [ ] **Security:** Prefer storing SSH password encrypted or mark demo risk; never log credentials; prefer key path over embedding private key material when possible
- [ ] **Docs:** Document server fields and auth method options

### 2.2 Add server form
- [ ] UI form to add a Linux server
- [ ] Validate required fields server-side
- [ ] **Security:** CSRF protection (Flask-WTF) on forms; sanitize/validate host input (no shell injection later)
- [ ] **Docs:** Document how to add a server

### 2.3 Edit & delete server
- [ ] Edit form (pre-filled)
- [ ] Delete with confirm in UI
- [ ] **Security:** Only authenticated users; confirm delete; do not echo secrets back in HTML (mask password fields)
- [ ] **Docs:** Document edit/delete flows

### 2.4 Server list page
- [ ] List configured servers (name, host, port) — no live metrics yet
- [ ] Links to edit/delete/detail stub
- [ ] **Security:** Auth-required; do not display stored SSH passwords
- [ ] **Docs:** Screenshot or short description of list page

### 2.5 Tests + CI update
- [ ] Unit tests: create / edit / delete server (auth required)
- [ ] Test: unauthenticated cannot mutate servers
- [ ] **Security:** Assert passwords are not returned in list responses/HTML
- [ ] **Docs:** Update test run notes if new markers/fixtures added
- [ ] CI already runs `pytest` — ensure new tests pass in GitHub Actions

---

## Phase 3 — SSH connection test

### 3.1 SSH helper
- [ ] Add Paramiko (or equivalent) dependency
- [ ] Implement `test_connection(server)` → success/failure + message
- [ ] **Security:** Timeouts; disable unknown-host auto-trust or document demo known_hosts policy; never log passwords/keys
- [ ] **Docs:** Document SSH requirements on target Linux hosts

### 3.2 Wire “Test connection” in UI
- [ ] Button on add/edit (or after save) shows success/failure flash
- [ ] **Security:** Auth-required endpoint; rate-limit naively if easy (optional for demo)
- [ ] **Docs:** Document expected success/failure messages

### 3.3 Tests
- [ ] Unit test with mocked SSH (no real network in CI)
- [ ] **Security:** Mocks must not require real credentials in CI
- [ ] **Docs:** Note that CI uses mocks for SSH
- [ ] Confirm GitHub Actions still green

---

## Phase 4 — Metric collection (SSH, no agent)

### 4.1 Collect CPU & memory
- [ ] Remote commands over SSH for CPU % and memory used/total
- [ ] Parse into a simple dict/struct
- [ ] **Security:** Fixed command strings only (no user-controlled shell); timeouts
- [ ] **Docs:** Document commands used and parsed fields

### 4.2 Collect network & listening ports
- [ ] Network in/out via SSH commands
- [ ] Listening ports (e.g. `ss`) and process if available
- [ ] **Security:** Read-only commands; handle large output safely
- [ ] **Docs:** Document network/port fields shown in UI

### 4.3 Unreachable handling
- [ ] On SSH failure, return clear “unreachable” status + error message
- [ ] **Security:** Sanitize error messages (no credential leakage)
- [ ] **Docs:** Document unreachable behavior

### 4.4 Tests
- [ ] Unit tests with mocked SSH command output for CPU/mem/network/ports
- [ ] Test unreachable path
- [ ] **Security:** No real SSH in CI
- [ ] CI: keep GitHub Actions green

---

## Phase 5 — Dashboard, detail views & auto-refresh

### 5.1 Overview dashboard
- [ ] Show all servers with reachable status + summary CPU/memory
- [ ] Link to detail page
- [ ] **Security:** Auth-required; read-only display
- [ ] **Docs:** Describe dashboard fields

### 5.2 Server detail page
- [ ] Show CPU, memory, network, listening ports (read-only)
- [ ] Show unreachable error state clearly
- [ ] **Security:** No remote shell UI; metrics display only
- [ ] **Docs:** Describe detail page layout

### 5.3 Auto-refresh (10s)
- [ ] Client poll or meta-refresh every 10 seconds on dashboard/detail
- [ ] Prefer small JSON endpoint for metrics refresh if simple
- [ ] **Security:** Refresh endpoints auth-required; no credential data in JSON
- [ ] **Docs:** Document 10s refresh behavior

### 5.4 Polish UI
- [ ] Consistent Bootstrap/Tailwind styling across login, dashboard, list, detail, forms
- [ ] **Security:** Escape all user/server-provided strings in Jinja (default autoescape on)
- [ ] **Docs:** Final UI page list in README

### 5.5 Tests + CI
- [ ] Tests for dashboard/detail routes (auth + mocked metrics)
- [ ] Test refresh/metrics endpoint rejects anonymous users
- [ ] **Docs:** Final “how to demo” section in README (login → add server → view metrics)
- [ ] Confirm full `pytest` suite passes in GitHub Actions

---

## Phase 6 — Hardening, docs wrap-up & CI polish

### 6.1 Security pass
- [ ] Review: hashed passwords, session cookie flags, CSRF on forms, no secrets in git
- [ ] Ensure localhost bind by default; document risk if exposing beyond localhost
- [ ] Mask secrets in UI; confirm logs have no passwords/keys
- [ ] **Docs:** Short `docs/SECURITY.md` (demo threats + mitigations)

### 6.2 Documentation pass
- [ ] README: minimal local setup (venv, install, run, login, add server)
- [ ] Link PRD (`docs/requirements.md`) and this TODO
- [ ] **Docs:** Note demo limitations (single admin, local SQLite, SSH from this machine)

### 6.3 CI/CD finalize
- [ ] GitHub Actions: test on push/PR to main
- [ ] Cache pip dependencies
- [ ] Fail CI on test failure
- [ ] **Security:** No repository secrets required for demo CI (mocked SSH)
- [ ] **Docs:** Document CI workflow path `.github/workflows/ci.yml`

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
