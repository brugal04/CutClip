"""Icono y menú de la bandeja del sistema."""

from __future__ import annotations

import threading
from collections.abc import Callable
from pathlib import Path

from PIL import Image, ImageDraw
import pystray


class TrayController:
    """Controla el icono dinámico y las acciones rápidas de la bandeja."""

    def __init__(
        self,
        app_name: str,
        on_show: Callable[[], None],
        on_short_clip: Callable[[], None],
        on_long_clip: Callable[[], None],
        on_open_clips: Callable[[], None],
        on_open_logs: Callable[[], None],
        on_settings: Callable[[], None],
        on_reconnect: Callable[[], None],
        on_about: Callable[[], None],
        on_exit: Callable[[], None],
        base_icon: Path | None = None,
    ) -> None:
        self.app_name = app_name
        self.base_icon = base_icon
        self._state = "disconnected"
        self._status_text = "OBS desconectado"
        self._thread: threading.Thread | None = None
        self.icon = pystray.Icon(
            "cutclip",
            self._make_icon("disconnected"),
            app_name,
            menu=pystray.Menu(
                pystray.MenuItem(app_name, lambda _i, _x: on_show(), default=True),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem(lambda _item: self._status_text, None, enabled=False),
                pystray.MenuItem("Guardar últimos 3 minutos", lambda _i, _x: on_short_clip()),
                pystray.MenuItem("Guardar hasta 10 minutos", lambda _i, _x: on_long_clip()),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Abrir carpeta de clips", lambda _i, _x: on_open_clips()),
                pystray.MenuItem("Abrir carpeta de logs", lambda _i, _x: on_open_logs()),
                pystray.MenuItem("Configuración", lambda _i, _x: on_settings()),
                pystray.MenuItem("Reconectar con OBS", lambda _i, _x: on_reconnect()),
                pystray.MenuItem("Acerca de", lambda _i, _x: on_about()),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Salir", lambda _i, _x: on_exit()),
            ),
        )

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self.icon.run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        try:
            self.icon.stop()
        except Exception:
            pass

    def set_state(self, state: str, status_text: str) -> None:
        self._state = state
        self._status_text = status_text
        self.icon.icon = self._make_icon(state)
        self.icon.title = f"{self.app_name} — {status_text}"
        try:
            self.icon.update_menu()
        except Exception:
            pass

    def _make_icon(self, state: str) -> Image.Image:
        if self.base_icon and self.base_icon.exists():
            # Abrimos el archivo dentro de un contexto y copiamos la imagen para
            # no mantener un descriptor abierto durante toda la ejecución.
            with Image.open(self.base_icon) as source:
                image = source.convert("RGBA").resize((64, 64)).copy()
        else:
            image = Image.new("RGBA", (64, 64), (20, 23, 28, 255))
            draw = ImageDraw.Draw(image)
            draw.rounded_rectangle((6, 6, 58, 58), radius=14, fill=(36, 40, 48, 255))
            draw.ellipse((18, 18, 46, 46), outline=(230, 234, 239, 255), width=4)
            draw.ellipse((27, 27, 37, 37), fill=(230, 234, 239, 255))

        colors = {
            "connected": (53, 201, 122, 255),
            "reconnecting": (245, 179, 66, 255),
            "disconnected": (225, 91, 100, 255),
        }
        draw = ImageDraw.Draw(image)
        draw.ellipse((43, 43, 61, 61), fill=(17, 19, 24, 255))
        draw.ellipse((46, 46, 58, 58), fill=colors.get(state, colors["disconnected"]))
        return image
