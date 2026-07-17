# Guía de instalación y configuración — CutClip v1.0.1

## 1. Instalar

Ejecuta `CutClip_Setup_v1.0.1.exe` y abre CutClip. FFmpeg ya debe estar incluido; el usuario final no tiene que descargarlo.

## 2. Preparar OBS Studio

1. Abre OBS Studio.
2. Entra en **Herramientas → Configuración del servidor WebSocket**.
3. Activa el servidor WebSocket.
4. Mantén el puerto recomendado `4455`.
5. Copia la contraseña mostrada por OBS.
6. Activa **Replay Buffer** en **Configuración → Salida → Replay Buffer**.

## 3. Conectar CutClip

1. Abre **Configuración** en CutClip.
2. Servidor: `127.0.0.1`.
3. Puerto: `4455` (CutClip también prueba 4444 y 4456 localmente).
4. Pega la contraseña de OBS.
5. Pulsa **Guardar configuración** y luego **Conectar con OBS**.

## 4. Uso

- `F1`: últimos 3 minutos; necesita FFmpeg.
- `Shift + F1`: Replay completo de hasta 10 minutos.

## 5. Diagnóstico

Abre Configuración y pulsa **Diagnóstico**. CutClip comprobará conexión con OBS, FFmpeg, carpeta de clips y atajos.

## Problemas frecuentes

### OBS no conecta
Verifica que OBS esté abierto, WebSocket esté activado y la contraseña sea correcta.

### F1 falla pero Shift+F1 funciona
La instalación no contiene FFmpeg o el antivirus lo aisló. Reinstala CutClip v1.0.1 y revisa la cuarentena del antivirus.

### Replay Buffer desactivado
Actívalo en OBS. CutClip puede iniciarlo automáticamente si la opción correspondiente está habilitada.
