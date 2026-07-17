"""Integración nativa con Windows.

Este módulo concentra los detalles específicos del sistema operativo para que la
interfaz principal no dependa directamente de ``ctypes``. Separarlo facilita el
mantenimiento, las pruebas y la futura compatibilidad con otros sistemas.
"""

from __future__ import annotations

import ctypes
import logging
import os
from pathlib import Path
from typing import Any


APP_USER_MODEL_ID = "BryantBrugal.CutClip.1.0.1"


def configure_windows_identity() -> None:
    """Asigna una identidad propia al proceso antes de crear la ventana.

    Windows agrupa los procesos de Python bajo el icono de ``python.exe`` si no
    se define un AppUserModelID explícito. Esta llamada hace que la ventana use
    el icono y la identidad de CutClip en la barra de tareas.
    """
    if os.name != "nt":
        return
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            APP_USER_MODEL_ID
        )
    except Exception:
        logging.exception("No se pudo establecer el AppUserModelID de Windows")


def apply_window_icon(window: Any, ico_path: Path, png_path: Path) -> Any | None:
    """Aplica iconos ICO y PNG a una ventana Tk/CustomTkinter.

    Se devuelve la referencia de ``PhotoImage`` para que el recolector de
    basura no la elimine mientras la ventana continúa abierta.
    """
    photo = None
    try:
        if ico_path.exists():
            window.iconbitmap(default=str(ico_path))

            # Refuerzo nativo para ejecuciones desde pythonw.exe. Tk aplica el
            # icono a la ventana, pero Windows puede conservar el de Python en
            # la barra de tareas hasta que recibe WM_SETICON explícitamente.
            if os.name == "nt":
                window.update_idletasks()
                hwnd = int(window.winfo_id())
                load_image = ctypes.windll.user32.LoadImageW
                load_image.restype = ctypes.c_void_p
                image_icon = 1
                load_from_file = 0x0010
                default_size = 0x0040
                handle = load_image(
                    None, str(ico_path), image_icon, 0, 0,
                    load_from_file | default_size,
                )
                if handle:
                    ctypes.windll.user32.SendMessageW(hwnd, 0x0080, 0, handle)
                    ctypes.windll.user32.SendMessageW(hwnd, 0x0080, 1, handle)
                    # Guardar el handle evita que se pierda durante la sesión.
                    window._native_icon_handle = handle
    except Exception:
        logging.exception("No se pudo aplicar el icono ICO")

    try:
        if png_path.exists():
            from tkinter import PhotoImage

            photo = PhotoImage(file=str(png_path))
            window.iconphoto(True, photo)
    except Exception:
        logging.exception("No se pudo aplicar el icono PNG")
    return photo
