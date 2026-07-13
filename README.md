Naija Prep is a web app that helps students in Nigeria prepare for JAMB, WAEC, NECO, and Post-UTME. It provides subject/topic-based MCQ practice, a full JAMB CBT mock exam, a diagnostic placement test, progress tracking, and streak-based gamification.

## Tech stack (v2 — migrated from Flask/Jinja)

- **Backend**: FastAPI (Python), SQLAlchemy 2.0, JWT auth via httpOnly cookie, Pydantic schemas. SQLite for local dev, Postgres for production.
- **Frontend**: React + TypeScript, Vite, Tailwind CSS, React Router, TanStack Query.

The two are fully decoupled: the backend is a JSON REST API, the frontend is a single-page app that talks to it over HTTP.

## Project structure

```
Naija Prep/
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI app + router registration + CORS
│   │   ├── models.py          # SQLAlchemy models
│   │   ├── schemas.py         # Pydantic request/response schemas
│   │   ├── auth.py            # password hashing, JWT, cookie auth dependency
│   │   ├── database.py        # engine/session setup
│   │   ├── subjects.py        # canonical subject list
│   │   └── routers/           # auth, subjects, quiz, dashboard, review, admin
│   ├── seed_questions.py      # imports data/*.csv into the DB (safe, re-runnable)
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── pages/              # Home, Login, Register, Subjects, Quiz, Results, Dashboard, Review, Admin
│   │   ├── components/         # Layout (nav/footer), RequireAuth
│   │   ├── context/AuthContext.tsx
│   │   └── api/                # typed fetch client
│   ├── package.json
│   └── .env.example
└── data/                       # question bank CSVs (subject-agnostic of backend/frontend)
```

## Running it locally

### 1. Backend (FastAPI)

```
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux
pip install -r requirements.txt

copy .env.example .env        # already done for you; edit SECRET_KEY etc. if you like
python seed_questions.py      # loads data/*.csv into backend/naijaprep.db (SQLite)

uvicorn app.main:app --reload --port 8000
```

API docs (auto-generated): http://localhost:8000/docs

The **first account you ever register becomes an admin automatically** (can manage questions at `/admin` in the frontend). Promote additional admins by editing `is_admin` directly in the DB, or add a small script later if you need it often.

### 2. Frontend (React + Vite)

```
cd frontend
npm install
npm run dev
```

App runs at http://localhost:5173 and proxies `/api/*` requests to the backend on port 8000 (see `vite.config.ts`) — no CORS setup needed in dev.

### 3. Try it

Register a free account, take a quiz, check the dashboard for streaks/points, mark a question for review, and (as the first/admin user) visit `/admin` to add or edit questions directly instead of touching CSVs.

## Notes on this migration

- **Subscriptions/premium are disabled** (all subjects are free) per a deliberate product decision — the `Payment` model and Paystack plumbing exist in `backend/app/models.py` but nothing calls it yet. Re-enabling paid tiers is a matter of wiring gating checks back into the relevant routers, not rebuilding payment infrastructure.
- **Quiz state moved from server sessions to a database table** (`QuizAttempt`). This is a deliberate upgrade for the new stateless-API architecture: attempts are resumable, auditable, and don't depend on a server-side session cookie (only the JWT auth cookie is needed).
- **CBT mock exam, diagnostic test, and daily challenge** existed in the previous Flask version but have not yet been ported to the new API + frontend — the core practice loop (auth → subjects → quiz → results → dashboard → admin) was prioritized first. These are the next things to port.
- **Known data quality issue**: a handful of legacy questions in `data/mathsQuestions.csv` (present before this migration) have `exam_year` values that look like they contain explanation text instead of a year, and at least one question's `correct_option` doesn't match its own explanation. Worth an audit pass — flagging here so it isn't missed.

## Deployment

- **Backend**: any ASGI host (Render, Railway, Fly.io, etc.) running `uvicorn app.main:app`. Set `DATABASE_URL` to a Postgres connection string in production, and `FRONTEND_ORIGINS` to your deployed frontend's URL (required for CORS + cookies to work).
- **Frontend**: any static host (Vercel, Netlify, Render static site). Set `VITE_API_URL` to your deployed backend's URL at build time.
- Nothing has been pushed or deployed by Claude — this is staged locally only, per your instruction. You control git/hosting.

## License

MIT License. Built to help Nigerian students succeed in WAEC/JAMB/NECO.
