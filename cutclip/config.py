"""Carga, validación, migración y almacenamiento de la configuración."""

from __future__ import annotations

import json
import os
import shutil
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .ffmpeg_locator import find_ffmpeg

APP_DIR = Path(os.getenv("APPDATA", Path.home())) / "CutClip"
CONFIG_PATH = APP_DIR / "config.json"
LEGACY_APP_DIR = Path(os.getenv("APPDATA", Path.home())) / "OBSClipManager"
LEGACY_CONFIG_PATH = LEGACY_APP_DIR / "config.json"


@dataclass(slots=True)
class AppConfig:
    """Configuración editable y persistente de CutClip."""

    obs_host: str = "127.0.0.1"
    obs_port: int = 4455
    obs_password: str = ""
    clips_folder: str = str(Path.home() / "Videos" / "CutClip")
    short_clip_seconds: int = 180
    long_clip_seconds: int = 600
    short_hotkey: str = "F1"
    long_hotkey: str = "SHIFT+F1"
    ffmpeg_path: str = "ffmpeg"
    auto_start_replay_buffer: bool = True
    auto_connect: bool = True
    auto_reconnect: bool = True
    reconnect_interval: int = 5
    minimize_to_tray: bool = True
    show_tray_notice: bool = True
    start_with_windows: bool = False
    silent_start: bool = False
    notifications_enabled: bool = True

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "AppConfig":
        """Ignora claves desconocidas para permitir upgrades seguros."""
        allowed = cls.__dataclass_fields__.keys()
        return cls(**{key: value for key, value in raw.items() if key in allowed})

    def validate(self) -> None:
        """Valida únicamente reglas que impedirían el funcionamiento correcto."""
        if not 1 <= int(self.obs_port) <= 65535:
            raise ValueError("El puerto de OBS debe estar entre 1 y 65535.")
        if self.short_clip_seconds <= 0:
            raise ValueError("La duración corta debe ser mayor que cero.")
        if self.long_clip_seconds < self.short_clip_seconds:
            raise ValueError("La duración larga no puede ser menor que la corta.")
        if self.reconnect_interval < 2:
            raise ValueError("El intervalo de reconexión debe ser de al menos 2 segundos.")


def _migrate_legacy_config() -> None:
    """Copia la configuración anterior sin borrar datos del usuario."""
    if CONFIG_PATH.exists() or not LEGACY_CONFIG_PATH.exists():
        return
    APP_DIR.mkdir(parents=True, exist_ok=True)
    try:
        shutil.copy2(LEGACY_CONFIG_PATH, CONFIG_PATH)
    except OSError:
        pass


def load_config() -> AppConfig:
    """Carga la configuración y repara automáticamente archivos inválidos."""
    APP_DIR.mkdir(parents=True, exist_ok=True)
    _migrate_legacy_config()
    if not CONFIG_PATH.exists():
        config = AppConfig()
        config.ffmpeg_path = find_ffmpeg(config.ffmpeg_path)
        save_config(config)
        return config
    try:
        config = AppConfig.from_dict(json.loads(CONFIG_PATH.read_text(encoding="utf-8")))
        config.ffmpeg_path = find_ffmpeg(config.ffmpeg_path)
        config.validate()
        return config
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        try:
            CONFIG_PATH.replace(CONFIG_PATH.with_suffix(".invalid.json"))
        except OSError:
            pass
        config = AppConfig()
        config.ffmpeg_path = find_ffmpeg(config.ffmpeg_path)
        save_config(config)
        return config


def save_config(config: AppConfig) -> None:
    """Guarda la configuración de forma atómica para evitar corrupción."""
    config.validate()
    APP_DIR.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(asdict(config), ensure_ascii=False, indent=2)
    temporary_path = CONFIG_PATH.with_suffix(".tmp")
    temporary_path.write_text(payload, encoding="utf-8")
    temporary_path.replace(CONFIG_PATH)
