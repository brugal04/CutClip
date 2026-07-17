# CutClip v1.0.0 — Rebranding y base oficial

## Identidad

- El producto cambia oficialmente de OBS Clip Manager a **CutClip**.
- Se agrega el subtítulo **Instant Replay Manager**.
- Se muestra **Compatible con OBS Studio** sin presentar la aplicación como producto oficial.
- Se añade un aviso claro de independencia en la interfaz, README e instalador.
- Nuevo icono original de CutClip para ventana, barra de tareas, bandeja, EXE e instalador.

## Rendimiento y experiencia

- La configuración inicia cerrada.
- Apertura y cierre instantáneos, sin animaciones.
- Panel desplazable solo al desplegar la configuración.
- La cola de eventos mantiene todas las actualizaciones de Tk en el hilo principal.
- La reconexión y las notificaciones continúan en hilos de fondo.

## Refactorización

- El paquete principal pasa a llamarse `cutclip`.
- Metadatos centralizados en `cutclip/app_info.py`.
- Detección de FFmpeg separada en `cutclip/ffmpeg_locator.py`.
- Configuración con escritura atómica y migración de la versión anterior.
- Punto de entrada reducido y comentado.
- Eliminación de cachés Python del paquete distribuido.

## Compatibilidad

- Se conserva la configuración de OBS, hotkeys, clips, bandeja y notificaciones.
- La configuración anterior se copia desde `%APPDATA%\OBSClipManager` a `%APPDATA%\CutClip` sin borrar el original.
