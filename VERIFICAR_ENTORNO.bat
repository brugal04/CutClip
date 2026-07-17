@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo No existe .venv. Ejecuta INSTALAR.bat primero.
    pause
    exit /b 1
)

".venv\Scripts\python.exe" -c "import sys; from PIL import Image; print('Entorno CutClip:'); print(sys.executable); print('Pillow:', Image.__version__)"
echo.
echo Entorno de Hermes no modificado por este proyecto.
pause
