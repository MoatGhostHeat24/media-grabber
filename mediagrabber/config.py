"""Small settings helper: defaults < config file < environment."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path

from . import APP_NAME

CONFIG_DIR = Path(os.environ.get("MEDIAGRABBER_CONFIG_DIR",
                                 Path.home() / f".{APP_NAME.lower()}"))
CONFIG_FILE = CONFIG_DIR / "settings.json"


@dataclass
class Settings:
    output_dir: str = "./downloads"
    filename_template: str = "{platform}/{title} [{id}].{ext}"
    audio_format: str = "mp3"
    max_parallel: int = 3
    theme: str = "dark"
    clipboard_watch: bool = False
    proxy: str | None = None
    user_agent: str = "default"
    extras: dict = field(default_factory=dict)


def load() -> Settings:
    data: dict = {}
    if CONFIG_FILE.exists():
        try:
            data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            data = {}
    known = {f: data[f] for f in Settings.__dataclass_fields__ if f in data}
    return Settings(**known)


def save(settings: Settings) -> Path:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(asdict(settings), indent=2), encoding="utf-8")
    return CONFIG_FILE


def resolve_path(settings: Settings, name: str) -> Path:
    return Path(settings.output_dir).expanduser().resolve() if name == "output_dir" \
        else Path(name).expanduser().resolve()
