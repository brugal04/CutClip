# CutClip v1.0.0

**Instant Replay Manager — Compatible con OBS Studio**

CutClip es una aplicación independiente para Windows que guarda clips rápidos desde el Replay Buffer de OBS Studio mediante atajos globales.

## Funciones principales

- `F1`: guarda los últimos 3 minutos.
- `Shift + F1`: guarda hasta los últimos 10 minutos.
- Conexión automática y reconexión con OBS WebSocket.
- Bandeja del sistema con acciones rápidas y estado dinámico.
- Configuración compacta, cerrada al iniciar y sin animaciones.
- Notificaciones de Windows.
- Detección automática de FFmpeg portable o instalado en PATH.
- Inicio opcional con Windows y modo silencioso.
- Configuración y logs en `%APPDATA%\CutClip`.
- Migración automática de la configuración anterior desde `%APPDATA%\OBSClipManager`.

## Instalación desde el código fuente

1. Ejecuta `INSTALAR.bat`.
2. Ejecuta `VERIFICAR_ENTORNO.bat`.
3. Ejecuta `INICIAR_CUTCLIP.bat`.

CutClip utiliza su propio entorno `.venv`; no modifica Hermes ni otros programas de Python.

## OBS Studio

En OBS Studio activa el servidor WebSocket y configura en CutClip:

- Servidor: `127.0.0.1`
- Puerto: `4455`
- Contraseña: la configurada en OBS

El Replay Buffer debe estar disponible. CutClip puede iniciarlo automáticamente cuando la configuración lo permite.

## FFmpeg

CutClip busca FFmpeg en este orden:

1. Ruta guardada por el usuario.
2. `ffmpeg\ffmpeg.exe` incluido junto al programa.
3. FFmpeg disponible en el `PATH` de Windows.

FFmpeg se utiliza únicamente para recortar los clips finales.

## Compilar

- `COMPILAR_EXE.bat` crea `dist\CutClip.exe`.
- `COMPILAR_INSTALADOR.bat` crea el instalador con Inno Setup 6.

## Aviso de independencia

CutClip es una aplicación independiente desarrollada por Bryant Brugal. No está afiliada, patrocinada ni respaldada por OBS Studio ni por sus desarrolladores. El nombre OBS Studio se utiliza únicamente para indicar compatibilidad técnica.

© 2026 Bryant Brugal. Todos los derechos reservados.
