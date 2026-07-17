@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo ============================================================
echo   CUTCLIP v1.0.1 - PREPARAR FFMPEG PORTABLE
echo ============================================================

if exist "tools\ffmpeg\ffmpeg.exe" (
    echo [OK] FFmpeg ya esta preparado.
    exit /b 0
)

set "ZIP=%TEMP%\cutclip_ffmpeg_release.zip"
set "EXTRACT=%TEMP%\cutclip_ffmpeg_extract"
set "URL=https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"

if exist "%EXTRACT%" rmdir /s /q "%EXTRACT%"
mkdir "%EXTRACT%" >nul 2>&1
mkdir "tools\ffmpeg" >nul 2>&1

echo [1/3] Descargando FFmpeg Essentials desde gyan.dev...
powershell -NoProfile -ExecutionPolicy Bypass -Command "Invoke-WebRequest -Uri '%URL%' -OutFile '%ZIP%'"
if errorlevel 1 goto :error

echo [2/3] Extrayendo paquete...
powershell -NoProfile -ExecutionPolicy Bypass -Command "Expand-Archive -LiteralPath '%ZIP%' -DestinationPath '%EXTRACT%' -Force"
if errorlevel 1 goto :error

echo [3/3] Copiando ffmpeg.exe y avisos de licencia...
for /r "%EXTRACT%" %%F in (ffmpeg.exe) do if not exist "tools\ffmpeg\ffmpeg.exe" copy /y "%%F" "tools\ffmpeg\ffmpeg.exe" >nul
for /r "%EXTRACT%" %%F in (LICENSE) do if not exist "tools\ffmpeg\FFMPEG_LICENSE.txt" copy /y "%%F" "tools\ffmpeg\FFMPEG_LICENSE.txt" >nul
for /r "%EXTRACT%" %%F in (README.txt) do if not exist "tools\ffmpeg\FFMPEG_BUILD_README.txt" copy /y "%%F" "tools\ffmpeg\FFMPEG_BUILD_README.txt" >nul

if not exist "tools\ffmpeg\ffmpeg.exe" goto :error

del /q "%ZIP%" >nul 2>&1
rmdir /s /q "%EXTRACT%" >nul 2>&1
echo [OK] FFmpeg portable listo para compilar CutClip.
exit /b 0

:error
echo [ERROR] No se pudo preparar FFmpeg automaticamente.
echo Descarga ffmpeg-release-essentials.zip y copia ffmpeg.exe en:
echo   tools\ffmpeg\ffmpeg.exe
exit /b 1
