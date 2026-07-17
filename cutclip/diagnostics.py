"""Comprobaciones locales para explicar el estado de CutClip al usuario."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .config import AppConfig
from .ffmpeg_locator import ffmpeg_is_available, find_ffmpeg


@dataclass(frozen=True, slots=True)
class DiagnosticItem:
    name: str
    ok: bool
    detail: str


def run_local_diagnostics(config: AppConfig, obs_connected: bool) -> list[DiagnosticItem]:
    """Evalúa componentes que no requieren modificar OBS ni los clips."""
    folder = Path(config.clips_folder).expanduser()
    folder_ok = True
    folder_detail = str(folder)
    try:
        folder.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        folder_ok = False
        folder_detail = str(exc)

    ffmpeg_path = find_ffmpeg(config.ffmpeg_path)
    ffmpeg_ok = ffmpeg_is_available(config.ffmpeg_path)
    return [
        DiagnosticItem("OBS WebSocket", obs_connected, "Conectado" if obs_connected else "No conectado"),
        DiagnosticItem("FFmpeg", ffmpeg_ok, ffmpeg_path if ffmpeg_ok else "No encontrado"),
        DiagnosticItem("Carpeta de clips", folder_ok, folder_detail),
        DiagnosticItem("Atajo rápido", True, config.short_hotkey),
        DiagnosticItem("Replay completo", True, config.long_hotkey),
    ]
