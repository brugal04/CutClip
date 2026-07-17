@echo off
setlocal EnableExtensions
cd /d "%~dp0"

if not exist "dist\CutClip.exe" (
    echo [ERROR] Primero debes ejecutar COMPILAR_EXE.bat
    pause
    exit /b 1
)

set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not exist "%ISCC%" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
if not exist "%ISCC%" (
    echo [ERROR] No se encontro Inno Setup 6.
    echo Instala Inno Setup 6 o ejecuta:
    echo winget install JRSoftware.InnoSetup
    pause
    exit /b 1
)

"%ISCC%" "installer\CutClip_v1.0.1.iss"
if errorlevel 1 (
    echo.
    echo [ERROR] No se pudo crear el instalador.
    pause
    exit /b 1
)

echo.
echo [OK] Instalador creado en:
echo installer\output\CutClip_Setup_v1.0.1.exe
start "" "installer\output"
pause
exit /b 0
