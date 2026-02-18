@echo off
echo ================================================
echo  Stopping Pronunciation Quiz Web App
echo ================================================
echo.

REM Kill existing servers
echo Stopping servers on port 8000 and 8001...

REM Kill processes using PowerShell (more reliable)
powershell -Command "$ports = @(8000, 8001); foreach($port in $ports) { $conn = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue; if($conn) { foreach($c in $conn) { Stop-Process -Id $c.OwningProcess -Force -ErrorAction SilentlyContinue } } }"

REM Also try traditional method as backup
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do (
    taskkill /F /PID %%a >nul 2>&1
)

for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8001') do (
    taskkill /F /PID %%a >nul 2>&1
)

echo.
echo ✅ Servers stopped!
echo.
pause
