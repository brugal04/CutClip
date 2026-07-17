@echo off
setlocal
cd /d "%~dp0"

echo ======================================================
echo   CutClip v1.0.1 - Instalador de dependencias
echo ======================================================
echo.

if exist ".venv\Scripts\python.exe" goto :install

echo Creando entorno virtual independiente en .venv...
where py >nul 2>nul
if not errorlevel 1 (
    py -3 -m venv .venv
) else (
    where python >nul 2>nul
    if errorlevel 1 goto :no_python
    python -m venv .venv
)
if errorlevel 1 goto :venv_error

:install
echo Instalando dependencias dentro de .venv...
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto :install_error
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto :install_error

echo.
echo Instalacion completada correctamente.
echo CutClip usa ahora un entorno independiente de Hermes y otros programas.
echo.
".venv\Scripts\python.exe" -c "import sys; from PIL import Image; print('Python:', sys.executable); print('Pillow:', Image.__version__)"
echo.
pause
exit /b 0

:no_python
echo ERROR: No se encontro Python instalado o disponible en PATH.
echo Instala Python 3.11 o superior y vuelve a ejecutar este archivo.
pause
exit /b 1

:venv_error
echo ERROR: No se pudo crear el entorno virtual .venv.
pause
exit /b 1

:install_error
echo ERROR: No se pudieron instalar las dependencias.
echo Ejecuta INICIAR_DIAGNOSTICO.bat para obtener mas informacion.
pause
exit /b 1
