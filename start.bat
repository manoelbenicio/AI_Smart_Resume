@echo off
setlocal enabledelayedexpansion
title Smart AI Resume — Bootstrap v2
color 0A
cd /d "d:\VMs\Projetos\Smart_AI_Resume"

echo.
echo  ========================================================
echo   Smart AI Resume — Executive Benchmark Engine v0.4.0
echo  ========================================================
echo.

:: ─── STEP 1: Check Docker ───────────────────────────────────
echo  [1/6] Checking Docker...
docker info >nul 2>&1
if !errorlevel! neq 0 (
    echo         Docker not running. Attempting to start...
    start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe" 2>nul
    echo         Waiting 45s for Docker daemon...
    for /L %%i in (1,1,9) do (
        timeout /t 5 /nobreak >nul
        docker info >nul 2>&1
        if !errorlevel! equ 0 (
            echo         Docker started.
            goto :docker_ok
        )
        echo         Still waiting... %%i/9
    )
    echo.
    echo  [FAIL] Docker did not start after 45 seconds.
    echo         Please start Docker Desktop manually then re-run.
    echo.
    goto :dashboard
)
:docker_ok
echo         OK — Docker is running.

:: ─── STEP 2: Start containers ───────────────────────────────
echo.
echo  [2/6] Starting PostgreSQL + API containers...
docker compose up -d 2>&1
echo         Waiting 8s for containers to initialize...
timeout /t 8 /nobreak >nul
echo         Containers started.

:: ─── STEP 3: Check API health ───────────────────────────────
echo.
echo  [3/6] Checking API health...
set API_OK=NO
for /L %%i in (1,1,6) do (
    curl -s -o nul -w "%%{http_code}" http://localhost:8000/health >"%TEMP%\api_check.txt" 2>nul
    set /p API_CODE=<"%TEMP%\api_check.txt"
    if "!API_CODE!"=="200" (
        set API_OK=YES
        goto :api_done
    )
    echo         Attempt %%i/6 — waiting 5s...
    timeout /t 5 /nobreak >nul
)
:api_done
if "!API_OK!"=="YES" (
    echo         OK — API responding on port 8000.
) else (
    echo         WARN — API not responding yet. Check docker logs.
)

:: ─── STEP 4: Check PostgreSQL ───────────────────────────────
echo.
echo  [4/6] Checking PostgreSQL...
set PG_OK=NO
docker compose exec -T postgres pg_isready -U smartuser >nul 2>&1
if !errorlevel! equ 0 (
    set PG_OK=YES
    echo         OK — PostgreSQL accepting connections on port 5432.
) else (
    echo         WARN — PostgreSQL not ready. Check docker compose logs postgres.
)

:: ─── STEP 5: Start frontend ─────────────────────────────────
echo.
echo  [5/6] Starting Next.js frontend...

:: Check if port 3000 is already in use
netstat -an 2>nul | findstr ":3000.*LISTENING" >nul 2>&1
if !errorlevel! equ 0 (
    echo         OK — Frontend already running on port 3000.
    set FE_OK=YES
    goto :fe_done
)

:: Ensure node_modules exist
if not exist "frontend\node_modules\" (
    echo         Installing npm dependencies (first run)...
    cd /d "d:\VMs\Projetos\Smart_AI_Resume\frontend"
    call npm install
    cd /d "d:\VMs\Projetos\Smart_AI_Resume"
)

:: Launch frontend in a separate window
start "Smart Resume Frontend (port 3000)" cmd /k "cd /d d:\VMs\Projetos\Smart_AI_Resume\frontend && title Frontend - localhost:3000 && npm run dev"
echo         Waiting 8s for frontend to compile...
timeout /t 8 /nobreak >nul

set FE_OK=NO
netstat -an 2>nul | findstr ":3000.*LISTENING" >nul 2>&1
if !errorlevel! equ 0 (
    set FE_OK=YES
    echo         OK — Frontend running on port 3000.
) else (
    echo         WARN — Frontend may still be compiling. Check its window.
)
:fe_done

:: ─── STEP 6: Open browser ───────────────────────────────────
echo.
echo  [6/6] Opening browser...
timeout /t 2 /nobreak >nul
start http://localhost:3000

:: ─── DASHBOARD ──────────────────────────────────────────────
:dashboard
echo.
echo  ========================================================
echo          SERVICE HEALTH DASHBOARD
echo  ========================================================
echo.

:: Docker status
docker info >nul 2>&1
if !errorlevel! equ 0 (
    echo    [OK]   Docker Engine           running
) else (
    echo    [FAIL] Docker Engine           NOT RUNNING
)

:: Container status
for /f "tokens=*" %%c in ('docker compose ps --format "{{.Name}} {{.Status}}" 2^>nul') do (
    echo    [  ]   Container: %%c
)

:: API
curl -s http://localhost:8000/health >"%TEMP%\health.txt" 2>nul
if !errorlevel! equ 0 (
    set /p HEALTH=<"%TEMP%\health.txt"
    echo    [OK]   Backend API :8000       !HEALTH!
) else (
    echo    [FAIL] Backend API :8000       NOT RESPONDING
)

:: Swagger
curl -s -o nul -w "%%{http_code}" http://localhost:8000/docs >"%TEMP%\swagger.txt" 2>nul
set /p SWAGGER=<"%TEMP%\swagger.txt"
if "!SWAGGER!"=="200" (
    echo    [OK]   Swagger UI  :8000/docs  HTTP 200
) else (
    echo    [FAIL] Swagger UI  :8000/docs  HTTP !SWAGGER!
)

:: PostgreSQL
docker compose exec -T postgres pg_isready -U smartuser >nul 2>&1
if !errorlevel! equ 0 (
    echo    [OK]   PostgreSQL  :5432       accepting connections
) else (
    echo    [FAIL] PostgreSQL  :5432       NOT READY
)

:: Frontend
netstat -an 2>nul | findstr ":3000.*LISTENING" >nul 2>&1
if !errorlevel! equ 0 (
    echo    [OK]   Frontend    :3000       running
) else (
    echo    [WARN] Frontend    :3000       check frontend window
)

echo.
echo  ========================================================
echo    URLs:
echo      App:      http://localhost:3000
echo      API:      http://localhost:8000
echo      Swagger:  http://localhost:8000/docs
echo  ========================================================
echo.
echo    Press any key to close this window.
echo    (Services will keep running in the background)
echo.
pause >nul
