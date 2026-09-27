@echo off
echo ============================================
echo   Permit Master - Build .exe
echo ============================================
echo.

:: Install dependencies
echo [1/2] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies.
    pause
    exit /b 1
)

echo.
echo [2/2] Building .exe with PyInstaller (using .spec)...
pyinstaller --noconfirm PermitMaster.spec

if errorlevel 1 (
    echo ERROR: Build failed.
    pause
    exit /b 1
)

echo.
echo ============================================
echo   BUILD SUCCESSFUL!
echo   Your .exe is at: dist\PermitMaster.exe
echo ============================================
echo ============================================
echo.

