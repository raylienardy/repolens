@echo off

:: 1. Docker version
docker --version

:: 2. List all containers
docker ps -a

:: 3. Ensure backend\.env exists (copy from example if missing)
if not exist "backend\.env" (
    if exist "backend\.env.example" (
        copy "backend\.env.example" "backend\.env"
        echo Copied backend\.env.example to backend\.env
    ) else (
        echo backend\.env.example not found; cannot create .env
    )
) else (
    echo backend\.env already exists
)

:: 4. Start only the DB service
docker-compose up -d db

:: 5. Wait for DB to start
timeout /t 10 >nul

:: 6. Show running containers
docker ps

:: 7. Wait for PostgreSQL to be ready (max 10 attempts, 3s interval)
set MAX_ATTEMPTS=10
set ATTEMPT=1
:check_loop
if %ATTEMPT% leq %MAX_ATTEMPTS% (
    echo Checking DB readiness (attempt %ATTEMPT%)
    docker exec repolens_db pg_isready -U repolens && goto after_check
    set /a ATTEMPT+=1
    timeout /t 3 >nul
    goto check_loop
)
:after_check

:: 8. List tables before app start
docker exec repolens_db psql -U repolens -d repolens -c "\dt"

:: 9. Start uvicorn in background, log to uvicorn.log
cd backend
start "uvicorn" cmd /c "uvicorn app.main:app --host 127.0.0.1 --port 8000 ^> ..\uvicorn.log 2^>^&1"
cd ..

:: 10. Wait for app to start
timeout /t 8 >nul

:: 11. Show uvicorn log
type uvicorn.log

:: 12. List tables after app start
docker exec repolens_db psql -U repolens -d repolens -c "\dt"

:: 13. Test health endpoint
curl -s http://127.0.0.1:8000/api/v1/health

:: 14. Kill uvicorn process (attempt to find by port)
for /f "tokens=5" %%a in ('netstat -ano ^| find ":8000" ^| find "LISTENING"') do taskkill /PID %%a /F

