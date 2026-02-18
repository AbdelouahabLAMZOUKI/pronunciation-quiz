@echo off
echo ================================================
echo  Starting Pronunciation Quiz Web App
echo ================================================
echo.

REM Activate virtual environment
echo [1/3] Activating virtual environment...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    echo Please make sure .venv exists
    pause
    exit /b 1
)

REM Start backend server in a new window
echo [2/3] Starting backend server on http://localhost:8000/...
start "Backend Server" cmd /k "cd web_app\backend && uvicorn api.main:app --reload --host 0.0.0.0 --port 8000"
timeout /t 3 /nobreak >nul

REM Start frontend server in a new window  
echo [3/3] Starting frontend server on http://localhost:8001/...
start "Frontend Server" cmd /k "python web_app\serve_frontend.py"
timeout /t 2 /nobreak >nul

echo.
echo ================================================
echo  ✅ Both servers are starting!
echo ================================================
echo.
echo Backend API:  http://localhost:8000/api/health
echo Frontend App: http://localhost:8001/templates/index.html
echo.
echo Press any key to open the app in your browser...
pause >nul

start http://localhost:8001/templates/index.html

echo.
echo The app is now running!
echo Close the server windows to stop the app.
echo.
