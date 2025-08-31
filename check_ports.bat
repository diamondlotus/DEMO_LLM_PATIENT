@echo off
echo 🔍 Checking Port Usage on Your System
echo ====================================

echo 📊 Checking common ports:
echo.

REM Check common ports
for %%p in (80 8000 3000 8080 443 22 3306 6379 8001) do (
    echo -n Port %%p: 
    netstat -an | findstr :%%p >nul 2>&1
    if !errorlevel! equ 0 (
        echo 🔴 IN USE
        echo    Process details:
        netstat -an | findstr :%%p
        echo.
    ) else (
        echo 🟢 AVAILABLE
    )
)

echo 🔍 Detailed Port 80 Check:
echo ==========================

REM Check port 80 specifically
netstat -an | findstr :80 >nul 2>&1
if !errorlevel! equ 0 (
    echo ❌ Port 80 is currently in use by:
    netstat -an | findstr :80
    echo.
    echo 💡 You may need to:
    echo    1. Stop the service using port 80
    echo    2. Change your Docker frontend port to something else (e.g., 8080)
    echo    3. Use port forwarding in docker-compose.yml
) else (
    echo ✅ Port 80 is available for use
)

echo.
echo 🔍 All Listening Ports:
echo =======================
netstat -an | findstr LISTENING | head -20

echo.
echo 💡 To free up port 80, you can:
echo    - Stop web servers (Apache, nginx, etc.)
echo    - Stop Docker containers using port 80
echo    - Change your application to use a different port

pause
