#!/bin/bash
#
# Olympus Transcriber - LaunchAgent Setup Script
# Installs the transcriber as a macOS LaunchAgent for automatic startup
#

set -e  # Exit on any error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LAUNCHAGENT_DIR="$HOME/Library/LaunchAgents"
PLIST_NAME="com.user.olympus-transcriber.plist"
PLIST_PATH="$LAUNCHAGENT_DIR/$PLIST_NAME"
PYTHON_PATH="$(which python3)"
MAIN_SCRIPT="$PROJECT_DIR/src/main.py"

echo ""
echo "================================================"
echo "  Olympus Transcriber - LaunchAgent Setup"
echo "================================================"
echo ""

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 not found${NC}"
    echo "Please install Python 3 and try again"
    exit 1
fi

echo -e "${GREEN}✓${NC} Python 3 found: $PYTHON_PATH"

# Check if main script exists
if [ ! -f "$MAIN_SCRIPT" ]; then
    echo -e "${RED}Error: Main script not found at $MAIN_SCRIPT${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Main script found"

# Create necessary directories
echo ""
echo "Creating directories..."

mkdir -p "$HOME/Documents/Transcriptions"
echo -e "${GREEN}✓${NC} Created: ~/Documents/Transcriptions"

mkdir -p "$HOME/Library/Logs"
echo -e "${GREEN}✓${NC} Created: ~/Library/Logs"

mkdir -p "$LAUNCHAGENT_DIR"
echo -e "${GREEN}✓${NC} Created: $LAUNCHAGENT_DIR"

# Check for whisper.cpp installation
WHISPER_CPP_PATH="$HOME/whisper.cpp/main"
if [ ! -f "$WHISPER_CPP_PATH" ]; then
    echo ""
    echo -e "${YELLOW}Warning: whisper.cpp not found at $WHISPER_CPP_PATH${NC}"
    echo "Please install it with:"
    echo "  bash $PROJECT_DIR/scripts/install_whisper_cpp.sh"
    echo ""
    read -p "Install whisper.cpp now? (Y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        bash "$PROJECT_DIR/scripts/install_whisper_cpp.sh"
        if [ ! -f "$WHISPER_CPP_PATH" ]; then
            echo -e "${RED}Error: whisper.cpp installation failed${NC}"
            exit 1
        fi
    else
        echo -e "${YELLOW}Warning: Continuing without whisper.cpp${NC}"
        echo "Transcription will not work until whisper.cpp is installed"
    fi
else
    echo -e "${GREEN}✓${NC} whisper.cpp found"
fi

# Check if virtual environment exists
VENV_PATH="$PROJECT_DIR/venv"
if [ ! -d "$VENV_PATH" ]; then
    echo ""
    echo -e "${YELLOW}Warning: Virtual environment not found${NC}"
    echo "Please create it with:"
    echo "  cd $PROJECT_DIR"
    echo "  python3 -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
    PYTHON_EXEC="$PYTHON_PATH"
else
    PYTHON_EXEC="$VENV_PATH/bin/python"
    echo -e "${GREEN}✓${NC} Virtual environment found"
fi

# Unload existing agent if running
if launchctl list | grep -q "$PLIST_NAME"; then
    echo ""
    echo "Unloading existing LaunchAgent..."
    launchctl unload "$PLIST_PATH" 2>/dev/null || true
    echo -e "${GREEN}✓${NC} Existing agent unloaded"
fi

# Generate plist file
echo ""
echo "Generating LaunchAgent plist..."

cat > "$PLIST_PATH" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.olympus-transcriber</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>$PYTHON_EXEC</string>
        <string>$MAIN_SCRIPT</string>
    </array>
    
    <key>RunAtLoad</key>
    <true/>
    
    <key>KeepAlive</key>
    <true/>
    
    <key>StandardOutPath</key>
    <string>/tmp/olympus-transcriber-out.log</string>
    
    <key>StandardErrorPath</key>
    <string>/tmp/olympus-transcriber-err.log</string>
    
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$HOME/whisper.cpp</string>
    </dict>
</dict>
</plist>
EOF

echo -e "${GREEN}✓${NC} Created: $PLIST_PATH"

# Load LaunchAgent
echo ""
echo "Loading LaunchAgent..."
launchctl load "$PLIST_PATH"

# Wait a moment for it to start
sleep 2

# Check if it's running
if launchctl list | grep -q "olympus-transcriber"; then
    echo -e "${GREEN}✓${NC} LaunchAgent loaded and running"
else
    echo -e "${RED}Error: LaunchAgent failed to load${NC}"
    echo "Check logs at:"
    echo "  /tmp/olympus-transcriber-err.log"
    exit 1
fi

# Display status
echo ""
echo "================================================"
echo -e "${GREEN}✓ Installation Complete!${NC}"
echo "================================================"
echo ""
echo "The Olympus Transcriber is now running as a daemon."
echo ""
echo "Key locations:"
echo "  • Transcriptions: ~/Documents/Transcriptions/"
echo "  • State file: ~/.olympus_transcriber_state.json"
echo "  • Application log: ~/Library/Logs/olympus_transcriber.log"
echo "  • System stdout: /tmp/olympus-transcriber-out.log"
echo "  • System stderr: /tmp/olympus-transcriber-err.log"
echo ""
echo "Useful commands:"
echo "  • Check status:  launchctl list | grep olympus-transcriber"
echo "  • View logs:     tail -f ~/Library/Logs/olympus_transcriber.log"
echo "  • Unload:        launchctl unload $PLIST_PATH"
echo "  • Reload:        launchctl load $PLIST_PATH"
echo ""
echo "Connect your Olympus LS-P1 recorder to start automatic transcription!"
echo ""


