@echo off
REM AI Factory Deployment Script for Windows (3090 PC)
REM Run this from the ai-factory directory

echo ========================================
echo    AI Factory Deployment Script
echo ========================================
echo.

REM Check Docker is running
docker info >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ERROR: Docker is not running. Please start Docker Desktop.
    pause
    exit /b 1
)

REM Check for .env file
if not exist .env (
    echo Creating .env from template...
    copy .env.template .env
    echo IMPORTANT: Edit .env with your API keys before continuing!
    notepad .env
    pause
)

REM Create data directories
echo Creating data directories...
if not exist "C:\ai-factory\data" mkdir "C:\ai-factory\data"

REM Pull latest images
echo Pulling Docker images (this may take a while)...
docker compose pull

REM Start core services
echo.
echo Starting core AI Factory services...
docker compose up -d vectorgraph-db embeddings letta-server cocoindex

echo.
echo Waiting for services to initialize...
timeout /t 30

REM Check service health
echo.
echo Checking service status...
docker compose ps

echo.
echo ========================================
echo    AI Factory Deployment Complete!
echo ========================================
echo.
echo Services running:
echo   - VectorGraph DB:  http://localhost:5432
echo   - Embeddings API:  http://localhost:8080
echo   - Letta Server:    http://localhost:8283
echo   - CocoIndex:       http://localhost:8081
echo.
echo From your MacBook (via WireGuard):
echo   - VectorGraph DB:  postgresql://vectorgraph:vectorgraph_secret@10.0.0.3:5432/ai_factory
echo   - Letta Server:    http://10.0.0.3:8283
echo.
echo To start optional services (Qdrant, LiteLLM):
echo   docker compose --profile full up -d
echo.
echo To view logs:
echo   docker compose logs -f
echo.
pause
