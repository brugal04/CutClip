@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title CutClip v1.0.1 - Compilador del instalador

 echo ============================================================
 echo       CUTCLIP v1.0.1 - CREAR INSTALADOR PARA WINDOWS
 echo ============================================================
 echo.

if not exist ".venv\Scripts\python.exe" (
    echo [PASO 1/3] El entorno de CutClip no existe.
    echo Ejecutando INSTALAR.bat...
    call "INSTALAR.bat"
    if errorlevel 1 goto :error
)

 echo [PASO 1/3] Compilando CutClip.exe...
call "COMPILAR_EXE.bat" nopause
if errorlevel 1 goto :error

set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not exist "%ISCC%" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
if not exist "%ISCC%" set "ISCC=%LocalAppData%\Programs\Inno Setup 6\ISCC.exe"

if not exist "%ISCC%" (
    echo.
    echo [ERROR] No se encontro Inno Setup 6.
    echo.
    echo Instala Inno Setup 6 desde su pagina oficial y vuelve a ejecutar
    echo este archivo. Tambien puedes instalarlo con winget:
    echo.
    echo     winget install JRSoftware.InnoSetup
    echo.
    pause
    exit /b 2
)

 echo.
 echo [PASO 2/3] Creando instalador con Inno Setup...
"%ISCC%" "installer\CutClip_v1.0.1.iss"
if errorlevel 1 goto :error

 echo.
 echo [PASO 3/3] Instalador creado correctamente.
 echo.
 echo Archivo:
 echo   %CD%\installer\output\CutClip_Setup_v1.0.1.exe
 echo.
start "" "%CD%\installer\output"
pause
exit /b 0

:error
 echo.
 echo [ERROR] No se pudo crear el instalador de CutClip.
 echo Revisa los mensajes anteriores para identificar el problema.
 echo.
pause
exit /b 1
