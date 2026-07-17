# Guía para crear el instalador de CutClip v1.0.0

## Requisitos

- Windows 10 u 11 de 64 bits.
- Python disponible mediante el entorno `.venv` creado por `INSTALAR.bat`.
- Inno Setup 6.

## Proceso automático

Ejecuta:

`COMPILAR_INSTALADOR_COMPLETO.bat`

El script:

1. Comprueba o crea el entorno de CutClip.
2. Instala una versión compatible de PyInstaller.
3. Limpia compilaciones anteriores.
4. Genera `dist\CutClip.exe`.
5. Compila el instalador con Inno Setup.
6. Abre automáticamente la carpeta de salida.

## Resultado

`installer\output\CutClip_Setup_v1.0.0.exe`

## Funciones del instalador

- Instalación por usuario o con elevación opcional.
- Acceso directo en el menú Inicio.
- Acceso directo opcional en el escritorio.
- Inicio automático opcional con Windows.
- Desinstalador registrado en Windows.
- Icono, versión, autor y descripción del producto.
- Aviso de independencia y compatibilidad con OBS Studio.
