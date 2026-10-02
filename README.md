# RepoLens

> Analyze any public GitHub repository and understand it in seconds — structure, tech stack, dependencies, tests, and AI-generated explanation, all evidence-based.

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.117-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-15-000000?logo=next.js&logoColor=white)](https://nextjs.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-18-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

---

## Table of Contents

- [Why RepoLens](#why-repolens)
- [What it does](#what-it-does)
- [Demo](#demo)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [API Reference](#api-reference)
- [Design Decisions](#design-decisions)
- [Testing](#testing)
- [Known Limitations](#known-limitations)
- [Roadmap](#roadmap)

---

## Why RepoLens

Understanding an unfamiliar repository usually means cloning it, opening 20 files, and reading until the picture becomes clear. GitHub's UI gives you a file tree and a README, but it doesn't tell you:

- What the project actually does
- Which technologies it uses — and _where_ it uses them
- How the code is organized
- What tests exist, and how complete they are
- Which files to read first

**RepoLens** answers those questions for any public GitHub repo in one request. Paste a URL, get a structured report.

---

## What it does

RepoLens performs **deterministic static analysis** on a repository, then uses an LLM to explain the results in plain language.

**Deterministic analysis (no AI involved):**

- **Repository overview** — stars, forks, license, default branch, primary language
- **Structure** — file/directory counts, top-level entries, depth, folder conventions (`backend/`, `frontend/`, `docs/`, `tests/`)
- **Languages** — extension breakdown + GitHub-reported primary language
- **Dependencies** — parses `package.json`, `pyproject.toml`, `requirements.txt`, `Cargo.toml`, `go.mod`, and more
- **Frameworks** — detects FastAPI, Django, Flask, Express, Next.js, React, Vue, Svelte, SQLAlchemy, Prisma, pytest, Jest, Vitest, and more — with the manifest file that proves it
- **Testing** — test folder, test files, test config, CI workflow
- **Documentation** — README, LICENSE, CHANGELOG, CONTRIBUTING, docs folder size
- **Configuration** — Dockerfile, docker-compose, CI workflows, `.env.example`, Makefile
- **Security signals** — SECURITY.md, Dependabot, `.gitignore`, LICENSE (signals only — no vulnerability scanning)
- **Entry points** — `main.py`, `app.py`, `applications.py`, `__main__.py`, `wsgi.py`, `index.ts`, `main.go`, `main.rs`, and more

**AI explanation:**

Given the deterministic facts above, RepoLens asks the LLM to produce a structured explanation: summary, purpose, key technologies, architecture notes, notable findings, and improvement suggestions. The prompt explicitly forbids the model from inventing information that is not in the facts.

---

## Demo

> [GANTI: tambahkan screenshot dashboard di sini]
>
> Contoh: analisis `fastapi/fastapi` menampilkan 3.181 file, 19 dependency, 653 test file, dan 3 entry point — lengkap dengan penjelasan AI.

Coba sendiri:

```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"repo_url": "https://github.com/pallets/flask"}'
```

---

## Architecture

```mermaid
flowchart TD
    FE[Next.js Frontend] -->|POST /api/v1/analyze| API[FastAPI Router]
    API --> ORCH[Orchestrator]

    ORCH -->|parse URL| URL[GitHub URL Parser]
    ORCH -->|check cache| DB[(PostgreSQL)]
    ORCH -->|fetch metadata + tree + files| GH[GitHub API Client]

    GH --> ANALYZERS[9 Deterministic Analyzers]
    ANALYZERS --> FACTS[Structured Facts]

    FACTS --> PROMPT[Prompt Builder]
    PROMPT --> AI[AI Provider]
    AI -->|OpenAI-compatible<br/>or mock| RESULT[AI Explanation]

    FACTS --> CACHE[Cache Writer]
    RESULT --> CACHE
    CACHE --> DB

    ORCH --> RESP[AnalysisResponse]
    RESP --> FE

    style DB fill:#ff9,stroke:#333
    style FACTS fill:#bfb,stroke:#333
    style AI fill:#bbf,stroke:#333
```

The pipeline is:

1. **Parse and validate** the GitHub URL
2. **Check cache** — if the same repo at the same commit SHA was analyzed in the last 7 days, return it
3. **Fetch** repo metadata, the full file tree (up to 15,000 entries), and up to 20 priority files
4. **Run 9 analyzers** on the fetched data → produce structured facts
5. **Build a prompt** from those facts only
6. **Call the AI provider** — if it fails, return the deterministic analysis anyway
7. **Save to cache**, return the response

---

## Tech Stack

| Layer       | Technology                                      |
| ----------- | ----------------------------------------------- |
| Backend     | FastAPI, Python 3.12, Pydantic v2               |
| Database    | PostgreSQL 18, SQLAlchemy async, Alembic        |
| HTTP client | httpx (async)                                   |
| Frontend    | Next.js 15, React, TypeScript, Tailwind CSS v4  |
| AI          | Provider abstraction — OpenAI-compatible + mock |
| Deployment  | Docker, Docker Compose                          |
| Testing     | pytest, pytest-asyncio                          |

---

## Getting Started

### Prerequisites

- Docker & Docker Compose (recommended)
- **or** Python 3.12+, Node.js 18+, and a running PostgreSQL instance

### Option 1 — Docker (recommended)

```bash
git clone https://github.com/raylienardy/repolens.git
cd repolens

# Copy environment templates
cp .env.example .env
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local

# (Optional but recommended) add a GitHub token for higher rate limits
# Edit backend/.env and set GITHUB_TOKEN=ghp_...

docker compose up --build
```

Open http://localhost:3000.

### Option 2 — Local development

**Backend:**

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Start PostgreSQL (via Docker is easiest)
docker compose up -d db

# Run migrations
alembic upgrade head

# Start API
uvicorn app.main:app --reload
```

API docs available at http://localhost:8000/docs.

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000.

---

## Environment Variables

### Backend (`backend/.env`)

| Variable       | Required               | Default                     | Description                                                                                 |
| -------------- | ---------------------- | --------------------------- | ------------------------------------------------------------------------------------------- |
| `DATABASE_URL` | yes                    | —                           | PostgreSQL connection string, e.g. `postgresql+asyncpg://user:pass@localhost:5433/repolens` |
| `GITHUB_TOKEN` | no                     | —                           | GitHub Personal Access Token. Raises rate limit from 60/h to 5,000/h.                       |
| `AI_PROVIDER`  | no                     | `mock`                      | `mock` or `openai_compatible`                                                               |
| `AI_API_KEY`   | only for real provider | —                           | API key for the AI provider                                                                 |
| `AI_BASE_URL`  | only for real provider | —                           | OpenAI-compatible base URL, e.g. `https://api.openai.com/v1`                                |
| `AI_MODEL`     | only for real provider | —                           | Model name, e.g. `gpt-4o-mini`                                                              |
| `CORS_ORIGINS` | no                     | `["http://localhost:3000"]` | JSON list of allowed origins                                                                |
| `LOG_LEVEL`    | no                     | `INFO`                      | Python log level                                                                            |
| `DEBUG`        | no                     | `True`                      | SQLAlchemy echo + FastAPI debug mode                                                        |

### Frontend (`frontend/.env.local`)

| Variable              | Required | Description                                    |
| --------------------- | -------- | ---------------------------------------------- |
| `NEXT_PUBLIC_API_URL` | yes      | Backend base URL, e.g. `http://localhost:8000` |

---

## API Reference

### `POST /api/v1/analyze`

Analyze a public GitHub repository.

**Request:**

```json
{
  "repo_url": "https://github.com/pallets/flask"
}
```

**Response** (truncated):

```json
{
  "repo_url": "https://github.com/pallets/flask",
  "repo_full_name": "pallets/flask",
  "commit_sha": "d73fa1cdcbd8b1465c151db8924ba58b1dd14e35",
  "from_cache": false,
  "analyzed_at": "2026-10-02T14:28:20.459275Z",
  "analysis": {
    "repository": {
      "stars": 74793,
      "forks": 17034,
      "license": "BSD-3-Clause",
      "...": "..."
    },
    "languages": {
      "primary": "Python",
      "detected": { ".py": 83, ".rst": 79, "...": 0 },
      "source": "both"
    },
    "structure": { "total_files": 236, "total_directories": 51, "...": "..." },
    "dependencies": {
      "has_manifest": true,
      "manifest_files": ["pyproject.toml"],
      "ecosystems": ["python"],
      "total_count": 24
    },
    "frameworks": {
      "detected": [
        {
          "name": "Flask",
          "category": "backend",
          "evidence": "found in pyproject.toml",
          "confidence": "high"
        },
        {
          "name": "pytest",
          "category": "testing",
          "evidence": "found in pyproject.toml",
          "confidence": "high"
        }
      ]
    },
    "testing": {
      "has_tests_folder": true,
      "test_files_count": 61,
      "...": "..."
    },
    "entry_points": {
      "found": [
        {
          "path": "src/flask/app.py",
          "kind": "python_app",
          "evidence": "found app.py in src/flask/"
        }
      ]
    }
  },
  "ai": {
    "status": "ok",
    "provider": "mock",
    "model": "mock-v1",
    "explanation": {
      "summary": "...",
      "purpose": "...",
      "key_technologies": ["Flask", "pytest", "Python"],
      "architecture_notes": "...",
      "notable_findings": ["..."],
      "improvement_suggestions": ["..."],
      "inference_disclaimer": "..."
    }
  }
}
```

**Error responses:**

| Status | Reason                          |
| ------ | ------------------------------- |
| `422`  | Invalid GitHub URL              |
| `403`  | Repository is private           |
| `404`  | Repository not found            |
| `413`  | Repository too large (>100 MiB) |
| `429`  | GitHub rate limit exceeded      |
| `502`  | Generic GitHub API error        |

### `GET /api/v1/health`

```json
{
  "status": "ok",
  "app": "RepoLens API",
  "version": "0.1.0",
  "env": "development"
}
```

---

## Design Decisions

### 1. Deterministic analysis first, AI second

RepoLens does not ask the LLM to read raw repository code. It runs deterministic analyzers that produce structured facts, then asks the LLM only to **explain those facts in natural language**. The prompt explicitly forbids invention.

**Why:** LLMs hallucinate. If we let the model read code directly, we would get confident-sounding but unreliable claims. By giving the model only verified facts, we keep its output grounded.

### 2. Cache keyed by commit SHA

Analysis is cached by `(repo_full_name, commit_sha)` with a 7-day TTL, not by URL.

**Why:** Two different URLs can point to the same repo (e.g. `tiangolo/fastapi` and `fastapi/fastapi`). And a repo's content changes over time — but a specific commit is immutable. Caching by commit SHA gives correct results and avoids re-analysis when the code hasn't changed.

### 3. AI failure is not analysis failure

If the AI provider times out or errors, RepoLens returns the full deterministic analysis with `ai.status = "error"` and a friendly message. The user still gets value.

**Why:** Developer tools should degrade gracefully. The LLM is an enhancement, not a dependency.

### 4. Only analyze, never execute

RepoLens fetches file _content_ via the GitHub Contents API and parses it as text. It never clones, installs, or runs code from the target repository.

**Why:** Running untrusted code is a security and resource risk. Static analysis is enough for the questions RepoLens answers.

### 5. Pluggable AI provider

AI providers implement a small `AIProvider` protocol. The factory supports `mock` (deterministic, no network) and `openai_compatible` (any OpenAI-compatible chat endpoint). Adding a new provider means writing one class.

**Why:** AI vendors change. Locking the codebase to one vendor's SDK creates unnecessary coupling.

---

## Testing

Backend tests live in `backend/tests/`:

```bash
cd backend
pytest -v
```

The suite covers:

- URL parsing and validation (`tests/unit/test_github_urls.py`)
- Tree selectors (`tests/unit/test_github_selectors.py`)
- Analysis engine (`tests/unit/test_analysis_engine.py`)
- Orchestrator end-to-end with mocked GitHub (`tests/integration/test_orchestrator.py`)
- Mock AI provider (`tests/integration/test_ai_mock_provider.py`)

---

## Known Limitations

RepoLens is honest about what it does not do:

- **Public repositories only.** Private repositories return `403`.
- **Rate-limited without a token.** Unauthenticated GitHub API allows 60 requests/hour, which is enough for roughly 3–5 full analyses. Provide `GITHUB_TOKEN` for real usage.
- **Bounded analysis.** RepoLens fetches up to 20 priority files with a 500 KB total content limit. Repositories larger than 100 MiB are rejected.
- **The testing analyzer counts files inside `tests/`, not only files matching test patterns.** This can overcount fixtures and templates.
- **AI output is interpretation, not verification.** Even with fact-only prompts, LLMs can misinterpret. Treat the AI section as a _starting point_, and always verify against the deterministic facts.
- **No authentication on the API.** The public endpoint is open. Add an API key or auth layer before exposing RepoLens to the open internet.
- **No cache eviction job.** Expired cache rows are ignored on read but not deleted. For long-running deployments, add a periodic cleanup task.

---

## Roadmap

- [ ] Add progress feedback during analysis (fetching → analyzing → explaining)
- [ ] Support private repositories via OAuth
- [ ] Improve testing analyzer to distinguish test files from fixtures
- [ ] Add structured cache cleanup job
- [ ] Support batch analysis (multiple URLs)
- [ ] Add Prometheus metrics
- [ ] Add API key authentication
- [ ] Support GitLab and Bitbucket

---

## License

[GANTI: pilih lisensi — mis. MIT. Buat file `LICENSE` di root repo.]
