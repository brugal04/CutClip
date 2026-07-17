# CutClip v0.2

## Cambios principales

- Interfaz completamente migrada a CustomTkinter.
- Diseño oscuro profesional inspirado en OBS Studio.
- Tarjetas modernas para clips de 3 y 10 minutos.
- Panel de configuración plegable.
- Botón para mostrar u ocultar la contraseña.
- Hotkeys globales nativos de Windows mediante `RegisterHotKey`.
- Eliminada la dependencia `pynput`.
- Conexión automática al iniciar.
- Reconexión automática si OBS se reinicia o se desconecta.
- Guardado persistente de servidor, puerto, contraseña, carpeta y FFmpeg.
- Mensajes de error en español.
- Registro de actividad en `%APPDATA%\CutClip\logs`.
- Menor uso de CPU en reposo: hotkeys y reconexión trabajan con espera bloqueante.
- Cierre limpio de hilos, hotkeys y conexión WebSocket.
