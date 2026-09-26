# RepoLens Architecture Overview

## High-Level Diagram

```
[ Frontend (Next.js) ] <---> [ Backend (FastAPI) ] <---> [ PostgreSQL ]
                                     |
                                     v
                             [ GitHub API / AI ]
```

## Components
- **Frontend**: Next.js 15 App Router, TypeScript, TailwindCSS.
- **Backend**: FastAPI, Async SQLAlchemy, Pydantic v2.
- **Database**: PostgreSQL for caching and store analysis logs.
