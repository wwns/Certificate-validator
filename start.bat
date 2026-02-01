@echo off
REM Palo Alto Certificate Manager - Windows Startup Script

echo.
echo ================================================
echo   Palo Alto Certificate Manager
echo ================================================
echo.

REM Sprawdz Python
python --version >nul 2>&1
if errorlevel 1 (
    echo BLAD: Python nie jest zainstalowany lub nie jest w PATH
    echo Pobierz Python z: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Sprawdz OpenSSL
openssl version >nul 2>&1
if errorlevel 1 (
    echo OSTRZEZENIE: OpenSSL nie znaleziony w PATH
    echo Pobierz OpenSSL z: https://slproweb.com/products/Win32OpenSSL.html
    echo.
)

REM Uruchom aplikacje
echo.
echo Uruchamianie aplikacji...
echo.
python app.py

pause
