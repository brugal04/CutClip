"""Punto de entrada mínimo de CutClip.

Mantener este archivo pequeño acelera el diagnóstico y evita mezclar el
arranque con la lógica de la interfaz.
"""

from __future__ import annotations

import argparse

from cutclip.ui import CutClipApp


def main() -> None:
    """Procesa opciones de arranque y ejecuta la aplicación."""
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--silent", action="store_true")
    args, _unknown = parser.parse_known_args()
    CutClipApp(force_silent=args.silent).run()


if __name__ == "__main__":
    main()
