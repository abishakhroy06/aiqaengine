# PRP: AI QA Engine

> Implementation blueprint for parallel agent execution

---

## METADATA

| Field | Value |
|-------|-------|
| **Product** | AI QA Engine |
| **Type** | SaaS |
| **Version** | 1.0 |
| **Created** | 2026-03-17 |
| **Complexity** | Medium |

---

## PRODUCT OVERVIEW

**Description:** A structured AI-powered QA tool that converts software requirements into scenario maps, generates senior-level test cases (positive, negative, boundary, edge, permission), and validates output using a built-in QA checklist and review loop.

**Value Proposition:** QA engineers and leads stop writing test cases from scratch. Paste a requirement, fill context, get a complete QA artifact in seconds — with scenario map, structured test case table, assumptions, questions for dev, and a validated coverage checklist.

**MVP Scope:**
- [x] User registration / login (JWT + Google OAuth)
- [x] Create QA session (paste requirement + fill context pack)
- [x] AI generation via Claude API (6-step QA prompt engine)
- [x] Tabbed output viewer (Scenario Map, Test Cases, Assumptions, Questions, QA Checklist)
- [x] List and delete past sessions
- [x] Export test cases to CSV

---

## TECH STACK

| Layer | Technology | Skill Reference |
|-------|------------|-----------------|
| Backend | FastAPI + Python 3.11+ | skills/BACKEND.md |
| Frontend | React + TypeScript + Vite | skills/FRONTEND.md |
| Database | PostgreSQL + SQLAlchemy | skills/DATABASE.md |
| Auth | JWT + bcrypt + Google OAuth | skills/BACKEND.md |
| UI | Chakra UI + Framer Motion | skills/FRONTEND.md |
| AI | Claude API (claude-sonnet-4-6) | skills/BACKEND.md |
| Testing | pytest + React Testing Library | skills/TESTING.md |
| Deployment | Docker + GitHub Actions | skills/DEPLOYMENT.md |

---

## DATABASE MODELS

### User
```
id: int (PK)
email: str (unique)
hashed_password: str (nullable — OAuth users)
full_name: str
is_active: bool (default: true)
is_verified: bool (default: false)
oauth_provider: str (nullable — "google")
created_at: datetime
updated_at: datetime
```

### QASession
```
id: int (PK)
user_id: int (FK → User)
name: str
requirement: text
context: jsonb  {
  product: str,
  platform: str,
  users_roles: str,
  rules_constraints: str,
  risks: str,
  environment: str
}
template: str  (default: "full" — which columns to include)
status: enum  [pending, generating, complete, failed]
created_at: datetime
updated_at: datetime
```

### QAOutput
```
id: int (PK)
session_id: int (FK → QASession, unique)
scenario_map: jsonb  {
  main_flows: [str],
  alternate_flows: [str],
  error_flows: [str],
  permission_flows: [str],
  integration_flows: [str]
}
test_cases: jsonb  [
  {
    test_id: str,
    scenario: str,
    type: str,         # Positive | Negative | Boundary | Edge | Permission
    preconditions: str,
    steps: str,
    test_data: str,
    expected_result: str,
    priority: str,     # P1 | P2 | P3
    risk_notes: str
  }
]
assumptions: [str]
questions: [str]
checklist_result: jsonb  {
  positive_negative: bool,
  boundary_conditions: bool,
  permissions_roles: bool,
  state_based: bool,
  clear_expected_results: bool,
  no_duplicates: bool,
  traceability: bool
}
created_at: datetime
```

### RefreshToken
```
id: int (PK)
user_id: int (FK → User)
token: str (unique)
expires_at: datetime
created_at: datetime
```

---

## MODULES

### Module 1: Authentication
**Agents:** DATABASE-AGENT + BACKEND-AGENT + FRONTEND-AGENT

**Backend Endpoints:**
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /auth/register | Create account with email/password |
| POST | /auth/login | Login, return access + refresh tokens |
| POST | /auth/refresh | Refresh access token |
| POST | /auth/logout | Invalidate refresh token |
| GET | /auth/me | Get current user |
| GET | /auth/google | Initiate Google OAuth |
| GET | /auth/google/callback | Handle Google OAuth callback |

**Frontend Pages:**
| Route | Page | Components |
|-------|------|------------|
| /login | LoginPage | LoginForm, GoogleOAuthButton |
| /register | RegisterPage | RegisterForm, GoogleOAuthButton |
| /profile | ProfilePage | ProfileCard, UpdateProfileForm |

---

### Module 2: QA Session Management
**Agents:** DATABASE-AGENT + BACKEND-AGENT + FRONTEND-AGENT

**Backend Endpoints:**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/sessions | List all sessions for current user |
| POST | /api/sessions | Create session + trigger AI generation |
| GET | /api/sessions/{id} | Get session + full output |
| DELETE | /api/sessions/{id} | Delete session |
| POST | /api/sessions/{id}/regenerate | Re-trigger AI generation |
| GET | /api/sessions/{id}/export | Export test cases as CSV |

**Frontend Pages:**
| Route | Page | Components |
|-------|------|------------|
| /sessions | SessionsListPage | SessionCard, EmptyState, StatusBadge |
| /sessions/new | NewSessionPage | RequirementInput, ContextForm, TemplateSelector, GenerateButton |
| /sessions/{id} | SessionOutputPage | OutputTabs, ScenarioMapTab, TestCasesTable, AssumptionsTab, QuestionsTab, ChecklistTab, ExportButton |

---

### Module 3: AI Generation Service (Backend)
**Agents:** BACKEND-AGENT

**Description:** Internal service that constructs the structured QA prompt and calls the Claude API. Runs asynchronously after session creation. Updates session status throughout.

**Service flow:**
1. Session created → status: `pending`
2. AI service triggered (background task) → status: `generating`
3. Build prompt from requirement + context pack
4. Call Claude API with 6-step QA system prompt
5. Parse structured JSON response
6. Save QAOutput record → status: `complete`
7. On error → status: `failed`

**Files:**
```
backend/app/services/ai_service.py      # Claude API client + prompt builder
backend/app/services/qa_prompt.py       # System prompt template (6-step QA logic)
backend/app/services/session_service.py # Session CRUD + generation trigger
```

**Claude API Prompt Structure (6 steps):**
```
Step 1: Scenario Map (main/alternate/error/permission/integration flows)
Step 2: Test cases per scenario (positive/negative/boundary/edge/permission)
Step 3: Structured table (Test ID, Scenario, Type, Preconditions, Steps, Test Data, Expected Result, Priority, Risk Notes)
Step 4: Assumptions + Questions for Product/Dev
Step 5: QA Review (remove duplicates, add missing edge cases, improve expected results, identify risk gaps)
Step 6: QA Checklist Validation (pass/fail per category)

Return: structured JSON matching QAOutput schema
```

---

### Module 4: Output Viewer (Frontend)
**Agents:** FRONTEND-AGENT

**Description:** Tabbed output viewer displayed after generation completes. Polls session status while generating.

**Tabs:**
| Tab | Content |
|-----|---------|
| Scenario Map | Cards grouped by flow type (main/alternate/error/permission/integration) |
| Test Cases | Sortable/filterable table. Columns: Test ID, Scenario, Type, Preconditions, Steps, Test Data, Expected Result, Priority, Risk Notes |
| Assumptions | Numbered list |
| Questions | Numbered list (for Product/Dev) |
| QA Checklist | Pass/fail indicators for all 7 coverage categories |

**Actions:**
- Copy test cases table (clipboard)
- Export to CSV
- Regenerate (re-trigger AI)

---

### Module 5: Dashboard
**Agents:** FRONTEND-AGENT

**Pages:**
| Route | Page | Components |
|-------|------|------------|
| /dashboard | DashboardPage | StatsCards (total sessions, total test cases, avg per session), RecentSessionsList |
| /settings | SettingsPage | ProfileSettings, ChangePasswordForm |

---

## PHASE EXECUTION PLAN

### Phase 1: Foundation (4 agents in parallel)

**DATABASE-AGENT:**
- Create all SQLAlchemy models: User, RefreshToken, QASession, QAOutput
- Set up `database.py`, `alembic.ini`, initial migration
- Files: `backend/app/models/`, `backend/app/database.py`, `alembic/`

**BACKEND-AGENT:**
- Scaffold `main.py`, `config.py`, project structure
- Set up CORS, logging, health check endpoint
- Install dependencies: fastapi, sqlalchemy, alembic, anthropic, python-jose, passlib, httpx
- Files: `backend/app/main.py`, `backend/app/config.py`, `backend/requirements.txt`

**FRONTEND-AGENT:**
- Vite + React + TypeScript setup
- Folder structure: components/, pages/, hooks/, services/, context/, types/
- Base layout, routing (react-router-dom), Chakra UI provider
- Files: `frontend/src/`, `frontend/package.json`, `frontend/vite.config.ts`

**DEVOPS-AGENT:**
- `docker-compose.yml` (postgres, backend, frontend)
- `Dockerfile` for backend and frontend
- `.env.example`, `.gitignore`
- GitHub Actions CI: lint + test on push

**Validation Gate 1:**
```bash
cd backend && pip install -r requirements.txt && alembic upgrade head
cd frontend && npm install && npm run type-check
docker-compose config
```

---

### Phase 2: Modules (backend + frontend in parallel per module)

**Auth Module (parallel):**
- BACKEND-AGENT: JWT auth, bcrypt, Google OAuth, all auth endpoints
  - Files: `routers/auth.py`, `services/auth_service.py`, `schemas/auth.py`, `auth/`
- FRONTEND-AGENT: Login/Register pages, AuthContext, protected routes, Google OAuth button
  - Files: `pages/LoginPage.tsx`, `pages/RegisterPage.tsx`, `context/AuthContext.tsx`

**QA Session Module (parallel):**
- BACKEND-AGENT: Session CRUD endpoints, Claude API integration, background task for generation, CSV export
  - Files: `routers/sessions.py`, `services/session_service.py`, `services/ai_service.py`, `services/qa_prompt.py`, `schemas/session.py`
- FRONTEND-AGENT: Sessions list, new session form (multi-step), output viewer with tabs, polling logic, export button
  - Files: `pages/SessionsListPage.tsx`, `pages/NewSessionPage.tsx`, `pages/SessionOutputPage.tsx`, `components/output/`

**Dashboard Module:**
- FRONTEND-AGENT: Dashboard stats, recent sessions, settings page
  - Files: `pages/DashboardPage.tsx`, `pages/SettingsPage.tsx`

**Validation Gate 2:**
```bash
ruff check backend/ && mypy backend/
npm run lint && npm run type-check
```

---

### Phase 3: Quality (3 agents in parallel)

**TEST-AGENT:**
- pytest: auth tests, session CRUD tests, AI service mock tests, CSV export tests
- RTL: LoginForm, RegisterForm, NewSessionPage, SessionOutputPage, ChecklistTab
- Target: 80%+ backend coverage
- Files: `backend/tests/`, `frontend/src/__tests__/`

**REVIEW-AGENT:**
- Security: JWT secret strength, no hardcoded secrets, SQL injection check, input sanitization
- Performance: async endpoints verified, DB query optimization, no N+1
- Code quality: type hints everywhere, no `any` in TS, no `print()` in Python

**Final Validation:**
```bash
pytest --cov=app --cov-fail-under=80
npm test -- --coverage
docker-compose up -d && curl localhost:8000/health
```

---

## VALIDATION GATES

| Gate | Commands |
|------|----------|
| 1 – Foundation | `alembic upgrade head`, `npm install`, `docker-compose config` |
| 2 – Modules | `ruff check backend/`, `mypy backend/`, `npm run lint`, `npm run type-check` |
| 3 – Quality | `pytest --cov --cov-fail-under=80`, `npm test -- --coverage` |
| Final | `docker-compose up -d`, `curl localhost:8000/health` |

---

## FILE STRUCTURE

```
ai-qa-engine/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── session.py       # QASession + QAOutput
│   │   │   └── token.py
│   │   ├── schemas/
│   │   │   ├── auth.py
│   │   │   └── session.py
│   │   ├── routers/
│   │   │   ├── auth.py
│   │   │   └── sessions.py
│   │   ├── services/
│   │   │   ├── auth_service.py
│   │   │   ├── session_service.py
│   │   │   ├── ai_service.py
│   │   │   └── qa_prompt.py
│   │   └── auth/
│   │       ├── jwt.py
│   │       └── dependencies.py
│   ├── alembic/
│   ├── tests/
│   │   ├── test_auth.py
│   │   ├── test_sessions.py
│   │   └── test_ai_service.py
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── common/          # Button, Badge, LoadingSpinner
│       │   └── output/          # OutputTabs, TestCasesTable, ChecklistTab, etc.
│       ├── pages/
│       │   ├── LoginPage.tsx
│       │   ├── RegisterPage.tsx
│       │   ├── DashboardPage.tsx
│       │   ├── SessionsListPage.tsx
│       │   ├── NewSessionPage.tsx
│       │   ├── SessionOutputPage.tsx
│       │   └── SettingsPage.tsx
│       ├── hooks/
│       │   ├── useAuth.ts
│       │   └── useSession.ts
│       ├── services/
│       │   ├── api.ts
│       │   ├── authService.ts
│       │   └── sessionService.ts
│       ├── context/
│       │   └── AuthContext.tsx
│       └── types/
│           ├── auth.ts
│           └── session.ts
├── docker-compose.yml
├── .env.example
└── .github/
    └── workflows/
        └── ci.yml
```

---

## ENVIRONMENT VARIABLES

```env
# Backend
DATABASE_URL=postgresql://user:password@localhost:5432/ai_qa_engine
SECRET_KEY=your-secret-key-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
ANTHROPIC_API_KEY=your-anthropic-api-key

# Frontend
VITE_API_URL=http://localhost:8000
VITE_GOOGLE_CLIENT_ID=your-google-client-id
```

---

## AGENT DISPATCH SUMMARY

| Agent | Phase | Tasks | Key Files |
|-------|-------|-------|-----------|
| DATABASE-AGENT | 1 | Models, migrations | models/, alembic/ |
| BACKEND-AGENT | 1+2 | Scaffold, auth API, sessions API, AI service | routers/, services/ |
| FRONTEND-AGENT | 1+2 | Scaffold, auth UI, session UI, dashboard | pages/, components/ |
| DEVOPS-AGENT | 1 | Docker, CI/CD, env | docker-compose.yml, .github/ |
| TEST-AGENT | 3 | pytest, RTL, 80%+ coverage | tests/, __tests__/ |
| REVIEW-AGENT | 3 | Security, performance, quality | All files |

---

## NEXT STEP

Execute with parallel agents:
```bash
/execute-prp PRPs/ai-qa-engine-prp.md
```
