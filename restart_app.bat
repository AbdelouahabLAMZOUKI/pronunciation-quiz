@echo off
echo ================================================
echo  Restarting Pronunciation Quiz Web App
echo ================================================
echo.

REM Kill existing servers
echo [1/4] Stopping existing servers...
echo Looking for processes on port 8000 and 8001...

REM Kill processes using PowerShell (more reliable)
powershell -Command "$ports = @(8000, 8001); foreach($port in $ports) { $conn = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue; if($conn) { foreach($c in $conn) { Stop-Process -Id $c.OwningProcess -Force -ErrorAction SilentlyContinue } } }"

REM Also try traditional method as backup
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do (
    taskkill /F /PID %%a >nul 2>&1
)

for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8001') do (
    taskkill /F /PID %%a >nul 2>&1
)

echo Servers stopped.
timeout /t 2 /nobreak >nul

REM Activate virtual environment
echo [2/4] Activating virtual environment...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    echo Please make sure .venv exists
    pause
    exit /b 1
)

REM Start backend server in a new window with --reload flag
echo [3/4] Starting backend server on http://localhost:8000/...
start "Backend Server" cmd /k "cd web_app\backend && uvicorn api.main:app --reload --host 0.0.0.0 --port 8000"
timeout /t 3 /nobreak >nul

REM Start frontend server in a new window  
echo [4/4] Starting frontend server on http://localhost:8001/...
start "Frontend Server" cmd /k "python web_app\serve_frontend.py"
timeout /t 2 /nobreak >nul

echo.
echo ================================================
echo  ✅ Servers restarted successfully!
echo ================================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:8001/templates/index.html
echo.
echo Note: Backend now has auto-reload enabled!
echo It will automatically restart when you edit Python files.
echo.
pause
