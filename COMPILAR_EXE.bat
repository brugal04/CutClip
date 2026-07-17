@echo off
setlocal EnableExtensions
cd /d "%~dp0"

call "DESCARGAR_FFMPEG.bat"
if errorlevel 1 goto :error

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Ejecuta primero INSTALAR.bat
    if /I not "%~1"=="nopause" pause
    exit /b 1
)

if exist "build" rmdir /s /q "build"
if exist "dist\CutClip.exe" del /q "dist\CutClip.exe"

".venv\Scripts\python.exe" -m pip install --upgrade "pyinstaller>=6.0,<7.0"
if errorlevel 1 goto :error

".venv\Scripts\python.exe" -m PyInstaller --noconfirm --clean "CutClip.spec"
if errorlevel 1 goto :error

if not exist "dist\CutClip.exe" goto :error

echo.
echo [OK] EXE creado en: dist\CutClip.exe
if /I not "%~1"=="nopause" pause
exit /b 0

:error
echo.
echo [ERROR] No se pudo compilar CutClip.exe.
if /I not "%~1"=="nopause" pause
exit /b 1
