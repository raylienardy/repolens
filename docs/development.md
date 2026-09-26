# Local Development Guide

## Prerequisites
- Node.js 18+
- Python 3.10+
- Docker (Optional)

## Running Backend
```bash
cd backend
python -m venv venv
# Activate venv
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Running Frontend
```bash
cd frontend
npm install
npm run dev
```
