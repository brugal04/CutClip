"""Control seguro de OBS Studio mediante obs-websocket v5."""

from __future__ import annotations

import threading
import time
from pathlib import Path
from typing import Callable, Optional

import obsws_python as obs

from .config import AppConfig


StatusCallback = Callable[[str], None]


class OBSController:
    """Encapsula conexión, verificación y solicitudes al servidor de OBS."""

    def __init__(self, config: AppConfig, status_callback: StatusCallback) -> None:
        self.config = config
        self.status_callback = status_callback
        self._client: Optional[obs.ReqClient] = None
        self._lock = threading.RLock()

    @property
    def connected(self) -> bool:
        """Indica si existe un cliente activo."""
        return self._client is not None

    def connect(self) -> dict[str, str]:
        """Conecta con OBS y prueba puertos locales conocidos cuando es necesario."""
        with self._lock:
            self.disconnect()
            client, version, selected_port = self._connect_with_detection()
            # Guardar el puerto detectado permite que el próximo inicio sea directo.
            self.config.obs_port = selected_port
            obs_version = str(getattr(version, "obs_version", "desconocida"))
            websocket_version = str(
                getattr(version, "obs_web_socket_version", "desconocida")
            )

            major = self._parse_major(obs_version)
            if major is not None and major < 30:
                try:
                    client.disconnect()
                except Exception:
                    pass
                raise RuntimeError(
                    f"OBS {obs_version} no es compatible. Se requiere OBS 30.0.0 o superior."
                )

            self._client = client
            self.status_callback(
                f"Conectado a OBS {obs_version} · WebSocket {websocket_version}"
            )
            return {
                "obs_version": obs_version,
                "websocket_version": websocket_version,
            }


    def _connect_with_detection(self) -> tuple[obs.ReqClient, object, int]:
        """Prueba primero la configuración y luego puertos WebSocket habituales.

        Solo se detectan puertos en localhost para evitar escaneos de red. La
        contraseña escrita por el usuario se reutiliza en cada intento.
        """
        configured_port = int(self.config.obs_port)
        ports = [configured_port]
        if self.config.obs_host.strip().lower() in {"127.0.0.1", "localhost", "::1"}:
            ports.extend(port for port in (4455, 4444, 4456) if port not in ports)

        last_error: Exception | None = None
        for port in ports:
            client: obs.ReqClient | None = None
            try:
                client = obs.ReqClient(
                    host=self.config.obs_host,
                    port=port,
                    password=self.config.obs_password,
                    timeout=3,
                )
                return client, client.get_version(), port
            except Exception as exc:
                last_error = exc
                if client is not None:
                    try:
                        client.disconnect()
                    except Exception:
                        pass

        if last_error is not None:
            raise last_error
        raise ConnectionError("No se encontró el servidor WebSocket de OBS.")

    def ping(self) -> bool:
        """Comprueba la conexión con una solicitud ligera."""
        with self._lock:
            if self._client is None:
                return False
            try:
                self._client.get_version()
                return True
            except Exception:
                self.disconnect()
                return False

    def disconnect(self) -> None:
        """Libera el cliente sin propagar errores durante el cierre."""
        client, self._client = self._client, None
        if client is not None:
            try:
                client.disconnect()
            except Exception:
                pass

    def ensure_replay_buffer(self) -> None:
        """Inicia el Replay Buffer si está detenido y la opción lo permite."""
        client = self._require_client()
        status = client.get_replay_buffer_status()
        active = bool(getattr(status, "output_active", False))
        if active:
            return
        if not self.config.auto_start_replay_buffer:
            raise RuntimeError("El Replay Buffer está detenido en OBS.")
        client.start_replay_buffer()
        self.status_callback("Replay Buffer iniciado automáticamente.")

    def save_replay(self) -> Path:
        """Guarda el Replay Buffer y devuelve la ruta creada por OBS."""
        with self._lock:
            client = self._require_client()
            self.ensure_replay_buffer()
            previous_path = self._get_last_replay_path(client)
            client.save_replay_buffer()

            deadline = time.monotonic() + 20
            while time.monotonic() < deadline:
                time.sleep(0.35)
                current_path = self._get_last_replay_path(client)
                if current_path and current_path != previous_path:
                    path = Path(current_path)
                    if self._wait_until_file_stable(path):
                        return path

            raise TimeoutError(
                "OBS recibió la orden, pero no informó el nuevo archivo en 20 segundos."
            )

    @staticmethod
    def _get_last_replay_path(client: obs.ReqClient) -> str:
        try:
            response = client.get_last_replay_buffer_replay()
            return str(getattr(response, "saved_replay_path", "") or "")
        except Exception:
            return ""

    @staticmethod
    def _wait_until_file_stable(path: Path, timeout: float = 20.0) -> bool:
        deadline = time.monotonic() + timeout
        last_size = -1
        stable_checks = 0
        while time.monotonic() < deadline:
            if not path.exists():
                time.sleep(0.25)
                continue
            try:
                size = path.stat().st_size
            except OSError:
                time.sleep(0.25)
                continue
            if size > 0 and size == last_size:
                stable_checks += 1
                if stable_checks >= 3:
                    return True
            else:
                stable_checks = 0
                last_size = size
            time.sleep(0.35)
        return path.exists() and path.stat().st_size > 0

    def _require_client(self) -> obs.ReqClient:
        if self._client is None:
            raise ConnectionError("La aplicación no está conectada a OBS.")
        return self._client

    @staticmethod
    def _parse_major(version: str) -> Optional[int]:
        try:
            return int(version.split(".", 1)[0])
        except (TypeError, ValueError):
            return None
