# STEPS.md — APAAR Nexus build plan for 2 people

> Companion to `AGENTS.md`. AGENTS.md says **how** we build. This file says **what, in which order, and who**.
> Prompts live in `PROMPTS_MEMBER_A.md` and `PROMPTS_MEMBER_B.md`. Run them in order.

---

## 1. Who does what (summary)

| | Member A — Data, Security & Prevent | Member B — UI Shell, Detect & Prove |
|---|---|---|
| Pillar | **Prevent** (Seat Ledger) | **Detect** (Identity Graph, Risk) + **Prove** (Passport) |
| Foundation | Repo bootstrap, ALL DB models, seed (core), auth + RBAC, audit service | Design system, `base.html`, shared JS, vendored libraries |
| Data | Institutions, programmes, policies, students, change history, CSV ingestion, APAAR adapter, validation | Identity resolution, risk engine, case workflow |
| Pages | Login, Institutions, Students, Student Detail, Upload wizard, Seat Ledger, Audit Logs, Policies, Institution Dashboard | Governance Dashboard, Identity Graph, Risk Cases + Detail, Passport, Issue Credential, Verification, Sharing, Public Verify, Reports |
| Security | Auth, CSRF, authz decorators, institution isolation, upload limits | Ed25519 signing, tamper/revoke/expiry logic, token hashing, selective disclosure |
| Prompts | A0 – A13 (14 prompts) | B0 – B14 (15 prompts) |

**Why this split works:** A builds the data backbone and the "block bad admissions" story; B builds the "find bad identities" and "prove good credentials" story and owns the look and feel. The only hard dependencies are (1) B needs A's models and (2) A's login/pages need B's base layout. Both are resolved in the first block (see Section 3).

---

## 2. Rules of engagement

1. Use the prompts in order. After each prompt: run the app, click through the feature, run `pytest -q`, and commit to the same owner branch. Do not open a PR per prompt; use only the planned checkpoint PRs.
2. Use exactly two long-lived working branches for the whole project: `member-a` (Tanmay) and `member-b` (Yash). Never create a branch per prompt. Commit each completed prompt to the owner's existing branch. Open PRs from these two branches only, at the sync checkpoints below; merge in the order specified to keep integration predictable.
3. At the start of every session, fetch and sync the owner branch using the safe protocol in AGENTS.md; do not rebase shared branches.
4. Never edit a file owned by the other member (see AGENTS.md section 3). Ask them.
5. Every sync checkpoint below is a hard gate: both on `main`, app starts, `pytest -q` green.
6. Keep a shared note (WhatsApp / Notion / `docs/BLOCKERS.md`) with "waiting on X from teammate".

---

## 3. Phased plan

Time estimates assume focused working sessions. Scale them to the days left before the hackathon. If you are short on time, use the "Cut list" in Section 7.

### Block 0 — Bootstrap (about 1–2 hours) · parallel

| Member A | Member B |
|---|---|
| **A0** Repo skeleton, config, app factory, blueprint registry, error handlers, requirements, `.gitignore` | **B0** Design system: `style.css`, `base.html` (sidebar, topbar, footer banner, toast container), vendored Chart.js + Cytoscape.js |
| Push to GitHub immediately so B can pull | Starts from a local static mock, merges after A0 lands |

**Checkpoint 0:** A0 merged. `python app.py` shows a healthy `/api/health`. B0 merged on top. Both pull.

### Block 1 — Foundation (about 3–4 hours) · parallel

| Member A | Member B |
|---|---|
| **A1** All database models (including B's tables) + `docs/DB_SCHEMA.md` | **B1** Shared JS (`app.js`): api wrapper with CSRF, toast, confirm dialog, table/pagination helper, filter bar helper, badge helper |
| **A2** Auth, RBAC decorators, institution scoping, login page | **B2** Identity resolution service (pure Python first, wired to models after A1 merges) |

**Checkpoint 1:** A1 merged (B can now use models). Login works for all four demo accounts and redirects by role.

### Block 2 — Data and engines (about 4–5 hours) · parallel

| Member A | Member B |
|---|---|
| **A3** Seed script part 1 (users, institutions, programmes, capacities, policies, key metadata) | **B3** Risk engine (weights, dedupe, cap, bands, recommendation) |
| **A4** Seed script part 2 (150+ students, all scenarios) | **B4** Identity and risk APIs (`/api/identity/*`, `/api/risk/*`) |
| **A5** Institutions, programmes, policies APIs and pages | |
| **A6** APAAR adapter + validation service | |

**Checkpoint 2:** ``python seed.py --reset` produces a full synthetic dataset. B can run `scan` over it and get cases.

### Block 3 — Ingestion, Seat Ledger and Graph UI (about 5–6 hours) · parallel

| Member A | Member B |
|---|---|
| **A7** Student CRUD, change history, repository + detail pages | **B5** Identity graph page (Cytoscape, node inspector, evidence panel) |
| **A8** CSV ingestion pipeline + upload wizard | **B6** Risk investigation centre + case detail + actions |
| **A9** Seat ledger engine (transactions, concurrency, rules) | |
| **A10** Admissions API + Seat Ledger page | |

**Checkpoint 3 (mid-point demo):** upload CSV → errors shown → 121st admission blocked → graph shows a cross-institution conflict → case status changed → audit entry visible. Record a short screen capture for safety.

### Block 4 — Credentials, Sharing and Dashboards (about 5–6 hours) · parallel

| Member A | Member B |
|---|---|
| **A11** Audit service/log page + institution dashboard + enrolment report | **B7** Credential service (Ed25519, canonical JSON, issue, revoke, key metadata) |
| | **B8** Credentials API + Issue Credential page + Passport page |
| | **B9** Verification route + QR + four result states |
| | **B10** Consent and sharing sessions backend |
| | **B11** Sharing UI + public verify page |

**Checkpoint 4:** issue → QR verify → tamper → revoke → share link → employer sees only allowed claims.

### Block 5 — Governance views, tests and hardening (about 4–5 hours) · parallel

| Member A | Member B |
|---|---|
| **A12** Tests for all A modules | **B12** Governance dashboard + anomaly report + regulatory reports page |
| **A13** Hardening + integration (import → identity scan hook, security review) | **B13** `seed_b.py` + tests for all B modules |

**Checkpoint 5:** `pytest -q` fully green on `main`. `python seed.py --reset` then full demo works.

### Block 6 — Polish and rehearsal (about 3–4 hours) · together

| Member A | Member B |
|---|---|
| README sections: setup, data, seat ledger, CSV format, known limitations | **B14** Demo polish, `docs/DEMO_SCRIPT.md`, `docs/SECURITY.md`, `docs/API.md` finish, README sections: graph, credentials, sharing |
| Rehearse the 12-step SIH demo with a timer | Screenshots for README, backup screen recording |

**Final checkpoint:** fresh clone on a clean Windows machine runs with the README commands only.

---

## 4. Dependency map (who waits for whom)

```
A0 ──► B0 (B merges onto A's skeleton)        B0 ──► A2 (login page uses base.html)
A1 ──► B2 (wire identity service to models)   A1 ──► B3, B4, B7, B10
A3/A4 ──► B3/B4 testing (needs data)          B2/B3 ──► A13 (import triggers scan)
B1 ──► every page of A (api wrapper, toast)   A2 ──► every protected route of B
A9 ──► B3 (excess-intake risk event)          A11 (audit service) ──► everyone (log calls)
```

If blocked: write a stub with the agreed interface (AGENTS.md 5.9), keep going, replace the stub when the teammate merges.

Audit service stub (until A11 is done, A should ship the stub in A0/A1 so nobody is blocked):
```python
def log(actor, action, entity_type, entity_id, details=None, institution_id=None): ...
```
**A must merge a working `audit_service.log` with A1**, even if the audit page comes later.

---

## 5. The 12-step SIH demo and which prompt makes it work

| Demo step | Needs prompts |
|---|---|
| 1. AICTE admin logs in, sees governance dashboard | A2, A3, A4, B12 |
| 2. Upload CSV with valid, duplicate, invalid APAAR, conflicting rows | A6, A8 |
| 3. Validation results + error report download | A8 |
| 4. Seat ledger: exceed intake, backend blocks | A9, A10 |
| 5. Identity graph: cross-institution conflict, evidence, risk score | B2, B3, B5 |
| 6. Update case status, persisted audit event | B4, B6, A11 |
| 7. Open passport, issue signed credential | B7, B8 |
| 8. Scan QR → verified | B9 |
| 9. Tampered + revoked credential rejected | B7, B9 |
| 10. Time-limited sharing session (degree + award year only) | B10, B11 |
| 11. Employer sees only allowed fields | B10, B11 |
| 12. Export regulatory report | A11, B12 |

---

## 6. Local setup (both members, first time)

```powershell
git clone <your-repo-url> apaar-nexus
cd apaar-nexus
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python seed.py --reset
python app.py
```

Open http://127.0.0.1:5000

If PowerShell blocks the activate script:
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

Run tests:
```powershell
pytest -q
```

---

## 7. Cut list (if time runs out, drop in this order)

1. Student-facing "active and expired sessions" extras beyond create / list / revoke.
2. PDF anything — keep CSV exports only.
3. Institution-wise trend chart variants (keep one trend chart).
4. Field-mapping UI in CSV wizard (keep the documented template + strict headers).
5. Policy settings page edits (keep read-only view).

**Never cut:** server-side capacity enforcement, signature verification, tamper/revoke detection, selective disclosure, audit logs, role enforcement, tests for those.

---

## 8. Daily rhythm (suggested)

- Start: pull `main`, read teammate's last PR titles, pick next prompt.
- During: one prompt → run → click-test → tests → commit on the same owner branch. PR only at a planned checkpoint.
- End of session: merge, post a 3-line status ("done / next / blocked").
- Every checkpoint: 10-minute joint walkthrough of the demo steps that are now possible.

---

## 9. Pre-submission checklist

- [ ] Fresh clone + README commands works on a clean machine
- [ ] `python seed.py --reset` is deterministic (same data every time)
- [ ] All 4 demo accounts log in and see only their permitted institution scope and menu
- [ ] Demo script from `docs/DEMO_SCRIPT.md` runs in under 8 minutes
- [ ] `pytest -q` is green (and you have the real output saved)
- [ ] No `.env`, DB file or private key committed
- [ ] README has screenshots, known limitations, and the "synthetic data only" disclaimer
- [ ] Backup screen recording of the full demo saved offline
