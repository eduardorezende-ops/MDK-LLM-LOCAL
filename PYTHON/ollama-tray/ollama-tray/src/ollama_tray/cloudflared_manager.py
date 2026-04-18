from __future__ import annotations

import logging
import os
import re
import shutil
import subprocess
import threading
from dataclasses import dataclass


logger = logging.getLogger(__name__)

_URL_RE = re.compile(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com")


@dataclass(frozen=True)
class TunnelStatus:
    running: bool
    started_by_app: bool
    public_url: str | None


def _resolve_cloudflared_path(configured_path: str | None) -> str:
    if configured_path and os.path.exists(configured_path):
        return configured_path

    in_path = shutil.which("cloudflared")
    if in_path:
        return in_path

    raise FileNotFoundError(
        "Não encontrei o executável do Cloudflared (cloudflared.exe). "
        "Instale (winget) ou aponte o caminho nas Configurações."
    )


class CloudflaredManager:
    def __init__(self, ollama_base_url: str, cloudflared_path: str | None) -> None:
        self.ollama_base_url = ollama_base_url
        self.cloudflared_path = cloudflared_path

        self._process: subprocess.Popen[bytes] | None = None
        self._started_by_app = False
        self._public_url: str | None = None
        self._reader_thread: threading.Thread | None = None

    def status(self) -> TunnelStatus:
        running = self._process is not None and self._process.poll() is None
        return TunnelStatus(running=running, started_by_app=self._started_by_app, public_url=self._public_url)

    def start(self) -> None:
        if self._process is not None and self._process.poll() is None:
            logger.info("Start ignorado: tunnel já está rodando.")
            return

        exe = _resolve_cloudflared_path(self.cloudflared_path)
        logger.info("Iniciando Cloudflare Tunnel: %s tunnel --url %s", exe, self.ollama_base_url)

        creationflags = 0
        if os.name == "nt" and hasattr(subprocess, "CREATE_NO_WINDOW"):
            creationflags = subprocess.CREATE_NO_WINDOW  # type: ignore[attr-defined]

        # Importante: stdout em PIPE para capturar a URL do quick tunnel.
        self._process = subprocess.Popen(  # noqa: S603,S607
            [exe, "tunnel", "--url", self.ollama_base_url],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            creationflags=creationflags,
        )
        self._started_by_app = True
        self._public_url = None

        def _reader() -> None:
            if not self._process or not self._process.stdout:
                return
            for raw in self._process.stdout:
                line = raw.decode("utf-8", errors="ignore")
                m = _URL_RE.search(line)
                if m and not self._public_url:
                    self._public_url = m.group(0)
                    logger.info("Tunnel URL detectada: %s", self._public_url)
                # Continua lendo para não encher o buffer.

        self._reader_thread = threading.Thread(target=_reader, daemon=True)
        self._reader_thread.start()

    def stop(self, timeout_sec: int = 5) -> None:
        if not self._started_by_app:
            raise RuntimeError("Não vou parar o tunnel porque ele não foi iniciado por este app.")

        if not self._process:
            raise RuntimeError("Processo do cloudflared não está disponível para encerrar.")

        if self._process.poll() is not None:
            logger.info("Processo do cloudflared já terminou.")
            return

        logger.info("Encerrando cloudflared (pid=%s)...", self._process.pid)
        self._process.terminate()
        try:
            self._process.wait(timeout=timeout_sec)
        except subprocess.TimeoutExpired:
            logger.warning("Terminate não respondeu; forçando kill...")
            self._process.kill()
            self._process.wait(timeout=timeout_sec)
