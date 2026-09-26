# RepoLens

RepoLens is a tool to analyze public GitHub repositories and provide summaries and insights.

## Project Structure
- `backend/`: FastAPI application
- `frontend/`: Next.js application
- `docs/`: Documentation and ADRs

## Prerequisites
- Docker & Docker Compose
- Python 3.10+
- Node.js 18+

## Getting Started

### Local Development
1. Clone the repository.
2. Copy `.env.example` to `.env` in root, backend, and frontend folders.
3. Start backend:
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```
4. Start frontend:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

### Using Docker
```bash
docker-compose up --build
```

## API Documentation
Once the backend is running, visit `http://localhost:8000/docs` for the Swagger UI.
