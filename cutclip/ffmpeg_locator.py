"""Detección ligera de FFmpeg.

La búsqueda se hace una sola vez al cargar la configuración. Se prioriza una
copia incluida junto a la aplicación y después la instalación disponible en
PATH. No se descarga nada ni se ejecutan procesos durante la detección.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path


def resource_root() -> Path:
    """Devuelve la raíz de recursos en fuente o en un ejecutable PyInstaller."""
    return Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))


def find_ffmpeg(configured_path: str = "") -> str:
    """Devuelve la mejor ruta disponible de FFmpeg.

    Conserva una ruta configurada válida, busca una copia portable en
    ``ffmpeg/ffmpeg.exe`` y, como último recurso, consulta el PATH de Windows.
    Si no encuentra nada devuelve ``ffmpeg`` para mantener compatibilidad con
    instalaciones que se agreguen al PATH después de iniciar CutClip.
    """
    if configured_path:
        configured = Path(configured_path).expanduser()
        if configured.is_file():
            return str(configured)
        if configured_path.lower() == "ffmpeg" and shutil.which("ffmpeg"):
            return shutil.which("ffmpeg") or "ffmpeg"

    portable = resource_root() / "ffmpeg" / "ffmpeg.exe"
    if portable.is_file():
        return str(portable)

    discovered = shutil.which("ffmpeg")
    return discovered or "ffmpeg"
