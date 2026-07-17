"""Interfaz profesional de CutClip basada en CustomTkinter."""

from __future__ import annotations

import logging
import os
import queue
import sys
import threading
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from .app_info import (
    APP_AUTHOR,
    APP_BUILD,
    APP_COPYRIGHT,
    APP_DESCRIPTION,
    APP_INDEPENDENCE_NOTICE,
    APP_COMPATIBILITY,
    APP_TAGLINE,
    APP_NAME,
    APP_VERSION,
)
from .clip_manager import ClipManager
from .config import APP_DIR, load_config, save_config
from .diagnostics import run_local_diagnostics
from .hotkeys import GlobalHotkeys
from .notifications import Notifier
from .obs_controller import OBSController
from .startup import set_start_with_windows
from .tray import TrayController
from .windows_integration import apply_window_icon, configure_windows_identity

LOG_PATH = APP_DIR / "logs" / "cutclip.log"


def resource_path(relative: str) -> Path:
    """Resuelve recursos tanto en código fuente como dentro de PyInstaller."""
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))
    return base / relative


class CutClipApp:
    """Coordina UI, OBS, hotkeys, bandeja, notificaciones y clips."""

    BG = "#111318"
    PANEL = "#1B1E24"
    PANEL_ALT = "#23272F"
    BORDER = "#303641"
    TEXT = "#F4F6F8"
    MUTED = "#9DA6B2"
    GREEN = "#35C97A"
    YELLOW = "#F5B342"
    RED = "#E15B64"
    BLUE = "#3B82F6"
    BLUE_HOVER = "#2563EB"

    def __init__(self, force_silent: bool = False) -> None:
        self.config = load_config()
        self.events: queue.Queue[tuple[str, object]] = queue.Queue()
        self.busy = False
        self._closing = False
        self._hidden_to_tray = False
        # La aplicación siempre inicia en modo compacto. La configuración se
        # despliega únicamente cuando el usuario la solicita.
        self._settings_visible = False
        self._password_visible = False
        self._reconnect_stop = threading.Event()
        self._reconnect_thread: threading.Thread | None = None
        self._last_connection_state = False

        self._configure_logging()
        # Debe ejecutarse antes de crear CTk para que Windows no agrupe la
        # aplicación bajo el icono genérico de Python.
        configure_windows_identity()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()
        self.root.title(f"{APP_NAME} v{APP_VERSION}")
        self._compact_size = (760, 660)
        self._expanded_size = (920, 820)
        self.root.geometry(f"{self._compact_size[0]}x{self._compact_size[1]}")
        self.root.minsize(720, 620)
        self.root.configure(fg_color=self.BG)
        self.root.protocol("WM_DELETE_WINDOW", self._on_window_close)

        icon_ico = resource_path("assets/cutclip.ico")
        icon_png = resource_path("assets/cutclip.png")
        # Conservamos la referencia del PhotoImage para evitar que Tk la
        # descarte y vuelva a mostrar el icono de Python en la barra de tareas.
        self._window_icon_photo = apply_window_icon(self.root, icon_ico, icon_png)

        self.controller = OBSController(self.config, self._threadsafe_status)
        self.clip_manager = ClipManager(self.config)
        self.notifier = Notifier(APP_NAME, icon_png)
        self.hotkeys = GlobalHotkeys(
            on_short_clip=lambda: self.root.after(0, self.save_short_clip),
            on_long_clip=lambda: self.root.after(0, self.save_long_clip),
            on_error=lambda message: self.events.put(("warning", message)),
        )
        self.tray = TrayController(
            app_name=APP_NAME,
            on_show=lambda: self.root.after(0, self.show_window),
            on_short_clip=lambda: self.root.after(0, self.save_short_clip),
            on_long_clip=lambda: self.root.after(0, self.save_long_clip),
            on_open_clips=lambda: self.root.after(0, self.open_output_folder),
            on_open_logs=lambda: self.root.after(0, self.open_logs_folder),
            on_settings=lambda: self.root.after(0, self.show_settings),
            on_reconnect=lambda: self.root.after(0, self.connect_obs),
            on_about=lambda: self.root.after(0, self.show_about),
            on_exit=lambda: self.root.after(0, self.exit_application),
            base_icon=icon_png,
        )

        self.status_var = ctk.StringVar(value="OBS desconectado")
        self.detail_var = ctk.StringVar(value="F1: últimos 3 minutos  ·  Shift+F1: hasta 10 minutos")
        self.last_clip_var = ctk.StringVar(value="Último clip: —")
        self.last_time_var = ctk.StringVar(value="Hora: —")
        self.last_duration_var = ctk.StringVar(value="Duración: —")
        self.host_var = ctk.StringVar(value=self.config.obs_host)
        self.port_var = ctk.StringVar(value=str(self.config.obs_port))
        self.password_var = ctk.StringVar(value=self.config.obs_password)
        self.folder_var = ctk.StringVar(value=self.config.clips_folder)
        self.ffmpeg_var = ctk.StringVar(value=self.config.ffmpeg_path)
        self.minimize_to_tray_var = ctk.BooleanVar(value=self.config.minimize_to_tray)
        self.start_windows_var = ctk.BooleanVar(value=self.config.start_with_windows)
        self.silent_start_var = ctk.BooleanVar(value=self.config.silent_start)
        self.notifications_var = ctk.BooleanVar(value=self.config.notifications_enabled)

        self._build_ui()
        self.hotkeys.start()
        self.tray.start()
        self.root.after(100, self._process_events)
        self._start_reconnect_monitor()

        silent = force_silent or self.config.silent_start
        if silent:
            self.root.after(100, self.hide_to_tray)
        if self.config.auto_connect:
            self.root.after(450, self.connect_obs)

    def run(self) -> None:
        self.root.mainloop()

    def _configure_logging(self) -> None:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        logging.basicConfig(
            filename=LOG_PATH,
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s | %(message)s",
            encoding="utf-8",
        )
        logging.info("%s v%s iniciado", APP_NAME, APP_VERSION)

    def _build_ui(self) -> None:
        container = ctk.CTkFrame(self.root, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=24, pady=22)

        header = ctk.CTkFrame(container, fg_color=self.PANEL, corner_radius=14, border_width=1, border_color=self.BORDER)
        header.pack(fill="x")
        header.grid_columnconfigure(0, weight=1)

        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.grid(row=0, column=0, sticky="w", padx=20, pady=16)
        ctk.CTkLabel(title_box, text="CUTCLIP", font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"), text_color=self.TEXT).pack(anchor="w")
        ctk.CTkLabel(title_box, text=f"{APP_TAGLINE}  •  {APP_COMPATIBILITY}  •  v{APP_VERSION}", font=ctk.CTkFont(family="Segoe UI", size=12), text_color=self.MUTED).pack(anchor="w", pady=(2, 0))

        status_box = ctk.CTkFrame(header, fg_color="transparent")
        status_box.grid(row=0, column=1, sticky="e", padx=20)
        self.status_dot = ctk.CTkLabel(status_box, text="●", width=18, font=ctk.CTkFont(size=20), text_color=self.RED)
        self.status_dot.pack(side="left", padx=(0, 6))
        self.status_label = ctk.CTkLabel(status_box, textvariable=self.status_var, font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"), text_color=self.MUTED)
        self.status_label.pack(side="left")

        cards = ctk.CTkFrame(container, fg_color="transparent")
        cards.pack(fill="x", pady=(18, 14))
        cards.grid_columnconfigure((0, 1), weight=1, uniform="clipcards")
        self.short_button = self._create_clip_card(cards, 0, "●  CLIP RÁPIDO", "Últimos 3 minutos", "F1", self.save_short_clip)
        self.long_button = self._create_clip_card(cards, 1, "◉  REPLAY COMPLETO", "Hasta 10 minutos", "SHIFT + F1", self.save_long_clip)

        activity = ctk.CTkFrame(container, fg_color=self.PANEL_ALT, corner_radius=12, border_width=1, border_color=self.BORDER)
        activity.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(activity, textvariable=self.detail_var, text_color=self.MUTED, font=ctk.CTkFont(family="Segoe UI", size=12), anchor="w").pack(fill="x", padx=16, pady=11)

        summary = ctk.CTkFrame(container, fg_color=self.PANEL, corner_radius=12, border_width=1, border_color=self.BORDER)
        summary.pack(fill="x", pady=(0, 14))
        summary.grid_columnconfigure((0, 1, 2), weight=1)
        self._summary_item(summary, self.last_clip_var, 0)
        self._summary_item(summary, self.last_time_var, 1)
        self._summary_item(summary, self.last_duration_var, 2)

        settings_header = ctk.CTkFrame(container, fg_color="transparent")
        settings_header.pack(fill="x", pady=(0, 8))
        self.settings_toggle = ctk.CTkButton(settings_header, text="▼  CONFIGURACIÓN", width=155, height=32, fg_color=self.PANEL_ALT, hover_color=self.BORDER, corner_radius=8, command=self._toggle_settings)
        self.settings_toggle.pack(side="left")
        ctk.CTkButton(settings_header, text="Acerca de", width=100, height=32, fg_color=self.PANEL_ALT, hover_color=self.BORDER, corner_radius=8, command=self.show_about).pack(side="right")

        # El panel usa CTkScrollableFrame para que la ventana mantenga una
        # altura razonable incluso en pantallas pequeñas. La barra vertical
        # aparece solo cuando la configuración está desplegada.
        self.settings_panel = ctk.CTkScrollableFrame(
            container,
            fg_color=self.PANEL,
            corner_radius=14,
            border_width=1,
            border_color=self.BORDER,
            height=360,
            scrollbar_button_color=self.BORDER,
            scrollbar_button_hover_color="#434B59",
        )
        self._build_settings_fields(self.settings_panel)

        self.footer = ctk.CTkFrame(container, fg_color="transparent")
        self.footer.pack(fill="x", pady=(14, 0))
        ctk.CTkLabel(self.footer, text=f"{APP_NAME} v{APP_VERSION} • Diseñado y desarrollado por {APP_AUTHOR}", text_color="#6F7884", font=ctk.CTkFont(family="Segoe UI", size=10)).pack(side="left")
        ctk.CTkLabel(self.footer, text="OBS 30+ • WebSocket v5 • Hotkeys nativos", text_color="#6F7884", font=ctk.CTkFont(family="Segoe UI", size=10)).pack(side="right")

    def _summary_item(self, parent: ctk.CTkFrame, variable: ctk.StringVar, column: int) -> None:
        ctk.CTkLabel(parent, textvariable=variable, text_color=self.MUTED, font=ctk.CTkFont(family="Segoe UI", size=11), anchor="center").grid(row=0, column=column, sticky="ew", padx=12, pady=10)

    def _create_clip_card(self, parent: ctk.CTkFrame, column: int, eyebrow: str, title: str, hotkey: str, command: Callable[[], None]) -> ctk.CTkButton:
        button = ctk.CTkButton(
            parent,
            text=f"{eyebrow}\n\n{title}\n\n[ {hotkey} ]",
            height=176,
            corner_radius=16,
            fg_color=self.PANEL,
            hover_color="#292E37",
            border_width=2,
            border_color=self.BORDER,
            text_color=self.TEXT,
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            command=command,
        )
        button.grid(row=0, column=column, sticky="nsew", padx=(0, 8) if column == 0 else (8, 0))
        return button

    def _build_settings_fields(self, parent: ctk.CTkFrame) -> None:
        inner = ctk.CTkFrame(parent, fg_color="transparent")
        inner.pack(fill="x", padx=18, pady=18)
        inner.grid_columnconfigure(0, weight=3)
        inner.grid_columnconfigure(1, weight=1)

        self._add_field(inner, "Servidor", self.host_var, 0, 0)
        self._add_field(inner, "Puerto", self.port_var, 0, 1)
        ctk.CTkLabel(inner, text="Contraseña", text_color=self.MUTED, font=ctk.CTkFont(size=11)).grid(row=2, column=0, columnspan=2, sticky="w", pady=(12, 6))
        password_row = ctk.CTkFrame(inner, fg_color="transparent")
        password_row.grid(row=3, column=0, columnspan=2, sticky="ew")
        password_row.grid_columnconfigure(0, weight=1)
        self.password_entry = ctk.CTkEntry(password_row, textvariable=self.password_var, show="●", height=38, corner_radius=8, fg_color="#14171C", border_color=self.BORDER, text_color=self.TEXT)
        self.password_entry.grid(row=0, column=0, sticky="ew")
        self.password_toggle = ctk.CTkButton(password_row, text="👁", width=48, height=38, corner_radius=8, fg_color=self.PANEL_ALT, hover_color=self.BORDER, command=self._toggle_password)
        self.password_toggle.grid(row=0, column=1, padx=(8, 0))

        self._add_path_row(inner, "Carpeta de clips", self.folder_var, 4, self.choose_output_folder)
        self._add_path_row(inner, "FFmpeg", self.ffmpeg_var, 6, self.choose_ffmpeg)

        options = ctk.CTkFrame(inner, fg_color="transparent")
        options.grid(row=8, column=0, columnspan=2, sticky="ew", pady=(16, 0))
        for text, variable in (
            ("Minimizar a la bandeja al cerrar", self.minimize_to_tray_var),
            ("Iniciar con Windows", self.start_windows_var),
            ("Iniciar en modo silencioso", self.silent_start_var),
            ("Mostrar notificaciones de Windows", self.notifications_var),
        ):
            ctk.CTkCheckBox(options, text=text, variable=variable, text_color=self.MUTED, fg_color=self.BLUE, hover_color=self.BLUE_HOVER).pack(anchor="w", pady=3)

        actions = ctk.CTkFrame(inner, fg_color="transparent")
        actions.grid(row=9, column=0, columnspan=2, sticky="ew", pady=(18, 0))
        self.connect_button = ctk.CTkButton(actions, text="Conectar con OBS", height=38, corner_radius=8, fg_color=self.BLUE, hover_color=self.BLUE_HOVER, command=self.connect_obs)
        self.connect_button.pack(side="left")
        ctk.CTkButton(actions, text="Guardar configuración", height=38, corner_radius=8, fg_color=self.PANEL_ALT, hover_color=self.BORDER, command=self.save_visible_config).pack(side="left", padx=8)
        ctk.CTkButton(actions, text="Diagnóstico", height=38, corner_radius=8, fg_color=self.PANEL_ALT, hover_color=self.BORDER, command=self.show_diagnostics).pack(side="left")
        ctk.CTkButton(actions, text="Abrir clips", height=38, corner_radius=8, fg_color=self.PANEL_ALT, hover_color=self.BORDER, command=self.open_output_folder).pack(side="right")

    def _add_field(self, parent: ctk.CTkFrame, label: str, variable: ctk.StringVar, row: int, column: int) -> None:
        ctk.CTkLabel(parent, text=label, text_color=self.MUTED, font=ctk.CTkFont(size=11)).grid(row=row, column=column, sticky="w", padx=(0, 8), pady=(0, 6))
        ctk.CTkEntry(parent, textvariable=variable, height=38, corner_radius=8, fg_color="#14171C", border_color=self.BORDER, text_color=self.TEXT).grid(row=row + 1, column=column, sticky="ew", padx=(0, 8))

    def _add_path_row(self, parent: ctk.CTkFrame, label: str, variable: ctk.StringVar, row: int, command: Callable[[], None]) -> None:
        ctk.CTkLabel(parent, text=label, text_color=self.MUTED, font=ctk.CTkFont(size=11)).grid(row=row, column=0, columnspan=2, sticky="w", pady=(12, 6))
        path_row = ctk.CTkFrame(parent, fg_color="transparent")
        path_row.grid(row=row + 1, column=0, columnspan=2, sticky="ew")
        path_row.grid_columnconfigure(0, weight=1)
        ctk.CTkEntry(path_row, textvariable=variable, height=38, corner_radius=8, fg_color="#14171C", border_color=self.BORDER, text_color=self.TEXT).grid(row=0, column=0, sticky="ew")
        ctk.CTkButton(path_row, text="Buscar", width=82, height=38, corner_radius=8, fg_color=self.PANEL_ALT, hover_color=self.BORDER, command=command).grid(row=0, column=1, padx=(8, 0))

    def _toggle_settings(self) -> None:
        """Muestra u oculta Configuración de forma inmediata.

        CutClip es una utilidad ligera que debe reaccionar al instante.
        Por eso no se interpolan tamaños ni se ejecutan animaciones: el panel se
        inserta o se retira en una sola operación y la ventana adopta directamente
        el tamaño correspondiente.
        """
        if self._settings_visible:
            self._settings_visible = False
            self.settings_toggle.configure(text="▼  CONFIGURACIÓN")
            self.settings_panel.pack_forget()
            self._set_window_size(*self._compact_size)
            return

        self._settings_visible = True
        self.settings_toggle.configure(text="▲  CONFIGURACIÓN")
        self.settings_panel.pack(fill="both", expand=True, before=self.footer)
        self._set_window_size(*self._expanded_target_size())

    def _expanded_target_size(self) -> tuple[int, int]:
        """Calcula un tamaño expandido que nunca excede el área visible."""
        screen_width = max(800, self.root.winfo_screenwidth())
        screen_height = max(700, self.root.winfo_screenheight())
        width = min(self._expanded_size[0], screen_width - 80)
        height = min(self._expanded_size[1], screen_height - 100)
        return max(width, self._compact_size[0]), max(height, self._compact_size[1])

    def _set_window_size(self, width: int, height: int) -> None:
        """Cambia el tamaño sin animaciones y conserva la posición actual."""
        self.root.update_idletasks()
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def _toggle_password(self) -> None:
        self._password_visible = not self._password_visible
        self.password_entry.configure(show="" if self._password_visible else "●")
        self.password_toggle.configure(text="🙈" if self._password_visible else "👁")

    def save_visible_config(self) -> bool:
        try:
            self.config.obs_host = self.host_var.get().strip() or "127.0.0.1"
            self.config.obs_port = int(self.port_var.get().strip())
            self.config.obs_password = self.password_var.get()
            self.config.clips_folder = self.folder_var.get().strip()
            self.config.ffmpeg_path = self.ffmpeg_var.get().strip() or "ffmpeg"
            self.config.minimize_to_tray = bool(self.minimize_to_tray_var.get())
            self.config.start_with_windows = bool(self.start_windows_var.get())
            self.config.silent_start = bool(self.silent_start_var.get())
            self.config.notifications_enabled = bool(self.notifications_var.get())
            save_config(self.config)
            set_start_with_windows(self.config.start_with_windows)
            self.detail_var.set("Configuración guardada correctamente.")
            logging.info("Configuración guardada")
            return True
        except (ValueError, OSError) as exc:
            messagebox.showerror("Configuración inválida", str(exc), parent=self.root)
            return False

    def connect_obs(self) -> None:
        if self.busy or not self.save_visible_config():
            return
        self.tray.set_state("reconnecting", "Conectando con OBS…")
        self.status_dot.configure(text_color=self.YELLOW)
        self.status_var.set("Conectando…")
        self._run_task("Conectando con OBS…", self._connect_worker)

    def save_short_clip(self) -> None:
        self._run_task("Guardando los últimos 3 minutos…", self._short_clip_worker)

    def save_long_clip(self) -> None:
        self._run_task("Guardando el Replay completo…", self._long_clip_worker)

    def _connect_worker(self) -> None:
        version = self.controller.connect()
        self.events.put(("connected", f"OBS {version['obs_version']} conectado"))

    def _short_clip_worker(self) -> None:
        source = self.controller.save_replay()
        destination = self.clip_manager.create_short_clip(source)
        self.events.put(("clip_saved", (destination, "3 minutos")))

    def _long_clip_worker(self) -> None:
        source = self.controller.save_replay()
        destination = self.clip_manager.keep_long_clip(source)
        self.events.put(("clip_saved", (destination, "hasta 10 minutos")))

    def _run_task(self, message: str, worker: Callable[[], None]) -> None:
        if self.busy:
            self.detail_var.set("Ya se está procesando otra operación.")
            return
        self.busy = True
        self._set_buttons_enabled(False)
        self.detail_var.set(message)

        def guarded_worker() -> None:
            try:
                worker()
            except Exception as exc:
                logging.exception("Error en operación")
                self.events.put(("error", self._friendly_error(exc)))
            finally:
                self.events.put(("idle", ""))

        threading.Thread(target=guarded_worker, daemon=True).start()

    def _process_events(self) -> None:
        """Procesa eventos de fondo sin congelar la interfaz.

        Se limita la cantidad por ciclo para que una ráfaga de mensajes no
        monopolice el hilo principal de Tk.
        """
        if self._closing:
            return
        processed = 0
        try:
            while processed < 30:
                event, payload = self.events.get_nowait()
                processed += 1
                if event == "status":
                    self.status_var.set(str(payload))
                elif event == "connected":
                    message = str(payload)
                    self._set_connected_ui(True, message)
                    self.detail_var.set("F1: últimos 3 minutos  ·  Shift+F1: hasta 10 minutos")
                    if not self._last_connection_state:
                        self._notify("OBS conectado", "La conexión con OBS Studio está lista.")
                    self._last_connection_state = True
                elif event == "disconnected":
                    message = str(payload)
                    self._set_connected_ui(False, message)
                    if self._last_connection_state:
                        self._notify("OBS desconectado", "Intentando reconectar automáticamente…")
                    self._last_connection_state = False
                elif event == "clip_saved":
                    destination, duration = payload  # type: ignore[misc]
                    self._record_last_clip(Path(destination), str(duration))
                elif event == "warning":
                    self.detail_var.set(str(payload))
                    logging.warning("%s", payload)
                elif event == "error":
                    message = str(payload)
                    self.detail_var.set(message)
                    self._set_connected_ui(False, "OBS desconectado")
                    self._notify(APP_NAME, message)
                    if not self._hidden_to_tray:
                        messagebox.showerror(APP_NAME, message, parent=self.root)
                elif event == "idle":
                    self.busy = False
                    self._set_buttons_enabled(True)
        except queue.Empty:
            pass
        self.root.after(70 if processed else 140, self._process_events)

    def _record_last_clip(self, destination: Path, duration: str) -> None:
        now = datetime.now().strftime("%I:%M:%S %p")
        self.detail_var.set(f"Clip guardado correctamente: {destination.name}")
        self.last_clip_var.set(f"Último clip: {destination.name}")
        self.last_time_var.set(f"Hora: {now}")
        self.last_duration_var.set(f"Duración: {duration}")
        logging.info("Clip guardado: %s", destination)
        self._notify("Clip guardado", f"{duration} • {destination.name}")

    def _start_reconnect_monitor(self) -> None:
        if self._reconnect_thread and self._reconnect_thread.is_alive():
            return

        def monitor() -> None:
            while not self._reconnect_stop.wait(max(2, self.config.reconnect_interval)):
                if self._closing or not self.config.auto_reconnect:
                    continue
                if self.controller.connected and self.controller.ping():
                    continue
                self.events.put(("disconnected", "OBS desconectado · reconectando…"))
                self.tray.set_state("reconnecting", "Reconectando con OBS…")
                try:
                    version = self.controller.connect()
                    self.events.put(("connected", f"OBS {version['obs_version']} conectado"))
                except Exception:
                    logging.debug("Reconexión pendiente", exc_info=True)
                    self.tray.set_state("disconnected", "OBS desconectado")

        self._reconnect_thread = threading.Thread(target=monitor, name="OBSReconnectMonitor", daemon=True)
        self._reconnect_thread.start()

    def _threadsafe_status(self, message: str) -> None:
        self.events.put(("status", message))


    def show_diagnostics(self) -> None:
        """Muestra un reporte sencillo que el usuario puede comprender o copiar."""
        items = run_local_diagnostics(self.config, self.controller.connected and self.controller.ping())
        lines = [f"{'✅' if item.ok else '❌'} {item.name}: {item.detail}" for item in items]
        overall = all(item.ok for item in items)
        lines.extend(("", "Estado general: " + ("LISTO PARA USAR" if overall else "REQUIERE ATENCIÓN")))
        messagebox.showinfo(f"Diagnóstico de {APP_NAME}", "\n".join(lines), parent=self.root)

    def choose_output_folder(self) -> None:
        selected = filedialog.askdirectory(initialdir=self.folder_var.get() or str(Path.home()))
        if selected:
            self.folder_var.set(selected)

    def choose_ffmpeg(self) -> None:
        selected = filedialog.askopenfilename(title="Seleccionar ffmpeg.exe", filetypes=[("FFmpeg", "ffmpeg.exe"), ("Ejecutables", "*.exe"), ("Todos", "*.*")])
        if selected:
            self.ffmpeg_var.set(selected)

    def open_output_folder(self) -> None:
        folder = Path(self.folder_var.get()).expanduser()
        folder.mkdir(parents=True, exist_ok=True)
        self._open_path(folder)

    def open_logs_folder(self) -> None:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        self._open_path(LOG_PATH.parent)

    @staticmethod
    def _open_path(path: Path) -> None:
        if os.name == "nt":
            os.startfile(path)  # type: ignore[attr-defined]

    def show_about(self) -> None:
        dialog = ctk.CTkToplevel(self.root)
        dialog.title(f"Acerca de {APP_NAME}")
        dialog.geometry("520x520")
        dialog.resizable(False, False)
        dialog.configure(fg_color=self.BG)
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(dialog, text="CUTCLIP", font=ctk.CTkFont(size=25, weight="bold"), text_color=self.TEXT).grid(row=0, column=0, pady=(26, 4))
        ctk.CTkLabel(dialog, text=APP_TAGLINE, text_color=self.MUTED).grid(row=1, column=0)
        ctk.CTkLabel(dialog, text=f"Versión {APP_VERSION}  •  Build {APP_BUILD}", text_color=self.MUTED).grid(row=2, column=0, pady=(3, 0))
        ctk.CTkLabel(dialog, text=APP_COMPATIBILITY, text_color=self.GREEN).grid(row=3, column=0, pady=(18, 2))
        ctk.CTkLabel(dialog, text="Diseñado y desarrollado por", text_color=self.MUTED).grid(row=4, column=0, pady=(16, 4))
        ctk.CTkLabel(dialog, text=APP_AUTHOR, font=ctk.CTkFont(size=20, weight="bold"), text_color=self.TEXT).grid(row=5, column=0)
        ctk.CTkLabel(dialog, text=APP_DESCRIPTION, wraplength=420, justify="center", text_color=self.MUTED).grid(row=6, column=0, padx=30, pady=(18, 8))
        ctk.CTkLabel(dialog, text=APP_INDEPENDENCE_NOTICE, wraplength=420, justify="center", text_color="#7E8794", font=ctk.CTkFont(size=11)).grid(row=7, column=0, padx=30, pady=(4, 10))
        ctk.CTkLabel(dialog, text=APP_COPYRIGHT, text_color="#6F7884", font=ctk.CTkFont(size=10)).grid(row=8, column=0, pady=(4, 14))

        buttons = ctk.CTkFrame(dialog, fg_color="transparent")
        buttons.grid(row=9, column=0)
        ctk.CTkButton(buttons, text="Copiar información", fg_color=self.PANEL_ALT, hover_color=self.BORDER, command=lambda: self._copy_about_info(dialog)).pack(side="left", padx=6)
        ctk.CTkButton(buttons, text="Cerrar", fg_color=self.BLUE, hover_color=self.BLUE_HOVER, command=dialog.destroy).pack(side="left", padx=6)

    def _copy_about_info(self, dialog: ctk.CTkToplevel) -> None:
        info = (
            f"{APP_NAME}\nVersión: {APP_VERSION}\nBuild: {APP_BUILD}\n\n"
            f"Diseñado y desarrollado por {APP_AUTHOR}\n"
            f"Sistema operativo: {sys.platform}\nEstado OBS: {self.status_var.get()}"
        )
        self.root.clipboard_clear()
        self.root.clipboard_append(info)
        self.detail_var.set("Información de la aplicación copiada al portapapeles.")
        dialog.after(150, dialog.focus_force)

    def show_settings(self) -> None:
        self.show_window()
        if not self._settings_visible:
            self._toggle_settings()
        self.root.lift()
        self.root.focus_force()

    def hide_to_tray(self) -> None:
        self._hidden_to_tray = True
        self.root.withdraw()

    def show_window(self) -> None:
        self._hidden_to_tray = False
        self.root.deiconify()
        self.root.state("normal")
        self.root.lift()
        self.root.focus_force()

    def _on_window_close(self) -> None:
        if not self.config.minimize_to_tray:
            self.exit_application()
            return
        if self.config.show_tray_notice:
            choice = messagebox.askyesnocancel(
                APP_NAME,
                f"{APP_NAME} seguirá funcionando en segundo plano.\n\n"
                "Sí: minimizar a la bandeja\nNo: salir completamente\nCancelar: volver a la aplicación",
                parent=self.root,
            )
            if choice is None:
                return
            if choice is False:
                self.exit_application()
                return
            self.config.show_tray_notice = False
            save_config(self.config)
        self.hide_to_tray()

    def exit_application(self) -> None:
        if self._closing:
            return
        self._closing = True
        self._reconnect_stop.set()
        self.hotkeys.stop()
        self.controller.disconnect()
        self.tray.stop()
        logging.info("%s cerrado", APP_NAME)
        self.root.after(50, self.root.destroy)

    def _notify(self, title: str, message: str) -> None:
        if self.config.notifications_enabled:
            threading.Thread(target=self.notifier.show, args=(title, message), daemon=True).start()

    def _set_buttons_enabled(self, enabled: bool) -> None:
        state = "normal" if enabled else "disabled"
        self.short_button.configure(state=state)
        self.long_button.configure(state=state)
        self.connect_button.configure(state=state)

    def _set_connected_ui(self, connected: bool, text: str) -> None:
        self.status_var.set(text)
        self.status_dot.configure(text_color=self.GREEN if connected else self.RED)
        self.status_label.configure(text_color=self.TEXT if connected else self.MUTED)
        self.connect_button.configure(text="Reconectar" if connected else "Conectar con OBS", fg_color=self.GREEN if connected else self.BLUE, hover_color="#2BA966" if connected else self.BLUE_HOVER)
        self.tray.set_state("connected" if connected else "disconnected", text)

    @staticmethod
    def _friendly_error(exc: Exception) -> str:
        message = str(exc).strip()
        lowered = message.lower()
        if "authentication" in lowered or "password" in lowered:
            return "No se pudo autenticar con OBS. Revisa la contraseña del servidor WebSocket."
        if "connection refused" in lowered or "actively refused" in lowered or "no se encontró el servidor" in lowered:
            return ("No se encontró OBS WebSocket. Abre OBS y entra en Herramientas → "
                    "Configuración del servidor WebSocket para activarlo.")
        if "ffmpeg" in lowered:
            return ("F1 necesita FFmpeg para recortar el clip. Reinstala CutClip v1.0.1 "
                    "con FFmpeg incluido. Mientras tanto, Shift+F1 guarda el Replay completo.")
        if "timed out" in lowered or "timeout" in lowered:
            return "OBS tardó demasiado en responder. Comprueba la conexión y vuelve a intentar."
        return message or "Ocurrió un error inesperado. Revisa la carpeta de logs."
