"""Domyślne wartości konfiguracji użytkownika."""

from pathlib import Path

# Ścieżki
DEFAULT_OUTPUT_DIR = str(
    Path.home() / "Library" / "Mobile Documents"
    / "iCloud~md~obsidian" / "Documents" / "Obsidian" / "11-Transcripts"
)
CONFIG_DIR = Path.home() / "Library" / "Application Support" / "Transrec"
CONFIG_FILE = CONFIG_DIR / "config.json"

# Tryby monitorowania
WATCH_MODES = ["auto", "manual", "specific"]
DEFAULT_WATCH_MODE = "auto"

# Języki
SUPPORTED_LANGUAGES = {
    "pl": "Polski",
    "en": "English",
    "auto": "Automatyczne wykrywanie",
}
DEFAULT_LANGUAGE = "pl"

# Modele Whisper
SUPPORTED_MODELS = {
    "tiny": "Tiny (szybki, niska jakość)",
    "base": "Base (szybki, średnia jakość)",
    "small": "Small (zalecany)",
    "medium": "Medium (wolny, wysoka jakość)",
    "large": "Large (bardzo wolny, najwyższa jakość)",
}
DEFAULT_MODEL = "small"

# Systemowe volumeny do ignorowania
SYSTEM_VOLUMES = {
    "Macintosh HD",
    "Recovery",
    "Preboot",
    "VM",
    "Data",
    "Update",
    "Shared",
    "System",
    "com.apple.TimeMachine.localsnapshots",
}
