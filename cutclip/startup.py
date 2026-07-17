"""Integración opcional con el inicio de Windows."""

from __future__ import annotations

import os
import sys
from pathlib import Path

RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
VALUE_NAME = "CutClip"


def executable_command(silent: bool = True) -> str:
    """Devuelve el comando correcto tanto en fuente como en ejecutable."""
    if getattr(sys, "frozen", False):
        target = Path(sys.executable)
        command = f'"{target}"'
    else:
        target = Path(__file__).resolve().parents[1] / "app.py"
        command = f'"{sys.executable}" "{target}"'
    if silent:
        command += " --silent"
    return command


def set_start_with_windows(enabled: bool) -> None:
    """Activa o desactiva el inicio automático en el usuario actual."""
    if os.name != "nt":
        return
    import winreg

    with winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        RUN_KEY,
        0,
        winreg.KEY_SET_VALUE,
    ) as key:
        if enabled:
            winreg.SetValueEx(
                key, VALUE_NAME, 0, winreg.REG_SZ, executable_command(silent=True)
            )
        else:
            try:
                winreg.DeleteValue(key, VALUE_NAME)
            except FileNotFoundError:
                pass
