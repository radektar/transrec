"""Main entry point for Olympus Transcriber daemon."""

import sys

from src.env_loader import load_env_file

# Load environment variables before importing config-dependent modules
load_env_file()

from src.logger import logger
from src.app_core import OlympusTranscriber


def main():
    """Main entry point."""
    try:
        app = OlympusTranscriber()
        app.start()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
    
    sys.exit(0)


if __name__ == "__main__":
    main()


