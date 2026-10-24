# PROMPTS — MEMBER B (UI Shell, Detect & Prove)

15 prompts, run in order (B0 → B14). Paste each into your AI coding agent (Claude Code / Cursor / Codex) from the repo root.

**How to use**
1. Start every prompt with the **Common Header** below.
2. After each prompt: run the app, click through, run `pytest -q`, commit to the existing `member-b` branch. Do not create per-prompt branches or open per-prompt PRs.
3. B0 and B1 do not need the database. Start them while Member A does A0/A1. For B2 onward, pull `main` first so you have the models.
4. If something from Member A is missing, write a stub using the agreed interface in AGENTS.md 5.9 and keep going.

---

## COMMON HEADER (prepend to every prompt)

```text
You are working on APAAR Nexus (Smart India Hackathon PS 26263) in the repository in the current directory.
I am Member B (UI Shell, Detect & Prove).

FIRST: read AGENTS.md and STEPS.md completely and follow them strictly (stack, folder ownership, shared contracts,
enums, response envelope, CSRF, security checklist, frontend rules).
Only edit files owned by Member B unless the task explicitly says otherwise. If you need a change in a Member A file
(models, auth, students, seat ledger), do not edit it; list it in your final report so I can ask Member A.
Inspect the existing project first and reuse existing code. Do not create duplicate files.
The frontend must be SIMPLE AND CLEAN (government portal look): navy + white, plain tables, text badges, no gradients, no icon fonts, no emoji, no heavy animation.
All data is synthetic. Never claim zero-knowledge proofs, blockchain, or integration with AICTE/APAAR/UIDAI/DigiLocker.
After implementing: start the app, exercise the feature in the browser (or PowerShell Invoke-RestMethod), run pytest,
fix every runtime error, then give a final report: files changed, commands run, REAL test output summary,
what I should manually click-test, open issues. Never claim tests passed unless you ran them.
Environment: Windows 11, PowerShell, Python 3.11+.
```

---

## EXECUTION AND MERGE-SAFETY RULES (apply to every prompt)

- Work only on the existing `member-b` branch (Yash). Never create a branch per task. Member A uses only `member-a`.
- Before editing, run `git status --short`, inspect `git branch --show-current`, read the target files, and fetch/merge `origin/main` using AGENTS.md. Stop if the working tree is dirty; do not discard user work.
- Implement the task in small, coherent changes. Preserve unrelated behavior and existing interfaces. Do not regenerate or overwrite files wholesale when a focused edit is possible.
- Follow AGENTS.md ownership. Do not edit Member A's files/models/auth/seed.py; coordinate model changes with A. In `routes/__init__.py`, add only your own blueprint registration line.
- Keep exactly four seeded login accounts and three institutions as defined in AGENTS.md. Do not add legacy demo users; use synthetic student records for credential examples and public read-only verification routes.
- Add/update tests for happy paths, validation failures, authorization boundaries, idempotency and relevant regressions. Run focused tests first, then `pytest -q`; report actual output only.
- Before committing, inspect `git diff --check`, `git diff --stat`, and `git status`. Never claim there are no conflicts without checking. Do not force-push, rebase shared history, or amend pushed commits.
- At the end of each prompt, report files changed, tests and commands actually run, remaining issues, and the exact commit command. Commit to `member-b`; do not open a per-prompt PR.

## B0 — Design system and base layout

```text
TASK B0: Build the visual foundation. No database needed. Keep it simple, clean and official-looking.

1. static/css/style.css implementing the design tokens from AGENTS.md section 7 as CSS variables, plus:
   - reset + typography (Segoe UI / system-ui, 14px base),
   - layout: fixed left sidebar (220px, navy), top bar (page title area + user name + role badge + logout button), main content area (max-width 1280px, padding 24px),
   - a 4px saffron/white/green strip at the very top of the page (three equal segments) — the only decoration,
   - components: .card, .card-header, .grid (2/3/4 column responsive), .stat (big number + label + small trend text), .btn (primary navy, secondary outline,
     danger), .badge variants (ok, warn, danger, info, muted — pale background + coloured text), .table (compact, sticky header, hover), .form-row/.input/.select/.textarea
     with label above, .field-error, .toast container (top right), dialog styling (native <dialog>), .pagination, .filter-bar, .empty-state, .progress (utilisation bar with
     colour classes for 80/90/100), .kv (key-value definition list), .tabs (simple).
   - responsive: sidebar collapses to a horizontal top menu below 900px; tables scroll horizontally inside a wrapper.
   - accessibility: visible :focus-visible outline, contrast >= 4.5:1, prefers-reduced-motion respected.
2. templates/base.html (Jinja2): head with csrf-token meta, style.css, vendor scripts loaded only on pages that request them via a {% block scripts %};
   sidebar menu built from the role -> menu mapping in AGENTS.md section 7 (use current_user.role; keep the menu definition in one Jinja macro or a Python
   context processor so it is easy to edit); active link highlighting; topbar; flash/toast container; footer banner:
   "Prototype — synthetic data only. Not connected to AICTE, APAAR, UIDAI or DigiLocker."; {% block content %}.
3. Download Chart.js (UMD min) and Cytoscape.js (min) into static/vendor/ using PowerShell Invoke-WebRequest from the official CDN URLs (pin the versions in a
   static/vendor/README.txt). Commit the files so the demo works offline. Do NOT add npm or node.
4. A temporary route /ui-kit (development only, guarded by app.debug) and template templates/ui_kit.html that renders every component once so we can eyeball the system.
   This page must be removed or disabled in production config.
5. Make sure a template that extends base.html renders correctly even when current_user is anonymous (login page uses a variant with no sidebar: add a
   {% block shell %} switch or a base_public.html).

If the Flask skeleton (A0) is not yet on main, create a minimal local app only to preview, and do NOT commit app.py/config.py changes. Commit "ui: design system and base layout".
```

---

## B1 — Shared JavaScript helpers

```text
TASK B1: Write static/js/app.js — the only shared JS file. Vanilla ES6+, no libraries, documented with short JSDoc comments.

Exports on a single global namespace `window.Nexus` (avoid polluting globals):
1. api(path, {method='GET', body, params, raw=false}) — fetch wrapper that: adds Accept JSON, adds X-CSRFToken from <meta name="csrf-token"> for non-GET,
   sends JSON bodies (or FormData untouched), builds query strings from params (skipping empty values), parses the envelope from AGENTS.md 5.6,
   throws an ApiError(code, message, details, status) when ok is false, handles 401 by redirecting to /login?next=..., and shows nothing by itself.
2. toast(message, type='info'|'ok'|'warn'|'danger', ms=4000) — accessible (aria-live="polite"), stacked, dismissible, short fade only.
3. confirmDialog({title, message, confirmText, danger}) -> Promise<boolean> using a single native <dialog> created on demand.
4. openDialog(id) / closeDialog(id) helpers for <dialog> forms.
5. renderTable(container, {columns:[{key,label,render?,align?}], rows, emptyText}) — builds a compact table safely (textContent / escaping — never innerHTML with data),
   supports cell render functions that return DOM nodes.
6. paginate(container, meta, onPage) — renders prev/next + "Page X of Y (N records)".
7. filterBar(container, fields:[{name,label,type:'select'|'text'|'date',options}], onChange) — builds a filter bar, returns {getValues(), setValues()}, debounces text inputs.
8. badge(text, kind) -> HTMLElement; statusBadge(value) mapping the enum strings in AGENTS.md 5.3 to colours (e.g. CRITICAL -> danger, HIGH -> danger,
   MEDIUM -> warn, LOW -> ok; VERIFIED -> ok, REVOKED -> danger, EXPIRED -> warn, INVALID -> danger).
9. fmtDate(iso), fmtDateTime(iso), fmtNumber(n), fmtPercent(n).
10. escapeHTML(str) and a small `el(tag, attrs, ...children)` DOM builder.
11. withButtonLock(button, asyncFn) — disables the button during the request and re-enables it afterwards (prevents double submits). No fake spinners.
12. loadFilters helpers that call /api/institutions, /api/seats/summary (programmes) etc. only if available; fail gracefully with a toast.

Add a small test page section to /ui-kit demonstrating: toast types, confirm dialog, table + pagination with fake in-memory data, filter bar.
Document usage in docs/FRONTEND.md (short, with 6-8 code snippets) so Member A can use the helpers in their pages. Tell Member A when merged — all their pages depend on this.

No tests required beyond a manual checklist in docs/FRONTEND.md. Commit "ui: shared js helpers".
```

---

## B2 — Identity resolution service

```text
TASK B2: Implement services/identity_resolution.py — the Detect engine's evidence layer. Pull main first (models from A1, seed data from A3/A4 if available).

Public interface (must match AGENTS.md 5.9):
  scan(institution_id=None, submission_id=None, academic_year=None) -> ScanResult
ScanResult (dataclass) contains: scan_id, matches (list), edges (list), events (list of detected events with event_key), stats, started_at, finished_at.

Detections (pure functions + one orchestrating scan; each returns events with a stable `event_key`, rule_key, involved student ids, evidence dict, explanation string):
1. DUPLICATE_APAAR — same apaar_ref used by more than one student record (same institution with different institutional IDs, or across institutions).
2. SIMULTANEOUS_ENROLMENT — same apaar_ref ACTIVE in two different institutions in the same academic year.
3. DUPLICATE_INSTITUTE_ID — same institution_student_id + institution + year used by records with different APAAR/name (conflict).
4. SIMILAR_NAME_CORROBORATED — RapidFuzz token_sort_ratio / WRatio on normalized_name >= configurable threshold (default 88) AND at least one corroborating attribute
   (same programme+year+admission_date, or same contact_ref, or same fee_payer_ref, or same institution_student_id pattern). Name similarity alone NEVER creates an event.
   Use blocking (group by first letter/year/programme) so it is not O(n^2) over all records; document the approach.
5. SHARED_CONTACT — same normalized contact_ref across multiple student records: INVESTIGATION SIGNAL only, severity weight small, never creates a duplicate-identity match.
6. SHARED_FEE_PAYER — same for fee_payer_ref. Also signal only.
7. MISSING_OR_MALFORMED_APAAR — empty or fails apaar_adapter.validate_format.
8. CONFLICTING_ACADEMIC_DATA — same APAAR with conflicting programme/admission date/enrolment status in the same year.
9. DUPLICATE_SUBMISSION — read from data_submissions / audit events flagged by A8.

Graph output:
- Nodes: STUDENT, INSTITUTION, APAAR (masked label), CONTACT, FEE_PAYER.
- Edges (identity_graph_edges): every edge has a mandatory human-readable `explanation` such as "Same synthetic APAAR reference", "Similar name (91%) and same programme and admission date",
  "Same normalized contact reference (shared by 3 records — investigation signal, not proof)", "Conflicting enrolment in the same academic year".
- Persist matches and edges idempotently: re-running scan must not duplicate rows (use event_key / unique keys and upsert or delete-and-rebuild within a transaction for that scope).
- Normalization helpers: normalize_contact(ref), normalize_name (reuse A6's if present — import it, do not copy).

Rules:
- Shared contacts/fee payers must never raise the score to "duplicate" territory by themselves and must never be treated as proof. Add a SIGNAL flag on events: is_signal=True.
- Never mutate student records. Never auto-flag anyone.
- Audit-log scan runs (who/when/scope/counts) via audit_service.log.

Tests (tests/test_identity.py): seeded scenarios produce exactly the expected events (simultaneous enrolment, duplicate APAAR, similar-name-with-corroboration, malformed APAAR);
the two legitimate shared-contact scenarios produce SIGNAL events only and no DUPLICATE_APAAR; similar names without corroboration produce nothing; re-running scan is idempotent;
every edge has a non-empty explanation; institution-scoped scan only reads that institution (but cross-institution conflicts involving it are still found when scanning for AICTE).
Commit "identity: resolution engine".
```

---

## B3 — Explainable risk engine

```text
TASK B3: Implement services/risk_engine.py — deterministic, configurable, explainable.

Public interface:
  evaluate_all(scan_result) -> list[RiskCase]            # builds/updates cases from scan events
  record_excess_intake_event(admission_event) -> RiskCase | None   # called by Member A's seat ledger on a REJECTED excess attempt
  score_events(events, weights) -> (score, severity, breakdown)    # pure function, easy to unit test

Rules:
1. Weights come from system_policies key `risk_weights` (defaults from AGENTS.md 5.5). If missing, fall back to defaults in code and log a warning.
2. Score = sum of points of DISTINCT event_keys (dedupe: the same underlying event never scores twice, even if found by two rules or re-scanned), capped at 100.
3. Bands: 0-29 LOW, 30-59 MEDIUM, 60-79 HIGH, 80-100 CRITICAL (read from policy risk_bands if present).
4. Case grouping: one case per "subject cluster" (connected set of student records linked by non-signal events; a signal-only cluster may form a LOW/MEDIUM case labelled
   "Investigation signal"). Re-running evaluate_all updates the existing case (same cluster key) instead of creating a duplicate, and preserves status, assignee and history.
5. Each case contains: reference CASE-XXXXXX, score, severity, evidence rows (rule_key, points, event_key, human description, related student ids, details),
   affected records and institutions, recommended next action (rule-based text, e.g. Critical simultaneous enrolment -> "Request institutional clarification from both institutions
   and place under review"), status OPEN, assigned_to null, initial history entry "Case opened by system scan".
6. NEVER auto-classify a student as fraudulent, NEVER revoke a credential, NEVER change student records because of a score. Include a docstring stating this and a test that proves
   no student/credential row is modified by evaluate_all.
7. Excess intake: record_excess_intake_event creates/updates a case for the institution with EXCESS_INTAKE_VIOLATION (+30), event_key = admission_event id.
8. Keep a small `explain(case)` function that returns a plain-English paragraph: "Score 75 (High) = 40 duplicate APAAR + 35 simultaneous enrolment (capped at 100)".

Tests (tests/test_risk.py): each weight applied once; dedupe works (same event twice = one scoring); cap at 100; band boundaries 29/30/59/60/79/80; signals alone stay low;
re-evaluation does not duplicate cases and keeps status/history; custom weights from policy change the result; excess-intake case creation; no side effects on students/credentials.
Seed data check: the five risk cases required by the spec exist across LOW/MEDIUM/HIGH/CRITICAL after seed + scan (if one band is missing, tell Member A which seed scenario to adjust; do not edit seed.py).
Commit "risk: explainable engine".
```

---

## B4 — Identity and risk APIs, case workflow

```text
TASK B4: Build routes/identity.py and routes/risk.py with the full investigation workflow.

Endpoints (standard envelope, auth + roles + institution scope via services/authz.py):
- POST /api/identity/scan (AICTE_ADMIN; INSTITUTION_ADMIN may scan own institution only). Body: optional institution_id, academic_year. Returns stats + number of cases created/updated.
  Runs scan -> risk_engine.evaluate_all in one request, audit-logged.
- GET /api/identity/graph — query: institution_id, academic_year, case_id, apaar_masked, min_severity, include_signals (bool), limit (default 300 nodes; return a `truncated` flag).
  Response: {nodes:[{id,type,label,institution,severity?,meta}], edges:[{id,source,target,type,explanation}]}. APAAR nodes show masked labels only. Scoped for institution admins.
- GET /api/identity/node/<node_id> — evidence panel data: linked records (masked APAAR), institutions, edges with explanations, linked cases.
- GET /api/risk/cases — filters: severity, status, institution_id, assigned_to, q; pagination; sorted by score desc. AUDITOR read-only; INSTITUTION_ADMIN own institution.
- GET /api/risk/cases/<id> — full case: score breakdown (rule points), evidence list, affected records and institutions, recommended action, status, assignee, history (case_actions).
- POST /api/risk/cases/<id>/actions — body {action, note, assigned_to?}. Allowed actions: UNDER_REVIEW, REQUEST_CLARIFICATION, CONFIRM_DATA_ERROR, DISMISS_FALSE_POSITIVE, RESOLVE.
  State machine (document in code + docs/API.md): OPEN -> UNDER_REVIEW | CLARIFICATION_REQUESTED | FALSE_POSITIVE; UNDER_REVIEW -> CLARIFICATION_REQUESTED | DATA_ERROR_CONFIRMED | FALSE_POSITIVE | RESOLVED;
  CLARIFICATION_REQUESTED -> UNDER_REVIEW | DATA_ERROR_CONFIRMED | FALSE_POSITIVE | RESOLVED; DATA_ERROR_CONFIRMED -> RESOLVED; FALSE_POSITIVE -> UNDER_REVIEW (reopen) | RESOLVED; RESOLVED -> UNDER_REVIEW (reopen, AICTE_ADMIN only).
  Invalid transitions return CONFLICT with the allowed next actions. A note is required for DISMISS_FALSE_POSITIVE, CONFIRM_DATA_ERROR and RESOLVE.
  Who can act: AICTE_ADMIN any case; INSTITUTION_ADMIN may only respond to REQUEST_CLARIFICATION cases of their own institution (a "respond" note, not status changes beyond that);
  AUDITOR read-only. Every action writes a case_actions row and an audit log entry in ONE transaction.
- Assigning a reviewer: PATCH /api/risk/cases/<id> {assigned_to} (AICTE_ADMIN). Reviewer must be a user with AICTE_ADMIN role.

Rules: no endpoint may revoke a credential or modify a student record as a side effect of a case action. Say so in a docstring. Human review is required.

Tests (add to tests/test_risk.py or tests/test_investigation.py): full workflow persisted; invalid transition rejected; note required; institution isolation; auditor cannot act (403);
audit rows created per action; graph endpoint masks APAAR and respects scope; scan endpoint idempotent.
Document the endpoints in docs/API.md (B section). Commit "risk: apis and workflow".
```

---

## B5 — Identity graph explorer page (Cytoscape.js)

```text
TASK B5: Build templates/identity_graph.html and static/js/identity-graph.js. Simple, clean, readable.

Layout (two columns): left = graph canvas (about 65%), right = "Inspector" panel (about 35%).
Top: filter bar (academic year, institution [AICTE only], severity, include shared-contact/fee-payer signals toggle, search by masked APAAR / name), buttons "Run identity scan"
(AICTE_ADMIN / INSTITUTION_ADMIN only, confirm dialog, then reload graph) and "Reset view".

Graph behaviour (Cytoscape.js, vendored):
- Node styles by type, limited palette: STUDENT (navy circle, border colour by risk severity), INSTITUTION (square, grey-blue), APAAR (diamond, saffron outline), CONTACT and FEE_PAYER
  (small hexagon / tag shapes, muted grey, dashed edges because they are signals).
- Edge styles: solid for identity-level evidence (same APAAR, conflicting enrolment), dashed for signals (shared contact / fee payer). Edge label = short type; full explanation shown on click/hover.
- Layout: cose or concentric (use a built-in layout only; no extension packages). Provide a layout selector (cose / circle / breadthfirst) and zoom controls (+, -, fit).
- Legend below the graph (plain HTML) explaining shapes/colours and clearly stating "Shared contact or fee-payer links are investigation signals, not proof of duplicate identity."
- Clicking a node loads GET /api/identity/node/<id> and shows in the Inspector: node type, label (masked APAAR), linked records table (name, institution, programme, year, status),
  all connected edges each with its explanation, and links to related risk cases (/risk-cases/<id>). Clicking an edge shows its explanation and evidence JSON in readable key/value form.
- Empty state: "No records match the filters" and a hint to run a scan. Large graphs: respect the API `truncated` flag and show a warning banner.
- Deep link support: /identity-graph?case_id=... highlights the case cluster and fits the view.
- No dead buttons, no fake loading: show a text "Loading graph..." only while the request is in flight.

Accessibility: all controls keyboard reachable; the inspector content is also listed as text so the graph is not the only way to read the evidence.

Flask route in routes/identity.py for the page (roles AICTE_ADMIN, INSTITUTION_ADMIN, AUDITOR). Manually test with seeded scenarios: the simultaneous-enrolment cluster should show two student nodes,
two institutions and one APAAR node with edges whose explanations are visible.
Commit "ui: identity graph explorer".
```

---

## B6 — Risk investigation centre and case detail

```text
TASK B6: Build templates/risk_cases.html, templates/risk_case_detail.html, static/js/risk.js.

Risk Cases list (/risk-cases):
- Summary strip: counts by severity (Critical/High/Medium/Low) and by status (small stat cards that double as quick filters).
- Filter bar: severity, status, institution (AICTE only), assigned reviewer, search by case reference / student name.
- Compact table: Case ref (link), severity badge, score, status badge, institutions involved, summary, assigned reviewer, last updated. Sort by score desc by default; pagination.
- Auditor sees everything read-only (no action buttons rendered, and the server enforces it).

Case detail (/risk-cases/<id>):
- Header: reference, severity badge, score "75 / 100", status badge, assignee, opened/updated dates.
- "Why this score" card: table of rules fired with points, description, and related records; footer with the capped total; plus the plain-English explain() sentence.
- "Affected records and institutions" card: masked APAAR, name, institution, programme, year, enrolment status, link to student detail; a button "Open in identity graph" -> /identity-graph?case_id=.
- "Recommended next action" card (text from the engine) with the notice: "Risk scores support human review. They do not prove fraud and never trigger automatic action."
- "Actions" card (AICTE_ADMIN only): buttons Under Review, Request Institutional Clarification, Confirm Data Error, Dismiss False Positive, Resolve Case. Only valid next actions are enabled
  (read allowed_actions from the API). Each opens a <dialog> with a note textarea (required where the API requires it), posts to /api/risk/cases/<id>/actions, then refreshes the page data and
  shows a success toast. Errors show the server message.
- Assign reviewer control (AICTE_ADMIN): select from eligible reviewer users (API: GET /api/risk/reviewers); with the required four-account seed, AICTE_Admin is the only seeded AICTE reviewer, so handle a single option and never seed extra reviewer accounts.
- Investigation history timeline: simple list of case_actions (time, actor, action, from -> to, note) plus the "Case opened by system scan" entry.
- Institution admin view for CLARIFICATION_REQUESTED cases of their institution: a "Submit clarification" form that records a note (action type INSTITUTION_RESPONSE) without changing status beyond what the API allows.

Test manually: change a case status as AICTE_Admin, reload, history persists, audit page (Member A) shows the event. Add small JS tests only if easy; backend behaviour is tested in B4.
Commit "ui: risk investigation centre".
```

---

## B7 — Credential service (Ed25519 signing, issue, revoke)

```text
TASK B7: Implement services/credential_service.py. Backend only — secure and testable.

Use `cryptography` Ed25519. Use Member A's services/key_store.py (load_private_key, get_active_key_id) and the signing_keys table (public key only).
If key_store is not on main yet, create a clearly marked temporary adapter and tell Member A.

Functions:
1. build_payload(student, institution, programme, award_year, issue_date, expires_at) -> dict containing ONLY: credential_id (reference), student_ref (synthetic student ID),
   apaar_masked (via apaar_adapter.mask_apaar), institution (code + name), programme, award_year, issue_date (ISO), expires_at (ISO or null), issuer_key_id, version, "synthetic": true.
   Never include full APAAR, DOB, address or contact details.
2. canonicalize(payload) -> bytes: JSON with sort_keys=True, separators=(",", ":"), ensure_ascii=False, UTF-8. Single function used for both signing and verifying.
3. issue_credential(student_id, award_year, programme_id=None, valid_years=None, actor) -> Credential: only INSTITUTION_ADMIN of the student's institution (or AICTE_ADMIN) may issue;
   student must be ACTIVE or GRADUATED, VALID validation_status and NOT have an open CRITICAL/HIGH risk case in UNDER_REVIEW? -> No: do not block on risk automatically.
   Instead return a `warnings` list when open cases exist, and require explicit `acknowledge_warnings=true`. One transaction: build payload, sign, store payload_json + signature (base64) + key_id, status ISSUED, audit-log.
4. verify_credential(reference) -> VerificationOutcome {result: VERIFIED|INVALID|REVOKED|EXPIRED, reason, credential (safe subset), key_id}. Order of checks: exists? -> signature valid over the
   STORED payload_json bytes with the public key for key_id? -> also compare DB columns (institution, programme, award_year, masked APAAR, student ref) to the signed payload (detects DB tampering without
   re-signing) -> revoked? -> expired? Result determined purely by backend logic. Unknown reference -> INVALID ("not found"). Record a verification_events row for every call (no secrets, ip hashed).
5. revoke_credential(credential_id, reason, actor): requires a reason; AICTE_ADMIN or the issuing institution's admin; one transaction; sets status REVOKED, revoked_at/by/reason; audit-logged; idempotent (revoking twice returns CONFLICT).
6. Key management documentation in docs/SECURITY.md: development keys only, where keys live, rotation concept (key_id in each credential), production needs (HSM/KMS, key ceremony, backup, public key distribution,
   revocation list/OCSP-style status endpoint, time-stamping). State plainly that this prototype uses Ed25519 signatures and does NOT implement zero-knowledge proofs or decentralised identity.

Tests (tests/test_credentials.py): valid credential verifies; modifying signature -> INVALID; modifying stored payload_json -> INVALID; modifying a DB column (e.g. award_year) without re-signing -> INVALID;
revoked -> REVOKED; expired -> EXPIRED; unknown reference -> INVALID; payload contains no full APAAR / DOB / address / contact; private key never in any returned structure or log output;
issue permission matrix (VESIT can issue for VESIT only, COEP cannot, no non-seeded login account can); revoke requires reason; verification events recorded.
Commit "credentials: signing, verify, revoke service".
```

---

## B8 — Credentials API, Issue Credential page and Academic Passport page

```text
TASK B8: Build routes/credentials.py (API), templates/issue_credential.html and templates/passport.html, static/js/credentials.js.

API:
- POST /api/credentials/issue (INSTITUTION_ADMIN own institution, AICTE_ADMIN) body {student_id, award_year, valid_years?, acknowledge_warnings?}. 201 with credential summary (never the private key, never the full payload secrets).
  If warnings exist and not acknowledged -> 409 with the warnings list.
- GET /api/credentials — filters: institution, status, student, year; scoped (institution admin own; student own; auditor all read-only).
- GET /api/credentials/<id> — details + current computed verification result + verification event count + QR image (data URI PNG generated server-side with the `qrcode` library, encoding the absolute
  URL of /verify/<reference> built from request.host_url or a PUBLIC_BASE_URL setting).
- POST /api/credentials/<id>/revoke (reason required).
- GET /api/credentials/<id>/qr.png — returns the QR image (scoped).
- GET /api/passport/me (STUDENT) — the student's own profile summary (masked APAAR, institution, programme, year, status) + their credentials list. Never DOB/address/contact.

Pages:
- templates/issue_credential.html (INSTITUTION_ADMIN, AICTE_ADMIN): step 1 search/select an eligible student (table with filter), step 2 form (award year, validity), warnings panel if open risk cases (checkbox
  to acknowledge), confirm dialog, submit, then show the issued credential card with QR and "Open verification page" link. Below: credential issuance history table with status badges and a Revoke button
  (confirm dialog + required reason textarea).
- templates/passport.html (STUDENT): "Academic Passport" card — masked APAAR, institution, programme, award year, status; credentials list with status badge (VERIFIED/REVOKED/EXPIRED computed live), QR image,
  link to verification page, and a button "Share selected details" -> /sharing (built in B11). A short note explains what is shown and that full identifiers are not displayed.
  Institution admins and AICTE admins can open any in-scope credential in a read-only passport view at /credentials/<id>.

Tests: API permission matrix, issue -> list -> detail round trip, revoke then detail shows REVOKED, QR endpoint returns image/png with the right content type and scope enforced, no private key / full APAAR in any response (tests/test_privacy.py start).
Commit "credentials: api, issue page, passport".
```

---

## B9 — Verification route, QR verification page and the four result states

```text
TASK B9: Implement the public QR verification flow.

Route GET /verify/<reference> (public — no login required; read-only; rate-limit lightly by IP using a simple in-memory limiter, 30/min):
- Calls credential_service.verify_credential(reference) and renders templates/verification.html.
- Page content by result:
  VERIFIED: green status panel "Credential verified" + safe claims (credential ID, institution, programme, award year, issue date, masked APAAR, signing key ID) + "Verified by backend signature check at <time>".
  INVALID: red panel "Credential invalid" + reason in plain words (signature mismatch / record altered / not found) and NO claims shown.
  REVOKED: red/amber panel "Credential revoked" + revocation date and reason category (not internal notes).
  EXPIRED: amber panel "Credential expired" + expiry date.
- The status is rendered from the backend result only. No hard-coded green badge. Include `Cache-Control: no-store`.
- JSON variant: GET /verify/<reference>.json (same logic) for tests and demos.
- A "Verify a credential" form page at /verify-console (VERIFIER and any logged-in role) where the user pastes a credential reference or opens a QR link; submitting navigates to /verify/<reference>.
  Logged-in VERIFIER sees recent verification events (their own) in a small table.
- Footer on this page: "Prototype — synthetic data only. Signature scheme: Ed25519 (development keys)."

Demo tooling (so the judges can see all four states without hacking the DB):
- Credentials seeded by seed_b.py: valid, revoked, expired, tampered (the tampered one has its stored payload altered after signing — created by a function in seed_b.py).
  Add a "Demo credentials" table on /verify-console (visible only when SHOW_DEMO_ACCOUNTS is true) listing the four references with links.

Tests: each of the four states renders the expected status text; tampered credential never shows claims; verification event recorded; no private key in response; route works without login; unknown reference -> INVALID page with 200 (do not leak existence info beyond "not found") — document this choice.
Commit "verify: public verification page and states".
```

---

## B10 — Consent and sharing sessions (backend)

```text
TASK B10: Implement services/sharing_service.py and routes/sharing.py (API only; UI is B11).

Concepts: a student creates a consent (list of claims), chooses an expiry, and gets an opaque, high-entropy link + QR that exposes ONLY the selected claims.

Service:
1. create_sharing_session(student, credential_id, claims, expiry_hours, actor): claims subset of {DEGREE_AUTHENTICITY, INSTITUTION, PROGRAMME, AWARD_YEAR, STUDENT_NAME, APAAR_MASKED};
   expiry_hours in {24, 72, 168} (policy-driven). Student may only share their OWN credential. Credential must currently verify as VERIFIED (else CONFLICT).
   Token = secrets.token_urlsafe(32). Store ONLY sha256(token) as token_hash plus the first 6 chars as token_prefix. Return the full token exactly once in the create response. Create consent_records row.
   STUDENT_NAME and APAAR_MASKED require an explicit flag `explicit_authorisation=true` for each sensitive claim in the request (else VALIDATION_ERROR). The full APAAR can never be shared by any claim.
2. resolve_token(token) -> hash lookup; checks: exists, not revoked, not expired (server-side clock), credential still VERIFIED (re-run verify; if revoked/expired the session shows that state and NO claims).
   Returns the minimal disclosure dict containing only authorised claims. Increment access_count, set last_accessed_at, write verification_events (no raw token in logs).
3. revoke_session(session_id, actor): student owner only (AICTE_ADMIN may revoke for support, audit-logged).
4. list_sessions(student) -> active / expired / revoked with computed status.

Routes:
- POST /api/sharing-sessions (STUDENT) -> 201 {id, token (once), share_url, qr_data_uri, expires_at, claims}
- GET /api/sharing-sessions (STUDENT own; AUDITOR/AICTE_ADMIN read-only metadata, never tokens) -> status computed server-side; token_prefix only.
- POST /api/sharing-sessions/<id>/revoke
- GET /public/verify/<token> (public GET; renders public_verify.html in B11 — for now return JSON when ?format=json) with Cache-Control: no-store, light IP rate limit, generic 404-style response for unknown/malformed tokens
  (do not reveal whether a token ever existed) but a clear message for expired/revoked ("This sharing link has expired / was revoked by the student").

Never expose in any response: full APAAR, DOB, address, contact info, other credentials, internal IDs of the student record beyond the credential reference.

Tests (tests/test_sharing.py and tests/test_privacy.py): create session returns token once and DB stores only hash; only selected claims in public response (degree + award year case: no name, no APAAR, no institution if not selected);
sensitive claims require explicit flag; expired session (freeze/advance time via an injectable clock) returns expired and no claims; revoked session returns revoked; credential revoked after sharing -> public view shows revoked, no claims;
student cannot share another student's credential; list endpoint never returns tokens; invalid expiry rejected; brute-force style malformed tokens give uniform responses.
Commit "sharing: consent sessions backend".
```

---

## B11 — Sharing UI and public verification page

```text
TASK B11: Build templates/sharing.html, templates/public_verify.html, static/js/sharing.js.

Student Sharing page (/sharing, STUDENT):
1. Step 1 — "Choose credential": list of the student's credentials with status badges (only VERIFIED ones selectable).
2. Step 2 — "Choose what to share": checkboxes for Degree authenticity, Institution, Programme, Award year, and separately (with an amber note "Personal details — share only if the verifier needs them")
   Student name and Masked APAAR reference. Explain in one line what each reveals. A plain note: "Your full APAAR ID, date of birth, address and contact details are never shared."
3. Step 3 — "Choose expiry": radio buttons 24 hours / 72 hours / 7 days.
4. Create button -> confirm dialog summarising the claims and expiry -> POST /api/sharing-sessions -> result panel shows the share link (read-only input + Copy button using the Clipboard API with a graceful fallback),
   the QR image (data URI from the API), the expiry time, and a warning "This link is shown once. Copy it now." The token is never stored in localStorage or the URL of the app page.
5. "My sharing sessions" table: created, claims, expires, status badge (ACTIVE / EXPIRED / REVOKED from the server), access count, token prefix, and a Revoke button (confirm dialog) that calls the API and refreshes.

Public verification page (/public/verify/<token>):
- Standalone simple layout (no sidebar; same style.css), header "Shared Academic Verification".
- Shows only the authorised claims as a key/value list, a status panel (Valid / Expired / Revoked / Invalid) rendered from the backend, the expiry time, and the note
  "The student chose to share only these details. This link expires on <time>."
- For expired/revoked/unknown: show a clear message and no claims.
- Never include student internal IDs in the HTML. Add <meta name="robots" content="noindex">.
- Employer verification experience: when a logged-in VERIFIER opens it, show the same page plus a small "Verification recorded" line (server logs a verification event).

Manual security checks to perform and report: open the link in a private window (no login) and confirm only selected claims appear; revoke and refresh -> revoked message; change one character of the token -> generic invalid message;
inspect page source for hidden fields containing non-authorised data (there must be none).
Commit "ui: sharing and public verification".
```

---

## B12 — Governance dashboard, anomaly report and regulatory reports page

```text
TASK B12: Build the AICTE governance dashboard and the reports page. Pull main first so Member A's /api/dashboard/institution contract exists (see docs/API.md).

API (routes/dashboards.py — governance part only; routes/reports.py — anomaly report only):
- GET /api/dashboard/governance (AICTE_ADMIN, AUDITOR) with filters: academic_year, institution_id, programme_id, category, validation_status, risk_level. Returns:
  totals (institutions, student records, validated, pending validations, active enrolments, identity conflicts, missing/invalid APAAR, institutions >= 80/90/100% capacity, excess-admission attempts),
  risk cases by severity, category-wise enrolment, institution-wise admission trend (per academic year), credential verification activity (counts by result per day, last 14 days), recent audit events (last 10).
  All values computed from the database. No hard-coded numbers.
- GET /api/reports/anomalies (JSON) and /api/reports/anomalies.csv — risk cases and key evidence per institution (masked APAAR only), filters like the dashboard; audit-logged exports; filename contains SYNTHETIC.
Dashboard page (templates/dashboard.html + static/js/dashboard.js) serves both the governance view (AICTE_ADMIN/AUDITOR) and the institution view (INSTITUTION_ADMIN, using Member A's endpoint) by role:
- Top filter bar working for every listed filter (the server must actually apply them).
- Stat cards row (8-10 cards). Charts with Chart.js using the limited palette, titles and axis labels: risk cases by severity (bar), category-wise enrolment (bar or horizontal bar), institution admission trend (line),
  capacity utilisation by institution (bar with 80/90/100 reference text), credential verification results (stacked bar or doughnut).
- Lists: institutions approaching capacity (name, utilisation badge), recent audit events (time, actor, action), recent high/critical risk cases (links).
- Institution view: approved intake, actual admissions, remaining seats, category-wise capacity table/chart, utilisation bar, submission history, validation errors by code, pending identity checks, institutional risk cases, credential issuance history.
- Every card/chart is clickable only if it navigates somewhere real (e.g. risk bars -> /risk-cases?severity=...). No dead links.
Reports page (templates/reports.html): cards for Enrolment report (Member A's CSV), Anomaly report, Audit log export (Member A's API) with filter selectors and Download buttons that hit the real CSV endpoints; a "Recent exports" list read from audit logs.

Tests: governance API scope (institution admin 403), numbers equal direct DB counts for seeded data, filters change results, anomaly CSV scope + masked APAAR + filename, auditor can read but not mutate.
Commit "dashboard: governance and reports".
```

---

## B13 — Seed extras for Detect and Prove, plus full test pass for Member B

```text
TASK B13: Create seed_b.py with function seed_prove_and_detect(db) (called by Member A's seed.py) and consolidate tests for all Member B modules.

seed_b.py (deterministic, idempotent, synthetic):
1. Run identity_resolution.scan() and risk_engine.evaluate_all() over the seeded students so risk cases exist from real engine output.
   Verify the result contains at least five cases spanning LOW, MEDIUM, HIGH and CRITICAL (including the excess-intake case from the seeded rejected admissions).
   If a band is missing, report to Member A which seed scenario to adjust — do not edit seed.py yourself.
2. Credentials (4 required, fixed references so the demo script can cite them):
   - CRED-DEMO01 valid (belongs to an eligible seeded synthetic student record),
   - CRED-DEMO02 revoked (revoked by AICTE_Admin, with a reason),
   - CRED-DEMO03 expired (expires_at in the past),
   - CRED-DEMO04 tampered (issued and signed correctly, then stored payload / award_year altered directly in the DB so verification returns INVALID).
   All signed with the development Ed25519 key through credential_service (except the deliberate tampering step).
3. One ACTIVE sharing session for an eligible seeded synthetic student record (claims: DEGREE_AUTHENTICITY + AWARD_YEAR, expiry 72h) with a KNOWN demo token printed once during seeding (in the seed summary only) so the demo can open the public link;
   state in docs/DEMO_SCRIPT.md that this token is demo-only. Also one expired and one revoked session for the table.
4. Representative audit entries for: scans, case actions, credential issue/revoke, sharing create/revoke (use the services so entries are authentic).

Tests: consolidate and make sure these files exist and pass: test_identity.py, test_risk.py, test_credentials.py, test_sharing.py, test_privacy.py. Add test_privacy.py cases that walk EVERY JSON endpoint as every role and fail if a response
body contains a full 12-digit APAAR from the seed, a private-key PEM header, a full sharing token, or a password hash. Add a test that enumerates url_map and asserts public routes are only the verify routes + login + health.
Run `pytest -q` and report the REAL summary line. Commit "seed-b and tests: member B".
```

---

## B14 — Demo polish, documentation and rehearsal

```text
TASK B14: Final polish. No new features — fix rough edges, write the docs that judges and teammates will read.

1. UI consistency pass across ALL pages (including Member A's — report problems instead of editing their files, or make tiny CSS-only fixes in style.css):
   - consistent page titles and helper text, consistent button wording, consistent badge colours, empty states everywhere, no console errors, keyboard navigation works, contrast OK,
   - every toast message is meaningful, every destructive action has a confirm dialog, no dead buttons or placeholder links, footer banner on every page,
   - check at 1366x768 and 1920x1080 and at ~900px width (sidebar collapses).
2. docs/DEMO_SCRIPT.md — the 12-step SIH workflow written as a click-by-click script with exact usernames, page URLs, what to say, expected result, and a fallback if something fails (e.g. run `python seed.py --reset`).
   Include timings (target under 8 minutes), the demo credential references (CRED-DEMO01..04), the demo sharing token note, and a "what judges might ask" Q&A list (why APAAR is not a primary key,
   why shared contacts are signals not proof, why no auto-revocation, how concurrency is handled, what is mocked, what production would need).
3. docs/SECURITY.md — complete: auth, RBAC, institution isolation, CSRF, session settings, upload controls, password hashing, key management (development keys vs production HSM/KMS), token hashing, selective disclosure,
   audit logging, privacy defaults (masked APAAR), what is NOT implemented (no ZKP, no decentralised identity, no real APAAR/UIDAI/DigiLocker integration, development server only).
4. docs/API.md — merge A and B sections into one readable reference: method, path, roles, params, example request/response, error codes. Verify each endpoint listed exists in `flask routes` output (write a tiny script `scripts/check_api_docs.py` that compares).
5. README.md sections owned by Member B: identity graph, risk engine (weights table + bands + "prototype rules, not official AICTE policy"), credentials and QR verification, consent sharing, screenshots added only when actual screenshots exist; do not leave broken placeholders
   (docs/screenshots/*.png — take real screenshots of the running app: dashboard, seat ledger block, graph, case detail, verification page, sharing page).
6. Rehearsal: run the full 12-step demo twice from `python seed.py --reset`, with a stopwatch, and write down any friction. Fix what you can. Record a backup screen recording and note where it is saved.
7. Fresh-clone test: clone the repo into a new folder, follow ONLY the README commands, and confirm the app starts and the demo login works. Report any missing step.

Final report must include the REAL `pytest -q` summary, the list of known limitations, and the exact commands used for the fresh-clone test.
Commit "docs: demo script, security, api, polish".
```
