"""Localización fiable de FFmpeg en desarrollo y en ejecutables empaquetados."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path


def application_root() -> Path:
    """Devuelve la carpeta física de CutClip o del ejecutable instalado."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[1]


def resource_root() -> Path:
    """Devuelve la raíz temporal de recursos utilizada por PyInstaller."""
    return Path(getattr(sys, "_MEIPASS", application_root()))


def ffmpeg_candidates(configured_path: str = "") -> list[Path]:
    """Construye candidatos ordenados sin ejecutar procesos externos."""
    candidates: list[Path] = []
    if configured_path and configured_path.lower() != "ffmpeg":
        candidates.append(Path(configured_path).expanduser())

    # En el instalador FFmpeg queda junto al EXE; en one-file también puede
    # encontrarse dentro de _MEIPASS. Se admiten ambas disposiciones.
    for base in (application_root(), resource_root()):
        candidates.extend((
            base / "ffmpeg" / "ffmpeg.exe",
            base / "tools" / "ffmpeg" / "ffmpeg.exe",
            base / "ffmpeg.exe",
        ))
    return candidates


def find_ffmpeg(configured_path: str = "") -> str:
    """Devuelve la mejor ruta disponible o ``ffmpeg`` como último recurso."""
    for candidate in ffmpeg_candidates(configured_path):
        if candidate.is_file():
            return str(candidate.resolve())

    discovered = shutil.which("ffmpeg")
    return discovered or "ffmpeg"


def ffmpeg_is_available(configured_path: str = "") -> bool:
    """Indica si CutClip puede ejecutar FFmpeg en este momento."""
    resolved = find_ffmpeg(configured_path)
    return Path(resolved).is_file() or shutil.which(resolved) is not None
