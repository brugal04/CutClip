@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Ejecuta primero INSTALAR.bat
    pause
    exit /b 1
)

".venv\Scripts\python.exe" -m pip install --upgrade pyinstaller
if errorlevel 1 goto :error

".venv\Scripts\python.exe" -m PyInstaller --noconfirm --clean "CutClip.spec"
if errorlevel 1 goto :error

echo.
echo EXE creado en: dist\CutClip.exe
pause
exit /b 0

:error
echo.
echo No se pudo compilar el EXE.
pause
exit /b 1
