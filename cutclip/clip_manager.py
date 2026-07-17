"""Organización, copia y recorte de clips."""

from __future__ import annotations

import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from .config import AppConfig


class ClipManager:
    """Mueve clips completos y genera versiones cortas mediante FFmpeg."""

    def __init__(self, config: AppConfig) -> None:
        self.config = config

    @property
    def output_folder(self) -> Path:
        """Carpeta final elegida por el usuario."""
        path = Path(self.config.clips_folder).expanduser()
        path.mkdir(parents=True, exist_ok=True)
        return path

    def keep_long_clip(self, source: Path) -> Path:
        """Mueve el Replay completo a la biblioteca como clip de 10 minutos."""
        destination = self._unique_destination(source.suffix, "10min")
        return self._move_or_copy(source, destination)

    def create_short_clip(self, source: Path) -> Path:
        """Recorta los últimos tres minutos del Replay completo sin recodificar."""
        destination = self._unique_destination(source.suffix, "3min")
        ffmpeg = self._resolve_ffmpeg()

        # -sseof usa un desplazamiento negativo desde el final del archivo.
        # -c copy evita recodificación y mantiene el uso de CPU/GPU al mínimo.
        command = [
            ffmpeg,
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-sseof",
            f"-{self.config.short_clip_seconds}",
            "-i",
            str(source),
            "-map",
            "0",
            "-c",
            "copy",
            "-avoid_negative_ts",
            "make_zero",
            str(destination),
        ]

        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=90,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        if completed.returncode != 0:
            error = completed.stderr.strip() or "FFmpeg no pudo recortar el clip."
            raise RuntimeError(error)

        if not destination.exists() or destination.stat().st_size == 0:
            raise RuntimeError("FFmpeg terminó sin crear un clip válido.")

        # El Replay temporal completo se elimina solo después de validar el recorte.
        try:
            source.unlink()
        except OSError:
            pass
        return destination

    def _resolve_ffmpeg(self) -> str:
        """Encuentra FFmpeg por ruta configurada o por PATH."""
        configured = Path(self.config.ffmpeg_path)
        if configured.is_file():
            return str(configured)

        located = shutil.which(self.config.ffmpeg_path)
        if located:
            return located

        raise FileNotFoundError(
            "No se encontró FFmpeg. Instálalo o selecciona ffmpeg.exe en Configuración."
        )

    def _unique_destination(self, suffix: str, label: str) -> Path:
        """Crea un nombre cronológico que nunca sobrescribe otro clip."""
        safe_suffix = suffix if suffix else ".mkv"
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        base = self.output_folder / f"Clip_{label}_{timestamp}{safe_suffix}"

        if not base.exists():
            return base

        for index in range(1, 1000):
            candidate = base.with_stem(f"{base.stem}_{index:03d}")
            if not candidate.exists():
                return candidate

        raise RuntimeError("No se pudo generar un nombre único para el clip.")

    @staticmethod
    def _move_or_copy(source: Path, destination: Path) -> Path:
        """Mueve el archivo; si los discos son distintos, copia y elimina."""
        destination.parent.mkdir(parents=True, exist_ok=True)
        try:
            return Path(shutil.move(str(source), str(destination)))
        except OSError:
            shutil.copy2(source, destination)
            source.unlink()
            return destination
