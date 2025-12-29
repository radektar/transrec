"""User settings management."""

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Optional

from src.config.defaults import (
    CONFIG_FILE,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_WATCH_MODE,
    DEFAULT_LANGUAGE,
    DEFAULT_MODEL,
)


@dataclass
class UserSettings:
    """Ustawienia użytkownika (persystentne w JSON)."""

    # Źródła nagrań
    watch_mode: str = DEFAULT_WATCH_MODE
    watched_volumes: List[str] = field(default_factory=list)

    # Ścieżki
    output_dir: str = DEFAULT_OUTPUT_DIR

    # Transkrypcja
    language: str = DEFAULT_LANGUAGE
    whisper_model: str = DEFAULT_MODEL

    # AI (PRO)
    enable_ai_summaries: bool = False
    ai_api_key: Optional[str] = None

    # UI
    show_notifications: bool = True
    start_at_login: bool = False

    # Stan wizarda
    setup_completed: bool = False

    @classmethod
    def load(cls) -> "UserSettings":
        """Wczytaj ustawienia z pliku JSON."""
        config_path = cls.config_path()
        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return cls(**data)
            except (json.JSONDecodeError, TypeError):
                pass
        return cls()

    def save(self) -> None:
        """Zapisz ustawienia do pliku JSON."""
        config_path = self.config_path()
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(asdict(self), f, indent=2, ensure_ascii=False)

    @staticmethod
    def config_path() -> Path:
        """Zwróć ścieżkę do pliku konfiguracji."""
        return CONFIG_FILE
