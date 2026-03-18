# INITIAL.md - Define Your Product

> Fill this out, then run `/generate-prp INITIAL.md`

---

## PRODUCT

**Name:** AI QA Engine

**Description:** A structured AI-powered QA tool that converts software requirements into scenario maps, generates senior-level test cases (positive, negative, boundary, edge, permission), and validates output using a built-in QA checklist and review loop. Built for QA engineers, leads, and teams who want to move fast without missing coverage.

**Type:** SaaS

---

## TECH STACK

| Layer | Choice |
|-------|--------|
| Backend | FastAPI + Python |
| Frontend | React + TypeScript + Vite |
| Database | PostgreSQL |
| Auth | JWT + Google OAuth |
| UI | Chakra UI / Tailwind |
| Payments | None |
| AI | Claude API (claude-sonnet-4-6) |

---

## MODULES

### Module 1: Authentication (Built-in)

**Models:** User, RefreshToken

**Endpoints:**
- POST /auth/register, /auth/login, /auth/refresh
- GET /auth/me, /auth/google

**Pages:** /login, /register, /profile

---

### Module 2: QA Session (Core Module)

**Description:** A QA session is one run of the AI engine. The user inputs a requirement + context pack, selects output columns/template, and the system generates a full QA artifact.

**Models:**
```
QASession:
  - id, user_id (FK)
  - name: str
  - requirement: text          # pasted or uploaded requirement
  - context: jsonb             # product, platform, users, rules, risks, environment
  - template: str              # column/output template selected
  - status: enum               # pending | generating | complete | failed
  - created_at, updated_at

QAOutput:
  - id, session_id (FK)
  - scenario_map: jsonb        # main/alternate/error/permission/integration flows
  - test_cases: jsonb          # list of structured test case rows
  - assumptions: text[]
  - questions: text[]
  - checklist_result: jsonb    # per-category pass/fail
  - created_at
```

**Endpoints:**
```
POST   /api/sessions              - Create session + trigger generation
GET    /api/sessions              - List all sessions for user
GET    /api/sessions/{id}         - Get session + output
DELETE /api/sessions/{id}         - Delete session
POST   /api/sessions/{id}/regenerate - Re-run generation
```

**Pages:**
```
/sessions           - List all past sessions
/sessions/new       - Create new session (input form)
/sessions/{id}      - View output (tabbed)
```

---

### Module 3: Input & Context Form

**Description:** Step-by-step input form where the user:
1. Pastes or uploads a requirement
2. Fills the context pack (product/domain, platform, users/roles, rules/constraints, risks, environment)
3. Selects output template (which columns to include in the test case table)
4. Clicks Generate

**Pages:**
```
/sessions/new       - Multi-step form (requirement → context → template → generate)
```

---

### Module 4: Output Viewer (Tabbed)

**Description:** After generation, display the full QA artifact in tabs.

**Tabs:**
- **Scenario Map** — Main flows, alternate flows, error flows, permission flows, integration flows
- **Test Cases** — Structured table with: Test ID, Scenario, Type, Preconditions, Steps, Test Data, Expected Result, Priority (P1/P2/P3), Risk Notes
- **Assumptions** — List of assumptions the AI made
- **Questions** — List of questions for Product/Dev
- **QA Checklist** — Pass/fail indicators for: Positive+Negative coverage, Boundary conditions, Permissions/roles, State-based scenarios, Clear expected results, No duplicates, Traceability

**Features:**
- Copy table to clipboard
- Export to CSV
- Export to PDF (nice-to-have)

**Pages:**
```
/sessions/{id}      - Tabbed output view
```

---

### Module 5: Dashboard

**Description:** Overview of all QA sessions, quick stats, and recent activity.

**Pages:**
```
/dashboard          - Stats: total sessions, avg test cases generated, recent sessions
/settings           - User profile, API key management (if needed)
```

---

## AI PROMPT LOGIC (Backend Service)

The backend constructs a structured prompt using:
1. The requirement text
2. The context pack fields
3. A fixed senior QA Lead system prompt

The AI runs a 6-step process:
1. Scenario Map (main/alternate/error/permission/integration flows)
2. Test case generation per scenario (positive/negative/boundary/edge/permission)
3. Structured table output (all columns)
4. Assumptions + Questions for Product/Dev
5. QA Review (remove duplicates, add missing edge cases, improve expected results, identify risk gaps)
6. QA Checklist Validation (pass/fail per category)

Returns structured JSON that maps directly to the QAOutput model.

---

## MVP SCOPE

Must Have:
- [x] User registration/login
- [x] Create QA session (paste requirement + context form)
- [x] AI generation via Claude API
- [x] Tabbed output viewer (Scenario Map, Test Cases, Assumptions, Questions, QA Checklist)
- [x] List/delete past sessions
- [x] Export test cases to CSV

Nice to Have:
- [ ] PDF export
- [ ] Re-generate / edit and regenerate
- [ ] Team/shared sessions
- [ ] Custom templates

---

## ACCEPTANCE CRITERIA

- [ ] User can register, login, and manage their account
- [ ] User can create a QA session by pasting a requirement and filling context
- [ ] AI generates a full QA artifact (scenario map + test cases + assumptions + questions + checklist)
- [ ] Output is displayed in a clean tabbed UI
- [ ] User can export test cases to CSV
- [ ] All past sessions are saved and retrievable
- [ ] 80%+ test coverage on backend
- [ ] Docker builds successfully

---

## RUN

```bash
/generate-prp INITIAL.md
/execute-prp PRPs/ai-qa-engine-prp.md
```
