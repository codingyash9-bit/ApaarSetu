# PROMPTS — MEMBER A (Data, Security & Prevent)

14 prompts, run in order (A0 → A13). Paste each into your AI coding agent (Claude Code / Cursor / Codex) from the repo root.

**How to use**
1. Start every prompt with the **Common Header** below (copy it once into the agent's session or paste it each time).
2. After each prompt: run the app, click through, run `pytest -q`, commit to the existing `member-a` branch. Do not create per-prompt branches or open per-prompt PRs.
3. If the agent says something is blocked on Member B, use a stub and move on (see STEPS.md section 4).

---

## COMMON HEADER (prepend to every prompt)

```text
You are working on APAAR Nexus (Smart India Hackathon PS 26263) in the repository in the current directory.
I am Member A (Data, Security & Prevent).

FIRST: read AGENTS.md and STEPS.md completely and follow them strictly (stack, folder ownership, shared contracts,
enums, response envelope, CSRF, security checklist, frontend rules).
Only edit files owned by Member A unless the task explicitly says otherwise. If you need a change in a Member B file,
do not edit it; list it in your final report.
Inspect the existing project first and reuse existing code. Do not create duplicate files.
All data is synthetic. Never claim integration with AICTE/APAAR/UIDAI/DigiLocker.
After implementing: start the app, exercise the feature (browser or PowerShell Invoke-RestMethod), run pytest,
fix every runtime error, then give a final report: files changed, commands run, REAL test output summary,
what I should manually click-test, open issues. Never claim tests passed unless you ran them.
Environment: Windows 11, PowerShell, Python 3.11+.
```

---

## EXECUTION AND MERGE-SAFETY RULES (apply to every prompt)

- Work only on the existing `member-a` branch (Tanmay). Never create a branch per task. Member B uses only `member-b`.
- Before editing, run `git status --short`, inspect `git branch --show-current`, read the target files, and fetch/merge `origin/main` using AGENTS.md. Stop if the working tree is dirty; do not discard user work.
- Implement the task in small, coherent changes. Preserve unrelated behavior and existing interfaces. Do not regenerate or overwrite files wholesale when a focused edit is possible.
- For shared files, follow AGENTS.md ownership. Do not edit Member B's files; do not edit `routes/__init__.py` beyond adding your own blueprint registration line. Coordinate any cross-owner contract change before coding.
- Keep exactly four seeded login accounts and three institutions as defined in AGENTS.md. Never reintroduce legacy demo users/institutions.
- Add/update tests for happy paths, validation failures, authorization boundaries, idempotency and relevant regressions. Run focused tests first, then `pytest -q`; report actual output only.
- Before committing, inspect `git diff --check`, `git diff --stat`, and `git status`. Never claim there are no conflicts without checking. Do not force-push, rebase shared history, or amend pushed commits.
- At the end of each prompt, report files changed, tests and commands actually run, remaining issues, and the exact commit command. Commit to `member-a`; do not open a per-prompt PR.

## A0 — Repository bootstrap and app factory

```text
TASK A0: Bootstrap the project skeleton so both teammates can start working immediately.

Create (if not already present) the exact folder structure from AGENTS.md section 4, with empty __init__.py files
where needed, plus:
1. requirements.txt with sensible pinned versions: Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF, pydantic,
   pandas, rapidfuzz, cryptography, qrcode[pil], pytest, python-dotenv, Werkzeug.
2. .env.example: SECRET_KEY, DATABASE_URL (sqlite:///instance/apaar_nexus.db), FLASK_ENV, DEMO_PASSWORD,
   MAX_UPLOAD_MB=2, MAX_CSV_ROWS=5000, SIGNING_KEY_DIR=instance/keys, SESSION_COOKIE_SECURE=false.
3. .gitignore: .venv, __pycache__, .env, instance/*.db, instance/keys/, *.pyc, .pytest_cache.
4. config.py: Config, DevelopmentConfig, TestingConfig (in-memory SQLite, CSRF configurable), ProductionConfig
   (refuses to start if SECRET_KEY is missing or default). Load from .env via python-dotenv.
5. extensions.py: db, login_manager, csrf (CSRFProtect).
6. app.py: create_app(config_name) factory. Registers extensions, calls routes.register_all(app), registers JSON
   error handlers returning the envelope from AGENTS.md 5.6 (401,403,404,409,422,429,500), sets secure session cookie
   options (HttpOnly, SameSite=Lax), sets MAX_CONTENT_LENGTH from env, adds a context processor exposing app name and
   the synthetic-data banner text. Include `if __name__ == "__main__": app.run(debug=True)` with a comment that this is
   the development server only.
7. routes/__init__.py with register_all(app) that imports and registers each blueprint inside try/except ImportError
   guarded blocks ONLY while modules do not exist yet; one line per blueprint so merges are trivial.
8. routes/health.py (or inside app.py): GET /api/health returning ok + app version + "synthetic data only".
9. services/audit_service.py with a WORKING log(actor, action, entity_type, entity_id, details=None, institution_id=None)
   function. For now it can print to the logger; A1 will persist it. Keep the signature exactly as in AGENTS.md 5.9.
10. A minimal README.md stub (title, disclaimer, run commands). Do not write the final README.
11. instance/.gitkeep, docs/ folder with empty API.md, DB_SCHEMA.md.

Then: create a venv, install requirements, start the app, call /api/health, and confirm the error handlers return
JSON for an unknown URL. Commit with message "bootstrap: app factory, config, error handlers".
Tell me the exact git commands to push so Member B can pull.
```

---

## A1 — Database models (all tables, including Member B's)

```text
TASK A1: Implement ALL SQLAlchemy models in models/ (one module per area, exported in models/__init__.py).
You own models for both members so that nobody is blocked. Use UUID string primary keys (default=lambda: str(uuid.uuid4())),
created_at/updated_at mixin, proper ForeignKeys, UniqueConstraints, and indexes on every column used for lookup/filter.

Tables and key fields (extend sensibly, keep names):
- users: id, username (unique), password_hash, full_name, role (enum), institution_id (nullable FK), student_id (nullable FK), is_active.
- institutions: id, code (unique), name, state, city, is_synthetic (default True), status, created_at.
- programmes: id, institution_id, code, name, level.   Unique (institution_id, code).
- intake_capacities: id, institution_id, programme_id, academic_year (e.g. "2026-27"), approved_regular_intake,
  supernumerary_capacity, category_rules (JSON: which categories may use REGULAR vs SUPERNUMERARY seats),
  UNIQUE(institution_id, programme_id, academic_year).
- student_records: id, institution_id, programme_id, institution_student_id, apaar_ref (indexed, NOT unique),
  full_name, normalized_name (indexed), academic_year, admission_date, admission_category, classification,
  is_nri, is_oci, is_foreign_national, enrolment_status, validation_status, validation_notes,
  contact_ref (indexed, NOT unique), fee_payer_ref (indexed, NOT unique), source_submission_id, is_synthetic.
  UNIQUE(institution_id, institution_student_id, academic_year).
- student_record_history: id, student_id, changed_by, changed_at, field, old_value, new_value, reason.
- admission_events: id, institution_id, programme_id, academic_year, student_id (nullable), category, classification,
  result (ACCEPTED/REJECTED), reason_code, message, actor_id, created_at.
- data_submissions: id, reference (SUB-YYYYMMDD-XXXXXX unique), institution_id, uploaded_by, filename, file_sha256,
  status, total_rows, valid_rows, error_rows, created_at, committed_at.  UNIQUE(institution_id, file_sha256) for idempotency.
- submission_errors: id, submission_id, row_number, field, code, message, raw_row (JSON).
- identity_matches: id, student_a_id, student_b_id, match_type, confidence, evidence (JSON), scan_id, event_key (unique per scan run logic).
- identity_graph_edges: id, source_type, source_id, target_type, target_id, edge_type, explanation (text, NOT NULL), evidence (JSON).
- risk_cases: id, reference (CASE-XXXXXX unique), institution_id (nullable), score, severity, status, assigned_to, recommended_action,
  summary, opened_at, updated_at.
- risk_evidence: id, case_id, rule_key, points, event_key, description, related_student_ids (JSON), details (JSON). Unique (case_id, event_key).
- case_actions: id, case_id, actor_id, action, from_status, to_status, note, created_at.
- credentials: id, reference (CRED-XXXXXX unique), student_id, institution_id, programme_name, award_year, issue_date,
  expires_at (nullable), payload_json (canonical JSON text that was signed), signature (base64), key_id, status_stored (ISSUED/REVOKED),
  revoked_at, revoked_by, revoke_reason.
- signing_keys: id, key_id (unique), public_key_pem, algorithm ("Ed25519"), created_at, is_active, is_development_key (bool). NEVER store the private key here.
- consent_records: id, student_id, claims (JSON list), created_at.
- sharing_sessions: id, student_id, credential_id, consent_id, token_hash (unique, SHA-256), token_prefix (first 6 chars only),
  claims (JSON), expires_at, revoked_at, created_at, access_count, last_accessed_at.
- verification_events: id, credential_id (nullable), sharing_session_id (nullable), result, verifier_user_id (nullable), ip_hash, created_at.
- audit_logs: id, actor_id, actor_role, action, entity_type, entity_id, institution_id, details (JSON), created_at (indexed).
- system_policies: id, key (unique), value (JSON), description, updated_by, updated_at.

Use Python enums stored as strings, with the exact values from AGENTS.md 5.3.
Also:
1. Make services/audit_service.log persist to audit_logs (never store secrets in details).
2. Add db.create_all() helper in a function init_db(app) used by app.py and seed.py (no migrations needed).
3. Write docs/DB_SCHEMA.md with a table list, relationships, and a simple text ERD.
4. Add tests/conftest.py (app fixture with TestingConfig, empty DB, client fixture) and a smoke test that creates one row in each table.
5. Verify SQLite foreign keys are enabled (PRAGMA foreign_keys=ON via event listener).

Run pytest, then commit "models: all tables". Tell Member B immediately when merged (they are waiting for it).
```

---

## A2 — Authentication, RBAC and institution scoping

```text
TASK A2: Implement authentication, role-based access control and institution-level authorization.

Backend:
1. routes/auth.py: POST /api/auth/login (username, password), POST /api/auth/logout, GET /api/auth/me.
   Use Flask-Login, werkzeug.security password checks, session protection "strong", and return the standard envelope.
   Also provide HTML routes: GET /login (page), GET / (redirect to the role's home: AICTE_ADMIN -> /dashboard,
   INSTITUTION_ADMIN -> /dashboard, STUDENT -> /passport, VERIFIER -> /verify-console).
2. services/authz.py:
   - decorator roles_required(*roles) -> 401 JSON for API/redirect for pages when unauthenticated, 403 when wrong role.
   - helper current_institution_id() and scope_query(query, model): AICTE_ADMIN sees everything; INSTITUTION_ADMIN
     is restricted to own institution_id; STUDENT restricted to own student record; others see nothing unless explicitly allowed.
   - helper assert_same_institution(obj) that raises a 403 (envelope FORBIDDEN) if an institution admin touches another institution's row.
3. Simple login rate limiting (in-memory counter by username+IP, 5 failures -> 429 for 60 seconds). Keep it simple and documented.
4. Audit-log every login success, login failure (without the password), and logout.
5. user_loader, unauthorized handler (JSON for /api/*, redirect to /login for pages).
6. Inactive users cannot log in.

Frontend (use Member B's base.html if it exists in main; otherwise create a minimal login.html that extends base.html later):
- templates/login.html: centred card, username + password, submit through the api() wrapper (static/js/app.js), error shown inline
  and as a toast. Show the demo accounts table ONLY when config SHOW_DEMO_ACCOUNTS is true (default true in development, false in production).
- Keep it simple and clean per AGENTS.md section 7.

Tests (tests/test_auth.py):
- login success/failure, inactive user, logout, /me, rate limiting,
- unauthenticated API call -> 401 JSON, wrong role -> 403 JSON,
- institution admin cannot read another institution's student (once students exist, test with a direct model query + scope_query),
- password is never present in any response.

Commit "auth: login, rbac, scoping".
```

---

## A3 — Seed script part 1 (users, institutions, programmes, policies)

```text
TASK A3: Create seed.py (deterministic) — PART 1: reference data. Part 2 (students and scenarios) comes in A4.

Requirements:
1. CLI: `python seed.py` (seed if empty), `python seed.py --reset` (drop all tables, recreate, seed). Refuse --reset when
   FLASK_ENV=production unless env ALLOW_DEMO_RESET=true. Use argparse. Print a clear summary of what was created.
2. Use random.Random(42) everywhere so output is identical every run. No uuid4 randomness for business identifiers that appear
   in the demo (use uuid5 with a fixed namespace, or deterministic reference generators), so re-seeding gives stable references.
3. Institutions (exactly three, all clearly labelled synthetic with is_synthetic=True):
   - VESIT (code VESIT) — primary demo institution
   - COEP (code COEP)
   - VJTI (code VJTI)
   Do not seed Pune/Nagpur/Delhi/Chennai or any fourth institution.
4. Programmes: at least B.Tech Information Technology, B.Tech Computer Engineering, B.Tech Electronics, Diploma Mechanical (spread across institutions).
5. intake_capacities for academic years 2024-25, 2025-26, 2026-27. VESIT / B.Tech IT / 2026-27:
   approved_regular_intake=120, supernumerary_capacity=10. Other institutions get different utilisation targets (planned in A4):
   one near 80%, one near 90%, one at 100%, one low (~50%).
   category_rules JSON example: {"REGULAR": ["OPEN","OBC","SC","ST","EWS"], "SUPERNUMERARY": ["NRI","OCI","FN"]}.
   Make NRI/OCI/FN eligible for SUPERNUMERARY only by default, and document that this is a configurable prototype rule.
6. system_policies rows: apaar_regex ("^\\d{12}$"), risk_weights (from AGENTS.md 5.5), capacity_warning_thresholds ([80,90,100]),
   risk_bands, max_upload_mb, sharing_allowed_expiry_hours ([24,72,168]), credential_default_validity_years.
7. Users: the four demo accounts from AGENTS.md 5.2: AICTE_Admin, VESIT, COEP and VJTI with Werkzeug hashes (password from DEMO_PASSWORD env, default only in non-production).
   Do not create student, verifier or auditor login accounts. Link demo credential examples directly to seeded synthetic student records, not to a student login.
8. signing_keys: generate (or load) a development Ed25519 key pair into SIGNING_KEY_DIR (instance/keys, git-ignored). Store only
   the public key + key_id in the DB. Write a small helper services/key_store.py: load_private_key(), get_active_key_id(). Never log the key.
   (Member B's credential_service will use this helper; document its interface in docs/DB_SCHEMA.md or a code docstring.)
9. Call hooks at the end: seed_students(...) (A4) and, if present, seed_b.seed_prove_and_detect(db) (Member B). Use try/except ImportError
   with a clear message so seeding works before B's file exists.

Tests: tests/test_seed.py — seeding twice with --reset produces identical institution codes, user list, and policy values;
no plaintext password stored; exactly 3 institutions (VESIT, COEP, VJTI) and exactly 4 demo users exist; all defined role enums remain supported in authorization code even though only AICTE_ADMIN and INSTITUTION_ADMIN accounts are seeded.

Commit "seed: reference data".
```

---

## A4 — Seed script part 2 (students and scenarios)

```text
TASK A4: Extend seed.py with synthetic student data and the demo scenarios. Everything deterministic (Random(42)).

Generate at least 150 student_records (aim for ~330 so the dashboards look alive), across institutions, programmes, and the years
2024-25, 2025-26, 2026-27. Every record is_synthetic=True. Names must be obviously synthetic Indian-style names from a fixed list
(no real people). APAAR refs: 12-digit synthetic numbers generated deterministically (use a clearly documented range, e.g. start with 9
to mark them synthetic). Contact refs look like "SYN-C-0001" style normalized tokens, fee-payer refs like "SYN-F-0001".

Required scenarios (document each in docs/DEMO_SCRIPT.md-ready comments in the seed file and print a summary table at the end):
1. VESIT / B.Tech IT / 2026-27: exactly 116 REGULAR admissions and 4 SUPERNUMERARY admissions (NRI/OCI/FN mix).
   Remaining regular = 4, remaining supernumerary = 6.
2. Utilisation spread for 2026-27 in other institutions/programmes: one at ~80%, one ~90%, one exactly 100% (full), one ~50%.
3. Two excess-admission test scenarios: (a) a programme exactly at 100% so any new REGULAR admission must be rejected;
   (b) a programme with 1 regular seat left so two concurrent requests are the concurrency test. Also write rows in
   admission_events with result=REJECTED for two past excess attempts (with reason_code CAPACITY_EXCEEDED).
4. Three duplicate/conflicting identity scenarios:
   (a) same apaar_ref at two institutions in the same academic year with ACTIVE status (simultaneous enrolment),
   (b) same apaar_ref twice in one institution with different institution_student_id (duplicate APAAR),
   (c) similar name (spelling variation, e.g. "Rahul Sharma" / "Rahul Sarma") + same date of admission/programme but different APAAR.
5. Two LEGITIMATE shared-contact scenarios: siblings sharing a parent's contact ref; two students from the same sponsor sharing a fee-payer ref.
   They must exist but must NOT be duplicates (different names, different APAAR).
6. A handful of invalid/missing APAAR refs flagged validation_status=INVALID.
7. at least one eligible synthetic VESIT student record exists for credential demos; no student login account is created.
8. Run validation_service later (A6) — for now set validation_status directly but through a single function so A6 can replace it.

Also create sample_data/students.csv (valid template, ~25 rows for VESIT) and sample_data/students_demo_upload.csv
which contains: valid rows, an in-file duplicate, an existing-database duplicate, malformed APAAR rows, a bad category, a wrong programme code,
and one conflicting enrolment (same APAAR already enrolled at another institution). Add a comment-free header row; document columns in docs/DB_SCHEMA.md.

Tests: counts match the scenario list (116/4, 100% programme, at least one eligible VESIT record for credential demos); re-seeding is identical.
Commit "seed: students and scenarios".
```

---

## A5 — Institutions, programmes and policy settings (API + pages)

```text
TASK A5: Institution directory, programme/intake configuration and system policy settings.

API (routes/institutions.py, standard envelope, pagination, validation):
- GET /api/institutions (filters: q, state, status; AICTE_ADMIN/AUDITOR see all, INSTITUTION_ADMIN sees only own)
- POST /api/institutions (AICTE_ADMIN)
- GET /api/institutions/<id>   (includes programmes + intake summary)
- PATCH /api/institutions/<id> (AICTE_ADMIN any; INSTITUTION_ADMIN only limited fields of own institution)
- GET/POST/PATCH /api/institutions/<id>/programmes and /api/institutions/<id>/capacities (AICTE_ADMIN can create/update intake and
  category rules; INSTITUTION_ADMIN read-only). Validate: approved intake >= 0, supernumerary >= 0, unique per (programme, year),
  cannot reduce approved intake below current admissions (return CONFLICT with explanation).
- GET /api/policies, PATCH /api/policies/<key> (AICTE_ADMIN only; validate value shapes: thresholds ascending list of ints <= 100,
  risk weights non-negative ints, expiry list subset of {24,72,168}, apaar_regex compiles). Audit every change with old/new values.

Pages (extend base.html from Member B; keep simple and clean):
- templates/institutions.html + static/js/institutions.js: searchable table (code, name, state, programmes, status), row click opens a side
  panel/section with programmes and capacities. Add/Edit forms in plain <dialog>. AICTE_ADMIN sees edit buttons; others do not.
- templates/policies.html: AICTE_ADMIN only, one card per policy with validation errors shown inline.

Tests: institution admin cannot read/patch another institution (403), cannot edit policies, capacity cannot be reduced below
current admissions, invalid policy values rejected, audit entries created.
Commit "institutions: directory, capacities, policies".
```

---

## A6 — APAAR adapter and validation service

```text
TASK A6: Build the mock APAAR adapter and the central validation service.

services/apaar_adapter.py:
- validate_format(ref) -> (bool, reason) using the apaar_regex policy (default 12 digits). Strip spaces; reject letters, wrong length, empty.
- mask_apaar(ref) -> "XXXXXXXX1234" (last 4 only). Handles None/short input safely. This is THE masking function used everywhere.
- mock_verify(ref) -> dict {"status": "MOCK_VERIFIED"|"MOCK_NOT_FOUND"|"MOCK_UNAVAILABLE", "source": "MOCK — not connected to any government system"}.
  Deterministic rule (documented in docstring): refs starting with "9" are MOCK_VERIFIED, refs ending in "0000" are MOCK_NOT_FOUND, otherwise MOCK_UNAVAILABLE.
  Do NOT invent any official APAAR checksum algorithm. Add a module docstring that clearly separates "format check" from "identity verification".

services/validation_service.py:
- Pydantic model (or equivalent) StudentInput with all required fields from the master spec: institutional student ID, APAAR ref, name,
  institution, programme, academic year (format YYYY-YY and consecutive years), admission date (valid, not in the future, not before 2000),
  admission category (enum), classification (enum), NRI/OCI/FN flags (bool parsing: yes/no/true/false/1/0), enrolment status (enum),
  optional contact_ref, optional fee_payer_ref.
- validate_student_row(row, context) -> ValidationResult(valid, errors=[{field, code, message}], warnings=[...], normalized=dict).
  Rules: required fields; APAAR format; programme exists in institution; academic year has a capacity row; category/classification
  consistent with category_rules (e.g. NRI cannot be REGULAR if rules forbid it) and consistent with the NRI/OCI/FN flags;
  duplicate institution_student_id within institution+year; duplicate APAAR within the same institution+year (error) and across
  institutions (WARNING that is passed to identity scan, not a hard rejection).
- normalize_name(name): lowercase, strip accents/punctuation/extra spaces, collapse initials. Store as normalized_name.
- Never silently accept invalid records: every failure produces an error with a stable code (MISSING_FIELD, APAAR_FORMAT, BAD_CATEGORY,
  UNKNOWN_PROGRAMME, DUPLICATE_STUDENT_ID, DUPLICATE_APAAR_IN_INSTITUTE, BAD_DATE, BAD_YEAR, CATEGORY_CLASSIFICATION_MISMATCH).
- Make the validation reusable by manual entry (A7), CSV (A8), and admissions (A9).

Tests (tests/test_students.py part 1 or tests/test_validation.py): each error code is triggered by a targeted row; mask_apaar behaviour;
mock_verify rules; flags parsing; cross-institution duplicate yields a warning not an error.
Commit "validation: apaar adapter and rules".
```

---

## A7 — Student records: CRUD, change history, repository and detail pages

```text
TASK A7: Central student repository with manual entry, updates and change history.

API (routes/students.py):
- GET /api/students — pagination + filters: academic_year, institution_id, programme_id, category, classification, validation_status,
  enrolment_status, q (name / institutional ID / masked APAAR search). Scope: institution admin sees only own institution.
  Responses show APAAR MASKED by default; AICTE_ADMIN and INSTITUTION_ADMIN (own) may request full value with ?reveal=true but
  that action is audit-logged. Students and verifiers never get the full value.
- POST /api/students — manual entry using validation_service. Returns row-level errors with VALIDATION_ERROR. Admissions that
  consume a seat MUST go through the seat ledger (A9). For now, create the record in a transaction and leave a clearly marked
  `seat_ledger.commit_admission` integration point; wire it fully in A10.
- GET /api/students/<id> — details + history + validation notes + linked risk case references (read-only list; just IDs and severities).
- PATCH /api/students/<id> — update allowed fields; writes student_record_history rows (old/new/changed_by/reason) in the same
  transaction; re-validates; re-runs identity scan hook if B's service exists (guarded import).
- GET /api/students/export — CSV export of the filtered list (masked APAAR; same scope rules; audit-logged).

Pages:
- templates/students.html + static/js/students.js: filter bar (year, institution [AICTE only], programme, category, validation status),
  compact table, pagination, "Add student" dialog with inline validation messages, "Export CSV" button.
- templates/student_detail.html: profile card, validation notes, change history timeline (plain list), linked risk cases (links),
  edit dialog (reason required). Use the shared helpers from app.js. Keep the UI simple.

Tests (tests/test_students.py): create valid student; invalid APAAR rejected with row error; update writes history with old/new; institution
admin cannot read/update another institution's student; masked APAAR by default; reveal is audit-logged; export respects scope.
Commit "students: repository, history, pages".
```

---

## A8 — CSV ingestion pipeline and upload wizard

```text
TASK A8: CSV upload pipeline with preview, validation, row-level errors, idempotency, and a 3-step wizard UI.

services/csv_service.py (use pandas only if useful; otherwise csv module):
1. Documented template: exact header names and order (put in sample_data/students.csv and in a /api/students/import/template download route).
   Accept header aliases only through an explicit alias map (document it); unknown required columns -> clear error, not silent skip.
2. preview(file, institution_id) -> parses up to MAX_CSV_ROWS, validates every row with validation_service, returns summary
   (total, valid, errors, warnings) plus first 50 rows with per-row status. Preview must NOT write student rows.
   It may create a data_submissions row with status PREVIEWED storing file_sha256.
3. commit(submission_id) -> in ONE transaction inserts all VALID rows, records submission_errors for invalid rows (row number, field, code,
   message, raw row), updates counts, sets status COMMITTED/PARTIAL/REJECTED, generates reference SUB-YYYYMMDD-XXXXXX, audit-logs it.
   Rows that would consume seats go through seat_ledger.precheck/commit (A9) once available; until then guard with a clear TODO.
   After commit, call services.identity_resolution.scan(submission_id=...) if available (guarded import) — do not crash if it is missing.
4. Idempotency: if the same institution uploads a file with the same SHA-256 (or the same row content hash), do not create duplicate
   students; return the existing submission reference with message "already imported". Row-level idempotency: same
   (institution, institution_student_id, academic_year) with identical data -> skipped as UNCHANGED, with different data -> reported as an update
   candidate (do not overwrite silently; require an `update_existing=true` option which writes history).
5. Duplicate CSV submission detection is an identity-risk signal: record it so B's risk engine can pick it up (store a flag in
   data_submissions.details JSON or an audit event DUPLICATE_SUBMISSION).
6. Error report download: CSV with original row number, original values, error code, error message. Route:
   GET /api/students/import/<submission_id>/errors.csv (scope-checked).
7. Upload limits: .csv only, size limit, UTF-8 (with BOM tolerance), max rows, reject formulas starting with = + - @ in text cells
   (CSV injection) by prefixing a single quote in exports and flagging on import.

Routes (routes/students.py): POST /api/students/import (multipart; fields: file, mode=preview|commit, submission_id for commit),
GET /api/students/import/history (submission history, scoped), GET /api/students/import/<id>.

Page templates/upload.html + static/js/upload.js — a simple 3-step wizard: (1) choose file + download template link, (2) preview with
counts, error table with row numbers and messages, (3) confirm commit -> show submission reference, counts, and "Download error report".
Show submission history table at the bottom. All buttons real. Toasts for success/failure.

Tests (tests/test_students.py or tests/test_csv.py): valid import; invalid APAAR rows reported with row numbers; in-file duplicates;
cross-institution conflict row accepted with warning (and flagged for scan); re-uploading the same file is idempotent (no new rows);
changed row without update flag is not overwritten; oversized/non-CSV rejected; error report content; institution admin cannot import into another institution;
CSV injection cells neutralised.
Commit "csv: ingestion pipeline and wizard".
```

---

## A9 — Seat ledger engine (rules, transactions, concurrency)

```text
TASK A9: Implement services/seat_ledger.py — the Prevent engine. No UI yet (A10).

Requirements:
1. Data model use: intake_capacities (approved_regular_intake, supernumerary_capacity, category_rules), student_records
   (classification, category, enrolment_status), admission_events.
2. Functions (all return plain dicts / dataclasses, never raw ORM objects):
   - get_summary(institution_id, programme_id, academic_year) -> approved_regular, regular_admitted, regular_remaining,
     supernumerary_capacity, supernumerary_admitted, supernumerary_remaining, utilisation_pct (regular), supernumerary_utilisation_pct,
     warning_level (None/80/90/100 from policy), category_breakdown (per category counts).
     Count only ACTIVE (and GRADUATED if same year) students towards seats; WITHDRAWN frees a seat — document the rule.
   - precheck(payload) -> {allowed: bool, reason_code, message, summary_after}. Applies explicit category eligibility:
     determine target pool (REGULAR vs SUPERNUMERARY) from category_rules and the NRI/OCI/FN flags; reject if the category
     is not allowed in the requested pool (reason_code CATEGORY_NOT_ELIGIBLE with explanation). Regular and supernumerary capacity
     are NEVER mixed or borrowed from each other.
   - commit_admission(payload, actor) -> within ONE DB transaction: re-check capacity under a lock, create/attach the student record,
     create an admission_events row ACCEPTED, audit-log. On failure create a REJECTED admission_events row (reason_code, human explanation like
     "Approved regular intake is 120 and 120 regular admissions already exist; admission 121 was blocked") and audit-log it, then raise
     CapacityExceeded (route returns 409 CAPACITY_EXCEEDED). Rejected attempts are persisted even though the admission is not.
   - Duplicate-admission prevention: same institution + student ID + year, or same APAAR already actively admitted in the same
     institution/programme/year -> reason_code DUPLICATE_ADMISSION.
3. Concurrency: on SQLite use `BEGIN IMMEDIATE` (via SQLAlchemy connection event / session execute) or an atomic conditional update on a
   counter row so two simultaneous requests for the last seat cannot both succeed. Prefer a conditional UPDATE on an
   `admitted_regular` / `admitted_supernumerary` counter column in intake_capacities (add the columns in models if needed, coordinating with the A1 owner = you)
   kept consistent with student_records; add a reconcile function recompute_counters() and a test proving counters match records.
4. After a rejected excess attempt call services.risk_engine.record_excess_intake_event(event) if available (guarded import; B will implement).
5. Thresholds: read 80/90/100 from system_policies (not hard-coded).
6. Admin-configurable rules: functions read category_rules from the DB so changes in A5 take effect without code change.

Tests (tests/test_seat_ledger.py): within capacity accepted; exactly at 120 -> 121st REGULAR rejected with explanation and a REJECTED event;
supernumerary accepted until 10, 11th rejected; NRI cannot take a REGULAR seat if rules forbid it; regular full does not allow
spilling into supernumerary; WITHDRAWN frees a seat; duplicate admission blocked; concurrency test with threads (two threads race for the
last seat -> exactly one ACCEPTED); counters reconcile; thresholds produce warning levels 80/90/100; demo scenario numbers (116/120, 4/10) hold after seeding.
Commit "seat-ledger: engine and concurrency".
```

---

## A10 — Admissions API and Seat Ledger page

```text
TASK A10: Expose the seat ledger through the API and build the Seat Ledger page.

API (routes/admissions.py):
- GET /api/seats/summary?academic_year=&institution_id=&programme_id= — list of programme summaries (scope-aware).
- GET /api/seats/ledger — detailed per-programme ledger with category breakdown (same filters).
- POST /api/admissions/precheck — body: student fields + programme + year + category + classification + flags. Returns allowed/not allowed
  with message and summary_after. Does not write anything (but audit-logs the precheck if rejected).
- POST /api/admissions — commit via seat_ledger.commit_admission. 201 on success; 409 CAPACITY_EXCEEDED / DUPLICATE_ADMISSION /
  CATEGORY_NOT_ELIGIBLE with clear explanation in message and details.
- GET /api/admissions/events — paginated admission history including rejected attempts; filters: result, institution, year, programme.
Wire A7's POST /api/students and A8's CSV commit to use the ledger (seat-consuming admissions must go through commit_admission).

Page templates/seat_ledger.html + static/js/seat-ledger.js:
- Filters (academic year, institution [AICTE only], programme).
- Summary cards for the selected programme: Approved regular, Admitted regular, Remaining, Supernumerary approved/admitted/remaining.
- A utilisation bar (plain HTML/CSS bar, with colour change at 80/90/100 thresholds and a text warning badge).
- Category-wise table.
- "Admission pre-check" form: student ID, name, APAAR, category, classification, flags -> shows ALLOWED / BLOCKED with the explanation,
  and a "Commit admission" button that is only enabled after an allowed pre-check and posts to /api/admissions. A blocked attempt
  shows the server's explanation in a red panel and appears in the history immediately.
- Admission history table (including rejected attempts, with reason code).
- Pre-filled demo helper (a small "Fill demo values" link) so you can reproduce "VESIT / B.Tech IT / 2026-27: 116 + 4" quickly;
  to demo the block, include in docs a recipe that fills the remaining 4 regular seats then attempts the 121st.

Tests: API-level tests for precheck + commit + 121st rejection response shape, scope (COEP cannot admit into VESIT), events list shows rejected
attempt, audit entries exist.
Commit "seat-ledger: api and page".
```

---

## A11 — Audit service, audit log page, institution dashboard, enrolment report

```text
TASK A11: Finish auditing and the institution-facing dashboard and report.

1. Audit:
   - Review that every mutating action in routes/services uses audit_service.log. Add missing calls (login, student create/update/import,
     admissions, policy changes, institution edits, reveal-APAAR, exports).
   - GET /api/audit-logs (AICTE_ADMIN and AUDITOR all; INSTITUTION_ADMIN own institution only), pagination, filters: actor, action,
     entity_type, date range, institution. Make audit rows append-only in code (no update/delete function exists) and document that.
   - templates/audit_logs.html: table with filters, expandable details (JSON pretty printed, sanitised: mask APAAR anywhere it appears).
2. Institution dashboard (routes/dashboards.py — institution part only, GET /api/dashboard/institution):
   approved intake, actual admissions, remaining seats, category-wise capacity, utilisation %, submission history (last 10),
   validation error counts by code, pending identity checks (validation_status PENDING/FLAGGED), institutional risk cases (count by severity,
   read via the risk_cases table; tolerate an empty table), credential issuance history (last 10). Filters: academic year, programme,
   category, validation status, risk level. ALL numbers come from the API; none hard-coded.
   Member B owns dashboard.html and dashboard.js — coordinate: you only deliver the JSON contract. Write the response shape into docs/API.md
   and message Member B. If dashboard.js is not ready, provide a tiny temporary JSON viewer page, not a duplicate dashboard.
3. Enrolment report: GET /api/reports/enrolment (JSON) and GET /api/reports/enrolment.csv (download): institution, programme, year,
   approved intake, admitted, remaining, utilisation, supernumerary figures, category counts. Scope-aware. Keep the CSV clean (no comment rows)
   and put "SYNTHETIC" in the filename (e.g. enrolment_report_SYNTHETIC_2026-27.csv). Audit-log exports.
4. Demo reset: POST /api/admin/demo-reset (AICTE_ADMIN only, disabled in production unless ALLOW_DEMO_RESET=true) that re-runs the seed in a safe way
   with a confirmation token in the body; audit-logged. Add a button on policies.html behind a confirm dialog (reuse B's confirm helper).

Tests (tests/test_audit.py): audit rows exist for login, student create, admission rejected, policy change; institution admin sees only own audit rows;
no secrets/full APAAR in details; dashboard JSON scope; enrolment CSV scope and filename; reset blocked for non-admin.
Commit "audit: logs, institution dashboard api, enrolment report".
```

---

## A12 — Automated tests for all Member A modules

```text
TASK A12: Test consolidation and gaps for Member A's modules.

1. Review tests/ and conftest.py. Provide fixtures: app, client, db, and logged-in clients for each role (AICTE_Admin, VESIT, COEP,
   student, verifier, auditor) using the seeded or minimal data. Keep fixtures fast (in-memory SQLite, small dataset).
2. Make sure these areas exist and pass (add what is missing):
   - test_auth.py: login/logout/me, wrong password, inactive user, role redirects, rate limit, 401/403 shapes, CSRF required on POST when enabled
     (add one test with CSRF enabled).
   - test_students.py: CRUD, invalid APAAR, duplicate detection, history, scope isolation, export.
   - test_csv.py: preview vs commit, errors with row numbers, idempotent import, update-existing flag, injection cells, limits, error report.
   - test_seat_ledger.py: within capacity, at capacity, 121st rejection, supernumerary, category eligibility, concurrency, threshold warnings, counters reconcile.
   - test_audit.py: audit coverage + secrets not logged.
   - test_seed.py: determinism.
3. Add a "contract test" tests/test_envelope.py that hits several endpoints and asserts the response envelope (ok/data/meta/error) and that error
   responses never contain a traceback.
4. Run `pytest -q` and `pytest -q -p no:randomly` if randomly is installed. Fix flaky tests. Print the REAL summary line.
5. Add a short "How to run tests" section to README.md (only that section).

Commit "tests: member A coverage".
```

---

## A13 — Hardening and integration

```text
TASK A13: Security review and cross-module integration for Member A's area. Do not add new features.

1. Integration:
   - Confirm CSV commit and manual student creation trigger services.identity_resolution.scan(...) after commit (Member B's service) and that failures
     in the scan never break the import (log + audit, continue).
   - Confirm excess-intake rejections call risk_engine.record_excess_intake_event and that the resulting risk case appears in /api/risk/cases.
   - Confirm student detail page links to risk cases and credentials created by Member B.
2. Security review against AGENTS.md section 8. Produce docs/SECURITY_REVIEW_A.md listing each check, the result, and fixes applied:
   - every route has login + role decorators (write a test that enumerates app.url_map and fails on any /api route lacking auth, except
     /api/auth/login, /api/health, and the two public verify routes),
   - institution isolation on every institution-scoped query,
   - upload limits, file type, CSV injection,
   - CSRF on mutating routes,
   - session cookie flags, logout invalidation,
   - error handlers never leak stack traces (try forcing a 500 in a test with a debug flag off),
   - no secrets in logs (grep tests for private key, token, password in log output),
   - SQL: only ORM / bound parameters.
3. Performance sanity: add indexes where list endpoints are slow with 300+ students (EXPLAIN a couple of queries), avoid N+1 in /api/students.
4. Final manual walkthrough as AICTE_Admin, VESIT and COEP: confirm COEP cannot see VESIT data through UI or API URLs typed by hand.
5. Update README.md sections owned by Member A: setup, seed/reset, CSV format and template, seat ledger rules (regular vs supernumerary), and known limitations
   for A's modules (e.g. mock APAAR, SQLite locking, in-memory rate limiter).

Run pytest -q and report the REAL output. Commit "hardening: member A".
```
