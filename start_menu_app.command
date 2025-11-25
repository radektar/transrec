#!/bin/bash
# Launch Olympus Transcriber menu app within the project venv.

cd "$(dirname "$0")" || exit 1

# Use zsh login shell to ensure PATH/env matches user session
source venv/bin/activate
export PYTHONPATH="$(pwd)"
python src/menu_app.py > ~/Library/Logs/olympus_menu_app.log 2>&1
