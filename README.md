# CutClip v1.0.1

**Instant Replay Manager — Compatible con OBS Studio**

CutClip es una aplicación independiente para Windows que guarda clips rápidos desde el Replay Buffer de OBS Studio mediante atajos globales.

## Funciones principales

- `F1`: recorta y guarda los últimos 3 minutos.
- `Shift + F1`: guarda el Replay completo de hasta 10 minutos.
- FFmpeg se incluye automáticamente al compilar el instalador.
- Detección local de OBS WebSocket en los puertos 4455, 4444 y 4456.
- Reconexión automática cuando OBS se reinicia.
- Botón **Diagnóstico** para comprobar OBS, FFmpeg, carpeta y atajos.
- Bandeja del sistema, notificaciones y arranque opcional con Windows.

## Instalación y configuración

Consulta `docs/GUIA_INSTALACION_Y_CONFIGURACION_v1.0.1.md`. La contraseña de OBS se introduce una sola vez en Configuración. CutClip nunca intenta extraerla silenciosamente de archivos internos de OBS.

## Compilar

1. Ejecuta `INSTALAR.bat`.
2. Ejecuta `COMPILAR_INSTALADOR_COMPLETO.bat`.
3. El proceso descarga FFmpeg Essentials, compila `CutClip.exe` y crea `installer/output/CutClip_Setup_v1.0.1.exe`.

## FFmpeg y licencia

CutClip ejecuta FFmpeg como herramienta separada. El script de compilación descarga la compilación Essentials publicada por gyan.dev y conserva los avisos incluidos en ese paquete. Revisa esos avisos antes de redistribuir el instalador.

## Aviso de independencia

CutClip es una aplicación independiente desarrollada por Bryant Brugal. No está afiliada, patrocinada ni respaldada por OBS Studio ni por sus desarrolladores.

© 2026 Bryant Brugal. Todos los derechos reservados.
