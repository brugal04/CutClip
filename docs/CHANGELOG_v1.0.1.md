# CutClip v1.0.1 — Mantenimiento y primer uso

## Cambios

- Preparación y empaquetado automático de FFmpeg Essentials durante la compilación.
- F1 muestra una explicación clara y permite seguir usando Shift+F1 si FFmpeg falta.
- Detección local de OBS WebSocket en 4455, 4444 y 4456.
- Nuevo diagnóstico visible para OBS, FFmpeg, carpeta y atajos.
- Guía de instalación, configuración y solución de problemas.
- Detección de Inno Setup instalado en `%LOCALAPPDATA%`.
- Versión actualizada a 1.0.1.

## Archivos principales modificados

`CutClip.spec`, `COMPILAR_EXE.bat`, `COMPILAR_INSTALADOR_COMPLETO.bat`, `cutclip/ffmpeg_locator.py`, `cutclip/clip_manager.py`, `cutclip/obs_controller.py`, `cutclip/ui.py`, `installer/CutClip_v1.0.1.iss`, `README.md`.

## Archivos nuevos

`DESCARGAR_FFMPEG.bat`, `cutclip/diagnostics.py`, `docs/GUIA_INSTALACION_Y_CONFIGURACION_v1.0.1.md`.

## Validación realizada

- Compilación sintáctica de todos los módulos Python.
- Verificación de referencias de versión 1.0.1.
- Verificación estática de rutas PyInstaller e Inno Setup.

La compilación final de Windows debe ejecutarse en Windows porque PyInstaller no genera un ejecutable Windows desde este entorno Linux.
