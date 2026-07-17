"""Notificaciones nativas de Windows con degradación segura."""

from __future__ import annotations

import logging
import os
from pathlib import Path


class Notifier:
    """Envía notificaciones sin interrumpir el flujo principal."""

    def __init__(self, app_id: str, icon_path: Path | None = None) -> None:
        self.app_id = app_id
        self.icon_path = icon_path

    def show(self, title: str, message: str) -> None:
        if os.name != "nt":
            return
        try:
            from winotify import Notification

            toast = Notification(
                app_id=self.app_id,
                title=title,
                msg=message,
                icon=str(self.icon_path) if self.icon_path and self.icon_path.exists() else "",
                duration="short",
            )
            toast.show()
        except Exception:
            logging.exception("No se pudo mostrar la notificación")
