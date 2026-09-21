# Midnight ATS Resume Builder

A resume builder + ATS (Applicant Tracking System) compatibility analyzer. Upload an existing
resume, edit it in a structured 3-panel editor, tailor it against a job description with AI
assistance (fact-locked, no fabrication), and export a validated, true-text, one-page PDF/DOCX.

## Architecture

- **Backend**: Python 3.12 + FastAPI, SQLAlchemy 2.0, Alembic migrations, MySQL.
- **Frontend**: React 19 + TypeScript + Vite + Tailwind CSS v4, Zustand, dnd-kit, React Hook Form.
- **AI**: Provider-agnostic (`app/ai/base.py: AIProvider`); only Groq is wired up today.
- **Parsing**: PyMuPDF (PDF), python-docx (DOCX/TXT) — deterministic, no AI in the parse path.
- **PDF export**: Jinja2 → WeasyPrint (true text-based PDF, never an image).
- **DOCX export**: built natively from the resume JSON via python-docx.
- **ATS scoring**: deterministic weighted formula (`app/ats/scorer.py`) — never AI-generated.

See `.claude`-independent architecture notes inline in `backend/app/` docstrings; the original
implementation plan is also a useful reference for the reasoning behind each layer.

## Repository layout

```
backend/
  app/
    api/v1/        FastAPI routers
    services/       business logic
    repositories/   SQLAlchemy data access
    models/         ORM entities
    schemas/        Pydantic DTOs (camelCase on the wire)
    parser/         PDF/DOCX/TXT → structured resume JSON
    ats/            keyword matching, scoring, parsing simulator, link/section validation
    ai/             AIProvider interface + Groq adapter + prompts
    pdf/            HTML/PDF renderer, DOCX renderer, one-page optimizer, filename generator
    security/       JWT + password hashing
    exceptions/     structured error handling
  alembic/          DB migrations
  templates/        Jinja2 resume template (shared by live preview AND PDF export)
  tests/            pytest suite (parser, ATS scorer, PDF export, API integration)
frontend/
  src/
    components/     UI + section editors + ATS panel
    pages/          route-level pages
    store/          Zustand stores (auth, resume editor with debounced autosave)
    services/       axios API client
    types/          TypeScript types mirroring the backend schemas
docker-compose.yml  MySQL + backend + frontend
```

## Environment setup

### Prerequisites

- Python 3.12+
- Node.js 20+
- MySQL 8 (or use `docker-compose up db`)
- **Windows only**: WeasyPrint needs the GTK3 runtime. Install with:
  `winget install --id tschoonj.GTKForWindows -e` (adds the required DLLs to PATH).
  Not needed on Linux/Docker — `backend/Dockerfile` installs the equivalent `apt` packages.

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux
pip install -r requirements.txt
copy .env.example .env          # then fill in DATABASE_URL and GROQ_API_KEY
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

Env vars (see `backend/.env.example`):

- `ENVIRONMENT` — `development` or `production`. In production this **refuses to start** if
  `JWT_SECRET_KEY` is still the placeholder value, and auto-disables `/docs`, `/redoc`, and
  `/openapi.json` (override with `ENABLE_DOCS=true` if you want them exposed anyway).
- `DATABASE_URL` — MySQL connection string.
- `JWT_SECRET_KEY` — generate a real one for anything beyond local dev: `openssl rand -hex 32`.
- `AI_PROVIDER` — `groq` (only implemented provider today).
- `GROQ_API_KEY` — required for "Analyze JD" and "Optimize Resume"; everything else
  (upload/parse/edit/ATS-score-without-JD/export) works without it.
- `LOG_FORMAT` — `text` (readable, local dev) or `json` (one JSON object per line, for a log
  aggregator).
- `LOGIN_RATE_LIMIT` / `REGISTER_RATE_LIMIT` — throttles brute-force attempts against auth
  endpoints (spec §37), format `"<count>/<period>"` e.g. `10/minute`.

### Frontend

```bash
cd frontend
npm install
copy .env.example .env          # VITE_API_BASE_URL, default http://localhost:8000/api/v1
npm run dev
```

Open http://localhost:5173.

### Database setup

```bash
docker-compose up db          # or point DATABASE_URL at your own MySQL instance
cd backend
alembic upgrade head
```

### Full stack via Docker Compose

```bash
cp backend/.env.example backend/.env   # fill in GROQ_API_KEY
docker-compose up --build
```

Backend: http://localhost:8000 (interactive docs at `/docs`). Frontend: http://localhost:5173.

## Production deployment

This has been run and manually verified locally (backend + frontend + real Groq calls, browser-
driven end to end) but **not** against a real MySQL instance or a real domain/TLS setup — no
Docker was available in the environment this was built in. Before deploying for real:

1. **Secrets**: set `ENVIRONMENT=production`, a real `JWT_SECRET_KEY` (the app refuses to start
   without one in production), and a real `GROQ_API_KEY` in `backend/.env`. Never commit `.env`
   (already gitignored).
2. **Database**: point `DATABASE_URL` at a real, backed-up MySQL instance, then run
   `alembic upgrade head`. `docker-compose.yml`'s `db` service is for local dev only — bring
   your own managed MySQL (RDS, Cloud SQL, etc.) in production.
3. **TLS**: put a reverse proxy (nginx, Caddy, Traefik, or your cloud LB) in front of both
   `backend` (port 8000) and `frontend` (port 5173) and terminate HTTPS there — neither
   container serves TLS itself. Update `CORS_ORIGINS` and the frontend's `VITE_API_BASE_URL`
   build arg to your real domain.
4. **Rate limiting**: `slowapi`'s default in-memory store is per-process — fine for a single
   backend instance, but if you scale to multiple replicas, back it with Redis (`slowapi`
   supports it) so limits are shared across instances.
5. **Logging**: set `LOG_FORMAT=json` and ship stdout to your log aggregator.
6. **Health checks**: `/health` checks real DB connectivity and returns `"degraded"` (still
   `200`, so it doesn't flap a load balancer on a blip) if the database is unreachable — wire
   your monitoring to alert on that field, not just the HTTP status.
7. Re-run the full test suite (`pytest tests/ -v`) and a build (`npm run build`) against your
   actual production config before rolling out.

## Testing

```bash
cd backend
pytest tests/ -v
```

50+ tests covering: parser field/section/date extraction (against a real resume fixture and a
synthetic edge-case resume), the ATS scoring formula (including boundary-safe keyword matching
and JD synonym de-duplication), PDF generation (page count, text extractability, one-page
auto-optimization, clickable brand-colored links in both PDF and DOCX), filename generation,
rate limiting (a real subprocess-isolated 429 test, not just wiring checks), production config
safety (refuses an insecure JWT secret when `ENVIRONMENT=production`), and the full API
lifecycle (register → upload → edit → ATS analyze → validate → export → diff).

Frontend:

```bash
cd frontend
npx tsc --noEmit -p tsconfig.app.json   # typecheck
npm run build                            # production build
```

## Deliberate deviations from a from-scratch spec

Built per explicit direction to use Python/FastAPI (not Java/Spring Boot) and Groq (not
OpenAI/Anthropic/Ollama, though the `AIProvider` interface supports adding them later without
touching call sites).

## Known scope limits

Deferred, not forgotten — flagged here so they're not mistaken for oversights:

- Only Groq is wired up behind `AIProvider`; OpenAI/Anthropic/Ollama adapters are not implemented.
- Only one visual template ("Professional ATS — One Page") ships; the template engine supports
  more, but Modern/Minimal/Executive templates aren't built.
- Section content editors use plain textareas, not a rich-text editor (TipTap) — full
  editability is intact, just not WYSIWYG-rich.
- No fine-grained keyword-stuffing UI beyond the basic repetition warning already surfaced in
  the ATS panel; no RBAC beyond a single "user" role; DOCX round-trip parsing isn't covered by
  the automated test suite (DOCX export itself is).
- Rate limiting's in-memory store isn't shared across replicas — fine for one backend instance,
  needs a Redis backend before horizontal scaling (see Production Deployment above).
- No dark mode; the UI is a hand-built Tailwind design system rather than the shadcn/ui CLI
  scaffold (same visual quality bar, without the CLI's registry dependency).
- Never run against real MySQL or behind real TLS — validated with SQLite locally and the
  migration itself round-trips cleanly, but treat the "Production deployment" checklist above
  as mandatory, not optional, before going live.

## Core flow

1. Register/log in.
2. Upload a resume (PDF/DOCX/TXT) → parsed deterministically into the Master Resume.
3. Edit any field in the 3-panel editor (left: draggable section list, center: structured
   editor / live preview tabs, right: ATS panel).
4. Paste a job description → "Analyze JD".
5. "Optimize Resume" → review the AI's suggested summary/bullet changes (diff-style
   Accept/Reject/Accept All) — nothing is applied until accepted, and locked fields (name,
   contact info, employment history, education, certifications) can never be touched by the AI.
6. "Run ATS Analysis" for the weighted compatibility score and keyword gap breakdown.
7. "Export PDF" / "Export DOCX" — blocked by a quality gate until the resume passes (exactly
   one page, all key fields re-parseable from the generated file, valid links) with an
   automatic one-page optimization pass run first.
8. Company-specific filenames (`FirstName_LastName_Company_Role.pdf`) and version comparison
   (Master vs. tailored version diff) are available from the Dashboard.
