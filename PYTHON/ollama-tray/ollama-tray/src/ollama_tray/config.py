from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppConfig:
    base_url: str = "http://localhost:11434"
    ollama_path: str | None = None
    cloudflared_path: str | None = None


def get_app_dir() -> Path:
    appdata = os.environ.get("APPDATA")
    if appdata:
        return Path(appdata) / "OllamaTray"
    return Path.home() / ".ollama_tray"


def get_config_path() -> Path:
    return get_app_dir() / "config.json"


def get_log_path() -> Path:
    return get_app_dir() / "app.log"


def load_config() -> AppConfig:
    path = get_config_path()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return AppConfig(
            base_url=str(data.get("base_url") or "http://localhost:11434"),
            ollama_path=(str(data["ollama_path"]) if data.get("ollama_path") else None),
            cloudflared_path=(str(data["cloudflared_path"]) if data.get("cloudflared_path") else None),
        )
    except FileNotFoundError:
        return AppConfig()
    except Exception:
        # se o JSON estiver corrompido, volta pro default
        return AppConfig()


def save_config(cfg: AppConfig) -> None:
    app_dir = get_app_dir()
    app_dir.mkdir(parents=True, exist_ok=True)
    get_config_path().write_text(
        json.dumps(asdict(cfg), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
