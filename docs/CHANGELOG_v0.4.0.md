# CutClip v0.4.1 — Professional Polish

**Build:** 2026.07.17.1  
**Diseñado y desarrollado por:** Bryant Brugal

## Interfaz

- La aplicación inicia siempre con **Configuración cerrada**, mostrando primero la vista compacta.
- El panel de Configuración ahora utiliza un contenedor desplazable independiente.
- La barra vertical aparece únicamente al desplegar Configuración.
- Apertura y cierre con cambio de tamaño suave, sin bloquear el hilo gráfico.
- El tamaño expandido se adapta automáticamente al área visible del monitor.

## Identidad visual de Windows

- AppUserModelID propio para evitar que Windows muestre el icono genérico de Python.
- Icono aplicado mediante ICO y PNG a la ventana, barra de tareas, bandeja, EXE e instalador.
- Recursos en 16, 24, 32, 48, 64, 128 y 256 píxeles.

## Refactorización y rendimiento

- Integración específica de Windows aislada en `windows_integration.py`.
- Cola de eventos limitada por ciclo para mantener fluidez durante ráfagas de mensajes.
- Escritura atómica de `config.json` para evitar archivos corruptos ante cierres inesperados.
- Lógica de expansión, cálculo de tamaño y animación separada en funciones pequeñas y comentadas.
- Versiones internas sincronizadas en código, EXE, instalador, documentación y scripts BAT.

## Archivos principales modificados

- `cutclip/ui.py`
- `cutclip/config.py`
- `cutclip/windows_integration.py`
- `cutclip/app_info.py`
- `cutclip/__init__.py`
- `version_info.txt`
- `installer/CutClip_v0.4.1.iss`
- Scripts de instalación, diagnóstico y compilación
