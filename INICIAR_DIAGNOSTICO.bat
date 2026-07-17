@echo off
setlocal
cd /d "%~dp0"

echo ======================================================
echo   CutClip v1.0.0 - Diagnostico
 echo ======================================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo ERROR: No existe el entorno independiente .venv.
    echo Ejecuta primero INSTALAR.bat
    pause
    exit /b 1
)

echo Python utilizado:
".venv\Scripts\python.exe" -c "import sys; print(sys.executable); print(sys.version)"
echo.
echo Dependencias principales:
".venv\Scripts\python.exe" -c "from PIL import Image; import customtkinter, pystray, obsws_python; print('Pillow:', Image.__version__); print('CustomTkinter:', customtkinter.__version__); print('Pystray: OK'); print('obsws-python: OK')"
echo.
echo Iniciando aplicacion con consola de diagnostico...
echo.
".venv\Scripts\python.exe" -u app.py
set EXIT_CODE=%ERRORLEVEL%
echo.
echo Codigo de salida: %EXIT_CODE%
pause
exit /b %EXIT_CODE%
