from __future__ import annotations

import logging
import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

import pystray
from PIL import Image, ImageDraw

from .cloudflared_manager import CloudflaredManager
from .config import AppConfig, get_log_path, load_config, save_config
from .logging_utils import setup_logging
from .ollama_manager import OllamaManager


logger = logging.getLogger(__name__)


def _make_status_image(running: bool) -> Image.Image:
    # Ícone simples: bolinha verde (rodando) / vermelha (parado)
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    color = (16, 185, 129, 255) if running else (239, 68, 68, 255)  # emerald-500 / red-500
    draw.ellipse((8, 8, size - 8, size - 8), fill=color)
    return img


class TrayApp:
    def __init__(self) -> None:
        setup_logging()

        self.cfg = load_config()
        self.manager = OllamaManager(base_url=self.cfg.base_url, ollama_path=self.cfg.ollama_path)
        self.tunnel = CloudflaredManager(
            ollama_base_url=self.cfg.base_url, cloudflared_path=self.cfg.cloudflared_path
        )

        self.root = tk.Tk()
        self.root.title("Ollama Tray")
        self.root.withdraw()  # a UI fica só no tray; abre janela quando necessário

        self._stop_event = threading.Event()
        self._settings_win: tk.Toplevel | None = None

        self.icon = pystray.Icon(
            "OllamaTray",
            icon=_make_status_image(running=False),
            title="Ollama Tray",
            menu=pystray.Menu(
                # No pystray, "text" pode ser uma função que recebe o próprio item.
                pystray.MenuItem(lambda item: self._status_text(), None, enabled=False),
                pystray.Menu.SEPARATOR,
                # "action" recebe (icon, item) no backend win32
                pystray.MenuItem("Iniciar Ollama", lambda icon, item: self._safe(self.start_ollama)),
                pystray.MenuItem("Parar Ollama", lambda icon, item: self._safe(self.stop_ollama)),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Iniciar Tunnel", lambda icon, item: self._safe(self.start_tunnel)),
                pystray.MenuItem("Parar Tunnel", lambda icon, item: self._safe(self.stop_tunnel)),
                pystray.MenuItem("Copiar URL do Tunnel", lambda icon, item: self._safe(self.copy_tunnel_url)),
                pystray.MenuItem("Configurações", lambda icon, item: self.root.after(0, self.open_settings)),
                pystray.MenuItem("Abrir logs", lambda icon, item: self._safe(self.open_logs)),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Sair", lambda icon, item: self._safe(self.exit_app)),
            ),
        )

    def _status_text(self) -> str:
        st = self.manager.status()
        tn = self.tunnel.status()
        tunnel_txt = "Tunnel: Rodando" if tn.running else "Tunnel: Parado"
        if st.running:
            src = " (iniciado pelo app)" if st.started_by_app else ""
            return f"Status: Rodando{src} | {tunnel_txt}"
        return f"Status: Parado | {tunnel_txt}"

    def _notify(self, msg: str) -> None:
        try:
            self.icon.notify(msg, "Ollama Tray")
        except Exception:
            # nem todo backend suporta notify
            logger.info("NOTIFY: %s", msg)

    def _safe(self, fn):  # type: ignore[no-untyped-def]
        try:
            fn()
        except Exception as e:  # noqa: BLE001
            logger.exception("Erro: %s", e)
            self._notify(str(e))

    def start_ollama(self) -> None:
        self.manager.ensure_running()
        self._notify("Ollama está rodando.")

    def stop_ollama(self) -> None:
        self.manager.stop()
        self._notify("Ollama foi encerrado (iniciado pelo app).")

    def start_tunnel(self) -> None:
        self.tunnel.start()
        self._notify("Tunnel iniciado. Use 'Copiar URL do Tunnel' em alguns segundos.")

    def stop_tunnel(self) -> None:
        self.tunnel.stop()
        self._notify("Tunnel foi encerrado (iniciado pelo app).")

    def copy_tunnel_url(self) -> None:
        url = self.tunnel.status().public_url
        if not url:
            raise RuntimeError("URL do tunnel ainda não disponível. Aguarde alguns segundos e tente novamente.")

        def _copy() -> None:
            self.root.clipboard_clear()
            self.root.clipboard_append(url)

        self.root.after(0, _copy)
        self._notify("URL do tunnel copiada para a área de transferência.")

    def open_logs(self) -> None:
        log_path = get_log_path()
        if os.name == "nt":
            os.startfile(str(log_path))  # noqa: S606
        else:
            self._notify(f"Log: {log_path}")

    def open_settings(self) -> None:
        if self._settings_win and self._settings_win.winfo_exists():
            self._settings_win.deiconify()
            self._settings_win.lift()
            return

        win = tk.Toplevel(self.root)
        win.title("Configurações - Ollama Tray")
        win.geometry("520x230")
        win.resizable(False, False)
        self._settings_win = win

        base_url_var = tk.StringVar(value=self.cfg.base_url)
        ollama_path_var = tk.StringVar(value=self.cfg.ollama_path or "")
        cloudflared_path_var = tk.StringVar(value=getattr(self.cfg, "cloudflared_path", None) or "")

        frm = tk.Frame(win, padx=12, pady=12)
        frm.pack(fill="both", expand=True)

        tk.Label(frm, text="URL do Ollama (Base URL):").grid(row=0, column=0, sticky="w")
        tk.Entry(frm, textvariable=base_url_var, width=52).grid(row=1, column=0, sticky="we")

        tk.Label(frm, text="Caminho do ollama.exe (opcional):").grid(row=2, column=0, sticky="w", pady=(10, 0))
        path_row = tk.Frame(frm)
        path_row.grid(row=3, column=0, sticky="we")
        tk.Entry(path_row, textvariable=ollama_path_var, width=44).pack(side="left", fill="x", expand=True)

        def browse() -> None:
            p = filedialog.askopenfilename(
                title="Selecione o ollama.exe",
                filetypes=[("Ollama", "ollama.exe"), ("Executáveis", "*.exe"), ("Todos", "*.*")],
            )
            if p:
                ollama_path_var.set(p)

        tk.Button(path_row, text="Procurar...", command=browse).pack(side="left", padx=(8, 0))

        tk.Label(frm, text="Caminho do cloudflared.exe (opcional):").grid(
            row=4, column=0, sticky="w", pady=(10, 0)
        )
        cloud_row = tk.Frame(frm)
        cloud_row.grid(row=5, column=0, sticky="we")
        tk.Entry(cloud_row, textvariable=cloudflared_path_var, width=44).pack(
            side="left", fill="x", expand=True
        )

        def browse_cloudflared() -> None:
            p = filedialog.askopenfilename(
                title="Selecione o cloudflared.exe",
                filetypes=[("Cloudflared", "cloudflared.exe"), ("Executáveis", "*.exe"), ("Todos", "*.*")],
            )
            if p:
                cloudflared_path_var.set(p)

        tk.Button(cloud_row, text="Procurar...", command=browse_cloudflared).pack(side="left", padx=(8, 0))

        btns = tk.Frame(frm)
        btns.grid(row=6, column=0, sticky="e", pady=(14, 0))

        def save() -> None:
            base_url = base_url_var.get().strip()
            if not base_url.startswith("http://") and not base_url.startswith("https://"):
                messagebox.showerror("Erro", "A URL precisa começar com http:// ou https://")
                return

            new_cfg = AppConfig(
                base_url=base_url,
                ollama_path=(ollama_path_var.get().strip() or None),
                cloudflared_path=(cloudflared_path_var.get().strip() or None),
            )
            save_config(new_cfg)
            self.cfg = new_cfg
            self.manager.base_url = new_cfg.base_url
            self.manager.ollama_path = new_cfg.ollama_path
            self.tunnel.ollama_base_url = new_cfg.base_url
            self.tunnel.cloudflared_path = new_cfg.cloudflared_path
            self._notify("Configurações salvas.")
            win.withdraw()

        tk.Button(btns, text="Salvar", command=save, width=10).pack(side="right")
        tk.Button(btns, text="Cancelar", command=win.withdraw, width=10).pack(side="right", padx=(0, 8))

        def on_close() -> None:
            win.withdraw()

        win.protocol("WM_DELETE_WINDOW", on_close)

    def exit_app(self) -> None:
        self._stop_event.set()
        try:
            self.icon.stop()
        except Exception:
            pass
        self.root.after(0, self.root.quit)

    def _status_loop(self) -> None:
        last_running: bool | None = None
        while not self._stop_event.is_set():
            st = self.manager.status()
            if st.running != last_running:
                self.icon.icon = _make_status_image(running=st.running)
                last_running = st.running
            self.icon.title = self._status_text()
            self._stop_event.wait(3)

    def run(self) -> None:
        # roda o tray em thread separada; o Tk fica no main thread
        threading.Thread(target=self.icon.run, daemon=True).start()
        threading.Thread(target=self._status_loop, daemon=True).start()
        self.root.mainloop()


def run_app() -> None:
    TrayApp().run()
