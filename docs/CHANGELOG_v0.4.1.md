# CutClip v0.4.1 — Performance Patch

## Objetivo

Eliminar animaciones innecesarias y priorizar respuesta inmediata en una utilidad ligera.

## Cambios

- Eliminada la animación de expansión y contracción de Configuración.
- El panel ahora abre y cierra de forma instantánea.
- El cambio de tamaño conserva la posición actual de la ventana.
- Eliminado el temporizador y estado interno usado solo por la animación.
- Reforzada la aplicación del icono mediante `WM_SETICON` para ejecuciones desde `pythonw.exe`.
- Actualizados versión, build, scripts, metadatos, instalador y documentación.

## Archivos principales modificados

- `cutclip/ui.py`
- `cutclip/windows_integration.py`
- `cutclip/app_info.py`
- `cutclip/__init__.py`
- `version_info.txt`
- `installer/CutClip_v0.4.1.iss`
