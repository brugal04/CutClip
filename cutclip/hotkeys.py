"""Hotkeys globales nativos de Windows para CutClip.

Usa RegisterHotKey en vez de pynput para reducir dependencias, consumo y
latencia. Los hotkeys se reciben aunque la ventana esté minimizada.
"""

from __future__ import annotations

import ctypes
import os
import threading
from collections.abc import Callable
from ctypes import wintypes


WM_HOTKEY = 0x0312
WM_QUIT = 0x0012
MOD_SHIFT = 0x0004
VK_F1 = 0x70
HOTKEY_SHORT_ID = 1
HOTKEY_LONG_ID = 2


class GlobalHotkeys:
    """Registra F1 y Shift+F1 mediante la API nativa de Windows."""

    def __init__(
        self,
        on_short_clip: Callable[[], None],
        on_long_clip: Callable[[], None],
        on_error: Callable[[str], None] | None = None,
    ) -> None:
        self.on_short_clip = on_short_clip
        self.on_long_clip = on_long_clip
        self.on_error = on_error or (lambda _message: None)
        self._thread: threading.Thread | None = None
        self._thread_id: int | None = None
        self._stop_event = threading.Event()

    def start(self) -> None:
        """Inicia el bucle de mensajes una sola vez."""
        if self._thread and self._thread.is_alive():
            return
        if os.name != "nt":
            self.on_error("Los hotkeys globales nativos solo están disponibles en Windows.")
            return

        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._message_loop,
            name="CutClipHotkeys",
            daemon=True,
        )
        self._thread.start()

    def stop(self) -> None:
        """Desregistra los hotkeys y detiene el hilo."""
        self._stop_event.set()
        if os.name == "nt" and self._thread_id:
            ctypes.windll.user32.PostThreadMessageW(self._thread_id, WM_QUIT, 0, 0)
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.5)
        self._thread = None
        self._thread_id = None

    def _message_loop(self) -> None:
        """Registra los hotkeys y atiende WM_HOTKEY sin sondeo activo."""
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        self._thread_id = int(kernel32.GetCurrentThreadId())

        short_ok = bool(user32.RegisterHotKey(None, HOTKEY_SHORT_ID, 0, VK_F1))
        long_ok = bool(
            user32.RegisterHotKey(None, HOTKEY_LONG_ID, MOD_SHIFT, VK_F1)
        )

        if not short_ok or not long_ok:
            if short_ok:
                user32.UnregisterHotKey(None, HOTKEY_SHORT_ID)
            if long_ok:
                user32.UnregisterHotKey(None, HOTKEY_LONG_ID)
            self.on_error(
                "No se pudieron registrar F1 y Shift+F1. "
                "Otra aplicación puede estar usando esas teclas."
            )
            return

        message = wintypes.MSG()
        try:
            while not self._stop_event.is_set():
                result = user32.GetMessageW(ctypes.byref(message), None, 0, 0)
                if result <= 0:
                    break
                if message.message == WM_HOTKEY:
                    if message.wParam == HOTKEY_SHORT_ID:
                        self.on_short_clip()
                    elif message.wParam == HOTKEY_LONG_ID:
                        self.on_long_clip()
        finally:
            user32.UnregisterHotKey(None, HOTKEY_SHORT_ID)
            user32.UnregisterHotKey(None, HOTKEY_LONG_ID)
