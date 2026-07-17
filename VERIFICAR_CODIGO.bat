@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo No existe .venv. Ejecuta INSTALAR.bat primero.
    pause
    exit /b 1
)

echo Verificando sintaxis de CutClip v1.0.0...
".venv\Scripts\python.exe" -m compileall -q app.py cutclip
if errorlevel 1 (
    echo ERROR: Se encontraron errores de sintaxis.
    pause
    exit /b 1
)

echo Codigo verificado correctamente.
pause
exit /b 0
