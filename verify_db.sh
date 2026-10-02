#!/usr/bin/env bash

# 1. Docker version
docker --version

# 2. List all containers
docker ps -a

# 3. Ensure backend/.env exists (copy from example if missing)
if [ ! -f "backend/.env" ]; then
  if [ -f "backend/.env.example" ]; then
    cp "backend/.env.example" "backend/.env"
    echo "Copied backend/.env.example to backend/.env"
  else
    echo "backend/.env.example not found; cannot create .env"
  fi
else
  echo "backend/.env already exists"
fi

# 4. Start only the DB service
docker-compose up -d db

# 5. Wait for DB to start
sleep 10

# 6. Show running containers
docker ps

# 7. Wait for PostgreSQL to be ready (max 10 attempts, 3s interval)
MAX_ATTEMPTS=10
ATTEMPT=1
while [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
  echo "Checking DB readiness (attempt $ATTEMPT)"
  docker exec repolens_db pg_isready -U repolens && break
  ATTEMPT=$((ATTEMPT+1))
  sleep 3
done

# 8. List tables before app start
docker exec repolens_db psql -U repolens -d repolens -c "\dt"

# 9. Start uvicorn in background, log to uvicorn.log
cd backend
uvicorn app.main:app --host 127.0.0.1 --port 8000 > ../uvicorn.log 2>&1 &
UVICORN_PID=$!
cd ..

# 10. Wait for app to start
sleep 8

# 11. Show uvicorn log
cat uvicorn.log

# 12. List tables after app start
docker exec repolens_db psql -U repolens -d repolens -c "\dt"

# 13. Test health endpoint
curl -s http://127.0.0.1:8000/api/v1/health

# 14. Kill uvicorn process if still running
if kill -0 $UVICORN_PID 2>/dev/null; then
  kill $UVICORN_PID
  echo "uvicorn process $UVICORN_PID terminated"
else
  echo "uvicorn process not running"
fi
