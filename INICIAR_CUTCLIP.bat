@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\pythonw.exe" (
    echo CutClip no esta instalado en su entorno independiente.
    echo Ejecuta primero INSTALAR.bat
    pause
    exit /b 1
)

start "" ".venv\Scripts\pythonw.exe" "app.py"
exit /b 0
