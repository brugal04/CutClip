# CutClip — Sprint v0.1.0

## Objetivo

Crear una primera base funcional para Windows 11 y OBS Studio 30.0.0+, sin inteligencia artificial.

## Funciones implementadas

- Conexión local con OBS mediante obs-websocket v5.
- Validación de OBS 30 o superior.
- Inicio automático del Replay Buffer cuando está detenido.
- F1 para clip de tres minutos.
- Shift+F1 para clip de diez minutos.
- Botones equivalentes dentro de la interfaz.
- Espera segura hasta que OBS termina de escribir el archivo.
- Recorte de los últimos 180 segundos mediante FFmpeg y copia directa de streams.
- Organización cronológica dentro de `Videos\OBS_Clips`.
- Configuración persistente en `%APPDATA%`.
- Indicador de conexión, mensajes de operación y errores descriptivos.
- Scripts de instalación, diagnóstico y compilación a EXE.

## Archivos principales

- `app.py`: punto de entrada.
- `cutclip/ui.py`: interfaz y coordinación.
- `cutclip/obs_controller.py`: conexión y control de OBS.
- `cutclip/clip_manager.py`: recorte y organización.
- `cutclip/hotkeys.py`: captura global de F1 y Shift+F1.
- `cutclip/config.py`: configuración persistente.
- `README.md`: instalación y uso.

## Decisión técnica sobre las dos duraciones

OBS solo puede conservar un Replay Buffer con una duración máxima a la vez. La base usa 600 segundos:

- Clip largo: conserva el archivo completo.
- Clip corto: extrae los últimos 180 segundos del archivo completo.

Esto evita detener y reiniciar el Replay Buffer durante el directo.

## Pruebas realizadas en esta entrega

Pruebas estáticas efectuadas:

1. Compilación sintáctica de todos los archivos Python.
2. Comprobación de estructura y archivos obligatorios.
3. Validación de JSON de ejemplo.
4. Verificación de nombres versionados de entregables.

Las pruebas reales de conexión y guardado requieren OBS ejecutándose en Windows.

## Próximo sprint recomendado

- Instalador con FFmpeg incluido de forma legal y trazable.
- Bandeja del sistema.
- Inicio con Windows.
- Hotkeys editables.
- Historial de clips.
- Detección del juego o escena activa para nombrar archivos.
- Notificaciones nativas de Windows.
