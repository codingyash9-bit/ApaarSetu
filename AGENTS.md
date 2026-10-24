# AGENTS.md — APAAR Nexus (SIH PS 26263)

> Read this file completely before writing any code.
> It is the single source of truth for every AI coding agent (Claude Code, Cursor, Copilot, Codex) and for both human teammates (Member A and Member B).
> If a prompt conflicts with this file, this file wins. If this file is wrong, fix it in a small PR and tell your teammate.

---

## 1. Project snapshot

**APAAR Nexus** is a working prototype for Smart India Hackathon problem statement **PS 26263**: a platform where AICTE-approved institutions submit, validate, monitor and verify student-level academic records using APAAR ID as the intended unique academic identifier.

The prototype has three pillars:

| Pillar | Name | What it really does |
|---|---|---|
| Prevent | Dynamic Seat Ledger | Blocks admissions beyond approved intake, keeps regular and supernumerary seats separate |
| Detect | Identity Graph + Explainable Risk Engine | Finds duplicate / conflicting identities, scores them with transparent rules, requires human review |
| Prove | Academic Passport | Ed25519-signed credentials, QR verification, consent-based selective sharing |

**Everything is synthetic.** We do NOT connect to AICTE, APAAR, UIDAI, DigiLocker or any government system. Every screen that shows demo data must make that clear (footer banner: "Prototype — synthetic data only").

---

## 2. Non-negotiable rules

1. **Stack is fixed.** Python 3 + Flask + Flask-SQLAlchemy + Flask-Login + Flask-WTF (CSRF) + SQLite. Frontend is plain HTML5 + CSS3 + vanilla JavaScript (ES6+) with Chart.js and Cytoscape.js.
2. **Forbidden:** React, TypeScript, Vite, Node.js, npm, Express, FastAPI, MongoDB, Tailwind, Bootstrap, jQuery, any frontend build step.
3. **Chart.js and Cytoscape.js are vendored** into `static/vendor/` (downloaded once, committed). No CDN links, so the demo works offline.
4. **QR codes are generated server-side** with the Python `qrcode` library (returned as PNG/SVG data). No JS QR library.
5. **Runs on Windows 11** with Python 3.11+ and a browser. No Linux-only commands, no bash scripts. Use PowerShell in docs.
6. **Never claim what is not implemented.** No "zero-knowledge", no "blockchain", no "live APAAR verification". APAAR validation is a format check plus a clearly labelled mock adapter.
7. **Never claim tests passed unless you ran them** and saw the output.
8. **No automatic punishment.** Risk scores never auto-flag a student as fraudulent and never auto-revoke credentials. A human with the right role must act.
9. **Shared phone numbers / fee-payer references are investigation signals, not proof.** They must never be unique-constrained and never cause a hard rejection.
10. **Secrets:** private keys, passwords, full sharing tokens and full APAAR IDs must never appear in logs, API responses (except where explicitly allowed below) or the frontend.
11. **Server-side enforcement only.** Frontend role checks are cosmetic. Every route enforces role + institution scope on the server.
12. **No dead buttons.** If a button exists, it performs a real action and shows success/error feedback.

---

## 3. Team ownership map

Two people: Tanmay (Member A) and Yash (Member B). Each person owns specific folders/files. Use exactly two long-lived branches: `member-a` and `member-b`; never create task-specific branches. Do not edit files you do not own without telling the owner (small PR + message).

### Member A — "Data, Security & Prevent"
Owns: project bootstrap, all database models, seed script (core), authentication and RBAC, institutions, students, CSV ingestion, APAAR adapter, validation, Seat Ledger, audit service, institution dashboard, enrolment report, A-side tests.

Files:
```
app.py, config.py, extensions.py, seed.py, requirements.txt, .env.example, .gitignore
models/*                      (ALL models, including Member B's tables)
routes/auth.py, institutions.py, students.py, admissions.py
routes/dashboards.py          (institution part only)
routes/reports.py             (enrolment report only)
services/apaar_adapter.py, validation_service.py, seat_ledger.py, csv_service.py, audit_service.py, authz.py
templates/login.html, institutions.html, students.html, student_detail.html, upload.html, seat_ledger.html, audit_logs.html, policies.html
static/js/students.js, seat-ledger.js, upload.js, institutions.js
sample_data/students.csv
tests/test_auth.py, test_students.py, test_seat_ledger.py, test_audit.py, conftest.py
```

### Member B — "UI Shell, Detect & Prove"
Owns: design system and base layout, shared JS, identity resolution, risk engine, identity graph, risk cases, credentials, QR verification, passport, consent sharing, governance dashboard, regulatory reports, B-side tests.

Files:
```
templates/base.html, dashboard.html, identity_graph.html, risk_cases.html, risk_case_detail.html,
          passport.html, issue_credential.html, verification.html, sharing.html, public_verify.html, reports.html
static/css/style.css, static/js/app.js, dashboard.js, identity-graph.js, risk.js, credentials.js, sharing.js
static/vendor/*
routes/identity.py, risk.py, credentials.py, sharing.py
routes/dashboards.py          (governance part only)
routes/reports.py             (anomaly report only)
services/identity_resolution.py, risk_engine.py, credential_service.py, sharing_service.py
seed_b.py                     (credentials, risk cases, sharing session seed — called by seed.py)
tests/test_identity.py, test_risk.py, test_credentials.py, test_privacy.py, test_sharing.py
docs/API.md (B sections), docs/SECURITY.md, docs/DEMO_SCRIPT.md
```

### Shared (edit with care)
- `README.md` — A writes setup/data/seat sections, B writes graph/credential/sharing sections.
- `docs/API.md` — each person documents their own endpoints.
- `routes/__init__.py` — one line per blueprint in `register_all(app)`; each person adds only their own lines.
- `models/*` — **A owns it.** B needs a field changed → message A, A edits within the hour (or B opens a tiny PR touching only that model and tags A).

---

## 4. Fixed repository structure

```
apaar-nexus/
├── app.py
├── config.py
├── extensions.py
├── seed.py
├── seed_b.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── AGENTS.md
├── STEPS.md
├── models/        __init__, user, institution, student, admission, identity, risk, credential, audit, policy
├── routes/        __init__, auth, institutions, students, admissions, identity, risk, credentials, sharing, dashboards, reports
├── services/      apaar_adapter, validation_service, seat_ledger, identity_resolution, risk_engine,
│                  credential_service, sharing_service, audit_service, csv_service, authz
├── templates/     base, login, dashboard, institutions, students, student_detail, upload, seat_ledger,
│                  identity_graph, risk_cases, risk_case_detail, passport, issue_credential,
│                  verification, public_verify, sharing, reports, audit_logs, policies
├── static/        css/style.css, js/*.js, vendor/ (chart.umd.min.js, cytoscape.min.js), img/
├── sample_data/   students.csv, students_demo_upload.csv
├── docs/          API.md, DB_SCHEMA.md, SECURITY.md, DEMO_SCRIPT.md
├── tests/
└── instance/      .gitkeep
```

(The master prompt had a typo `apa ar_adapter.py`. The correct name is `apaar_adapter.py`.)

---

## 5. Shared contracts (both members must follow exactly)

### 5.1 Roles
`AICTE_ADMIN`, `INSTITUTION_ADMIN`, `STUDENT`, `VERIFIER`, `AUDITOR`

### 5.2 Demo accounts (created by `seed.py`)

Password for all four demo users comes from env `DEMO_PASSWORD` (default `Demo@12345`, development only). If `FLASK_ENV=production`, the seed script must refuse to print or use the default.

| Username | Role | Scope |
|---|---|---|
| `AICTE_Admin` | AICTE_ADMIN | all three institutions |
| `VESIT` | INSTITUTION_ADMIN | VESIT only |
| `COEP` | INSTITUTION_ADMIN | COEP only |
| `VJTI` | INSTITUTION_ADMIN | VJTI only |

Seed exactly these four users—no student, verifier, auditor, or extra demo accounts. All four use `DEMO_PASSWORD` in development. Public verification remains available through read-only public routes; do not create a verifier login. Student records remain synthetic data and are not user accounts.

### 5.3 Enumerations (use these exact strings in DB and API)

- `classification`: `REGULAR`, `SUPERNUMERARY`
- `admission_category`: `OPEN`, `OBC`, `SC`, `ST`, `EWS`, `NRI`, `OCI`, `FN`
- `enrolment_status`: `ACTIVE`, `WITHDRAWN`, `GRADUATED`
- `validation_status`: `PENDING`, `VALID`, `INVALID`, `FLAGGED`
- `submission_status`: `PREVIEWED`, `COMMITTED`, `PARTIAL`, `REJECTED`
- `admission_event_result`: `ACCEPTED`, `REJECTED`
- `risk_severity`: `LOW` (0–29), `MEDIUM` (30–59), `HIGH` (60–79), `CRITICAL` (80–100)
- `case_status`: `OPEN`, `UNDER_REVIEW`, `CLARIFICATION_REQUESTED`, `DATA_ERROR_CONFIRMED`, `FALSE_POSITIVE`, `RESOLVED`
- `case_action`: `UNDER_REVIEW`, `REQUEST_CLARIFICATION`, `CONFIRM_DATA_ERROR`, `DISMISS_FALSE_POSITIVE`, `RESOLVE`
- `credential_status_stored`: `ISSUED`, `REVOKED`
- `verification_result` (computed on the server at verify time): `VERIFIED`, `INVALID`, `REVOKED`, `EXPIRED`
- `sharing_claim`: `DEGREE_AUTHENTICITY`, `INSTITUTION`, `PROGRAMME`, `AWARD_YEAR`, `STUDENT_NAME`, `APAAR_MASKED`
- `sharing_expiry_hours`: `24`, `72`, `168`

### 5.4 APAAR handling
- Stored as an **external identifier** column (`apaar_ref`), never a primary key, never globally unique.
- Prototype format rule (configurable in `system_policies`, key `apaar_regex`): 12 digits, `^\d{12}$`. This is a **format check only**.
- `services/apaar_adapter.py` exposes `validate_format(ref)` and `mock_verify(ref)`. The mock verify is deterministic and labelled `MOCK — not connected to any government system` in every response.
- Masking helper (one function, one place, used everywhere): `mask_apaar("123456789012") -> "XXXXXXXX9012"`.

### 5.5 Risk weights (stored in `system_policies`, key `risk_weights`)
```
DUPLICATE_APAAR        40
SIMULTANEOUS_ENROLMENT 35
DUPLICATE_INSTITUTE_ID 25
SIMILAR_NAME_CORROBORATED 15
SHARED_CONTACT         10
SHARED_FEE_PAYER       10
MISSING_OR_MALFORMED_APAAR 20
CONFLICTING_ACADEMIC_DATA 15
EXCESS_INTAKE_VIOLATION 30
```
Score is capped at 100. The same underlying event (same `event_key`) is never counted twice.

### 5.6 API response envelope
Success:
```json
{ "ok": true, "data": { }, "meta": { "page": 1, "per_page": 25, "total": 140 } }
```
Error:
```json
{ "ok": false, "error": { "code": "CAPACITY_EXCEEDED", "message": "Human readable explanation", "details": { } } }
```
- `meta` only on list endpoints.
- Standard codes: `UNAUTHENTICATED` (401), `FORBIDDEN` (403), `NOT_FOUND` (404), `VALIDATION_ERROR` (422), `CONFLICT` (409), `CAPACITY_EXCEEDED` (409), `RATE_LIMITED` (429), `SERVER_ERROR` (500).
- Pagination query params: `page`, `per_page` (max 100).

### 5.7 CSRF for JSON calls
- Every HTML page includes `<meta name="csrf-token" content="{{ csrf_token() }}">` (in `base.html`).
- `static/js/app.js` exposes `api(path, {method, body})` which adds header `X-CSRFToken` automatically. All JS must use this wrapper, never raw `fetch` for mutating calls.
- Public routes (`/verify/<reference>`, `/public/verify/<token>`) are GET-only and read-only.

### 5.8 IDs
- All internal primary keys are UUID strings (`str(uuid.uuid4())`).
- Human-friendly references: submissions `SUB-YYYYMMDD-XXXXXX`, risk cases `CASE-XXXXXX`, credentials `CRED-XXXXXX`.

### 5.9 Cross-member service interfaces (agree early, do not change silently)

```python
# Member B provides, Member A calls after import / admission:
services.identity_resolution.scan(institution_id=None, submission_id=None) -> ScanResult
services.risk_engine.evaluate_all(scan_result) -> list[RiskCase]
services.risk_engine.record_excess_intake_event(admission_event) -> RiskCase | None

# Member A provides, Member B calls:
services.audit_service.log(actor, action, entity_type, entity_id, details: dict, institution_id=None)
services.authz.scope_query(query, model)        # restricts queries to current user's institution
services.apaar_adapter.mask_apaar(ref) -> str
```

---

## 5.10 Two-branch workflow and merge-conflict prevention

Only these working branches are permitted:
- `member-a` — Tanmay, Member A
- `member-b` — Yash, Member B

Create each branch once from `main`. Keep using it for every prompt; never create `a/<topic>`, `b/<topic>`, or any other task branch. Do not force-push, rebase a branch other people may have pulled, amend pushed commits, or reset shared history.

PowerShell setup (each member, once):
```powershell
git clone <repo-url> apaar-nexus
cd apaar-nexus
git switch main
git pull --ff-only origin main
git switch -c member-a   # Tanmay only; Yash instead creates member-b
git push -u origin member-a  # replace with member-b for Yash
```
Before each work session:
```powershell
git fetch origin
git switch member-a       # use member-b for Yash
git merge origin/main
```
If merge conflicts occur, do not blindly accept ours/theirs. Compare both changes, preserve both where compatible, run tests, then commit the merge. If a file belongs to the other member, stop and coordinate rather than editing it. Only push after tests and `git status` is clean.

For checkpoint integration, merge Member A's PR first when it contains foundation/models/auth changes. Member B then merges the updated `origin/main` into `member-b`, tests, and opens the checkpoint PR. Keep PRs limited to the two long-lived branches; use small commits for individual prompts. Both members must avoid editing the same shared file at the same time. In `routes/__init__.py`, each member adds only their own blueprint registration line.

## 5.11 Four-account demo seed contract

`seed.py --reset` must create exactly four login users: `AICTE_Admin` (AICTE_ADMIN), `VESIT` (INSTITUTION_ADMIN scoped to VESIT), `COEP` (INSTITUTION_ADMIN scoped to COEP), and `VJTI` (INSTITUTION_ADMIN scoped to VJTI). Seed exactly three institutions: VESIT, COEP, VJTI. No additional institution or demo user may be added. Test both the exact count and cross-institution isolation. Other role enums may remain supported in code for future use, but do not seed accounts for those roles.

## 6. Coding conventions

### Python
- Python 3.11+, type hints on public functions, docstring on every service function.
- Blueprints per module, thin routes, logic in `services/`. Routes parse + authorize + call service + return envelope.
- Use SQLAlchemy ORM only (no string-built SQL). Use `db.session` inside explicit transactions for admissions, student updates, credential issue/revoke.
- Use `pydantic` models (or small validator functions) for request payloads.
- No print debugging committed. Use `current_app.logger`.
- Every mutating action calls `audit_service.log(...)`.
- Config via `.env` (python-dotenv). `SECRET_KEY` is never hard-coded in committed code.

### Naming
- Files `snake_case.py`, JS files `kebab-case.js`, CSS classes `kebab-case`, DB tables plural snake_case (`student_records`).

### Errors
- Never leak stack traces to the client. Register global error handlers returning the envelope.

---

## 7. Frontend rules — SIMPLE AND CLEAN

This is a government-tech prototype. Think "clean official portal", not "startup landing page".

**Design tokens (define once in `style.css` as CSS variables):**
```
--navy: #14315c;      --navy-dark: #0e2444;
--bg: #f5f7fa;        --surface: #ffffff;   --border: #dde3ea;
--text: #1d2733;      --muted: #5b6776;
--ok: #1a7f4b;        --warn: #b7791f;      --danger: #c0392b;   --info: #2b6cb0;
--saffron: #e8892b;   --green: #1a7f4b;     (tiny accents only)
font: "Segoe UI", system-ui, -apple-system, Arial, sans-serif; base size 14px; line-height 1.5
radius: 6px; spacing scale 4/8/12/16/24
```

**Rules:**
1. White cards on a light grey page. Navy top bar and navy sidebar. A 4px saffron-white-green strip at the very top is the only decoration.
2. No gradients, no shadows heavier than `0 1px 2px rgba(0,0,0,.06)`, no animations except a short toast fade.
3. No icon fonts and no emoji in the UI. Use plain text labels. Status is shown with small text badges (coloured text on a pale background).
4. One page = one purpose. Page title on top, short helper line, then content.
5. Tables: compact, sticky header, zebra off, row hover light grey, pagination at the bottom.
6. Forms: label above input, plain inputs, one primary button (navy) per section.
7. Charts: Chart.js with a limited palette (navy, grey-blue, and status colours). Always a title and axis labels.
8. Feedback: toast on success/error, confirm dialog (native `<dialog>`) before destructive actions (revoke, reset, resolve).
9. Responsive for laptop and desktop (≥1024px). Sidebar collapses to a top menu below 900px. No mobile-perfect work required.
10. Accessibility: contrast ≥ 4.5:1, visible focus outline, labels on every input, `aria-live` on toasts.
11. Every page extends `base.html` and shows the footer banner "Prototype — synthetic data only. Not connected to AICTE, APAAR, UIDAI or DigiLocker."
12. Sidebar items are filtered by role **in the template**, but the server still enforces access.

**Sidebar menu (by role):**
- AICTE_ADMIN: Dashboard, Institutions, Students, Seat Ledger, Identity Graph, Risk Cases, Credentials, Reports, Audit Logs, Policies
- INSTITUTION_ADMIN: Dashboard, Students, Upload CSV, Seat Ledger, Risk Cases (own), Issue Credential, Reports
- STUDENT: My Passport, Sharing
- VERIFIER: Verify Credential
- AUDITOR: Reports, Risk Cases (read-only), Audit Logs

---

## 8. Security checklist (every PR)

- [ ] Route has `@login_required` and a role decorator (unless it is one of the two public verify routes).
- [ ] Institution-scoped data goes through `authz.scope_query`. An institution admin can never read or write another institution's data (test it).
- [ ] Input validated server-side. File uploads: `.csv` only, size limit from config (default 2 MB), UTF-8, max rows from config.
- [ ] No secrets, tokens, full APAAR IDs or private keys in logs or responses.
- [ ] Passwords hashed with Werkzeug. Session cookie: `HttpOnly`, `SameSite=Lax`, `Secure` when not in debug.
- [ ] CSRF token required on every POST/PATCH/DELETE from the browser.
- [ ] Sharing tokens: `secrets.token_urlsafe(32)`, only a SHA-256 hash stored, full token shown to the student once.
- [ ] Signing private key never leaves the backend; only public-key metadata is exposed.
- [ ] Mutating actions write an audit log row.
- [ ] Jinja autoescape stays ON. Never use `|safe` on user data.

---

## 9. Testing rules

- `pytest` with an in-memory or temp SQLite DB, a `conftest.py` fixture that builds the app, seeds minimal data and provides logged-in clients per role.
- Each module ships with tests in the same PR as the feature.
- Required coverage areas: login/authorization, institution isolation, CSV import (valid, invalid APAAR, duplicates, idempotent re-import), seat capacity (within, at limit, 121st rejected, supernumerary), concurrency on the last seat, identity conflicts, shared-contact handling, risk score math + cap + dedupe, case workflow + audit, signature verify, tampered credential, revoked credential, expired sharing session, selective disclosure, audit logging.
- Run `pytest -q` before every push. Paste the real summary line in the PR description.

---

## 10. Git workflow

- `main` is always runnable. Do not push broken code to `main`.
- Exactly two working branches: `member-a` (Tanmay) and `member-b` (Yash). Do not create any other feature/task branches.
- Never rebase, force-push, reset, or amend a shared branch. Sync with `git fetch origin`, then merge `origin/main` into your own branch. Resolve conflicts locally before pushing.
- Use checkpoint PRs only: Member A's branch is integrated first when A-owned foundation changes are needed; Member B then merges the updated `main` into `member-b`. For a combined checkpoint, merge `member-a` to `main` first, then update and merge `member-b`. Avoid simultaneous edits to shared files; obey Section 3 ownership and add only your own blueprint-registration line.
- Use checkpoint PRs from `member-a` and `member-b` only. Individual prompts are commits, not separate PRs. The other member reviews each checkpoint.
- Before starting work each session: `git pull --rebase origin main`.
- Commit message format: `<area>: <what>` (e.g. `seat-ledger: block 121st regular admission`).
- Never commit: `.env`, `instance/*.db`, `.venv/`, private keys, `__pycache__/`.
- Sync checkpoints are defined in `STEPS.md`. Both members must be on `main` and green at every checkpoint.

---

## 11. Definition of done (per task)

A task is done only when:
1. The feature works in the browser end to end (not just via API).
2. Role and institution authorization is enforced on the server.
3. Success and error states are visible to the user.
4. An audit log entry is written for mutating actions.
5. Tests for the feature exist and `pytest -q` passes.
6. `docs/API.md` has the endpoints you added.
7. No console errors in the browser, no tracebacks in the terminal.
8. The checkpoint PR from the owner's long-lived branch is merged to `main`, then the other member syncs their own branch.

---

## 12. Behaviour rules for AI agents

1. **Inspect first.** List the directory, read existing files, and reuse existing code before creating new files.
2. **Stay in your lane.** Edit only files owned by the member who gave you the prompt. If you need a change elsewhere, say so in your final report instead of editing.
3. **Build, run, test, fix.** Start the app, hit the routes (browser or `curl`/PowerShell `Invoke-RestMethod`), run `pytest`, and fix runtime errors before reporting.
4. **Be honest.** Report real command output. If something is blocked or partially done, say exactly what.
5. **Small, reviewable steps.** Prefer several focused commits to one giant one.
6. **Keep the UI simple.** If you are tempted to add decoration, don't.
7. **Windows first.** Use PowerShell-compatible commands in docs and scripts.
8. **Final report format:** files created/changed, commands run, test summary, what the human should manually check in the browser, open issues.
