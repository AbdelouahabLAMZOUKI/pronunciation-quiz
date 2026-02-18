@echo off
echo ================================================
echo  Diagnosing Pronunciation Quiz Issues
echo ================================================
echo.

REM Activate virtual environment
call .venv\Scripts\activate.bat

echo [1/5] Checking if backend is running...
python -c "import requests; r = requests.get('http://localhost:8000/api/health', timeout=2); print('✅ Backend is UP -', r.json())" 2>nul
if errorlevel 1 (
    echo ❌ Backend is NOT responding on port 8000
    echo.
    echo SOLUTION: Run restart_app.bat
    goto :end
)

echo.
echo [2/5] Testing quiz endpoint...
python -c "import requests; r = requests.post('http://localhost:8000/api/quiz/new-word?session_id=test', timeout=2); print('Status:', r.status_code); print('Has word:', 'word' in r.json())" 2>nul
if errorlevel 1 (
    echo ❌ Quiz endpoint failed
    goto :end
)

echo.
echo [3/5] Testing features endpoint...
python -c "import requests; r = requests.get('http://localhost:8000/api/features', timeout=2); print('Status:', r.status_code); data = r.json(); print('Features found:', data.get('count', 0))" 2>nul
if errorlevel 1 (
    echo ❌ Features endpoint failed
    goto :end  
)

echo.
echo [4/5] Testing contractions feature...
python -c "import requests; r = requests.get('http://localhost:8000/api/features/contractions', timeout=2); print('Status:', r.status_code); print('Has contractions:', r.status_code == 200)" 2>nul
if errorlevel 1 (
    echo ❌ Contractions feature not found
    echo.
    echo SOLUTION: Backend needs restart - run restart_app.bat
    goto :end
)

echo.
echo [5/5] Checking frontend...
python -c "import requests; r = requests.get('http://localhost:8001/', timeout=2); print('✅ Frontend is UP')" 2>nul
if errorlevel 1 (
    echo ❌ Frontend is NOT responding on port 8001
    echo.
    echo SOLUTION: Run restart_app.bat
    goto :end
)

echo.
echo ================================================
echo  ✅ All systems operational!
echo ================================================
echo.
echo If features still don't work in browser:
echo 1. Open browser Developer Tools (F12)
echo 2. Go to Console tab
echo 3. Try clicking "Get Quiz Word"
echo 4. Look for error messages
echo 5. Share the error message for help
echo.
goto :done

:end
echo.
echo ================================================
echo  ❌ Issues detected!  
echo ================================================
echo.
echo Please run: restart_app.bat
echo.

:done
pause
