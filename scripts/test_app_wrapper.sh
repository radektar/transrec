#!/bin/bash
# Test script for Transrec.app wrapper
# Verifies that the app can access files on external recorder

echo "=== Testing Transrec.app ==="
echo ""

# Check if app exists
APP_PATH="$HOME/Applications/Transrec.app"
if [ ! -d "$APP_PATH" ]; then
    echo "❌ ERROR: App not found at $APP_PATH"
    exit 1
fi
echo "✓ App found: $APP_PATH"

# Check if app is in Login Items
LOGIN_ITEMS=$(osascript -e 'tell application "System Events" to get the name of every login item' 2>/dev/null)
if echo "$LOGIN_ITEMS" | grep -qi "Transrec"; then
    echo "✓ App is in Login Items"
else
    echo "⚠️  WARNING: App is NOT in Login Items"
fi

# Check if recorder is connected
if [ -d "/Volumes/LS-P1" ]; then
    echo "✓ Recorder connected: /Volumes/LS-P1"
    FILE_COUNT=$(ls -1 /Volumes/LS-P1/RECORDER/FOLDER_A/*.MP3 2>/dev/null | wc -l | tr -d ' ')
    echo "  Found $FILE_COUNT MP3 files"
else
    echo "⚠️  WARNING: Recorder not connected"
fi

# Check if app process is running
if pgrep -f "Transrec\|python.*src.main" > /dev/null; then
    echo "✓ App process is running"
    ps aux | grep -E "Transrec|python.*src.main" | grep -v grep | head -1
else
    echo "⚠️  WARNING: App process not running"
    echo "  Start with: open $APP_PATH"
fi

# Check recent logs
echo ""
echo "=== Recent log entries ==="
tail -10 ~/Library/Logs/olympus_transcriber.log 2>/dev/null || echo "No log file found"

echo ""
echo "=== Full Disk Access Check ==="
echo "⚠️  IMPORTANT: Make sure Transrec.app is added to Full Disk Access:"
echo "   System Settings → Privacy & Security → Full Disk Access"
echo "   If not added, the app cannot read files from /Volumes/LS-P1"
echo ""
echo "To verify access, check logs for:"
echo "  - 'Found X new audio file(s)' where X > 0"
echo "  - If X = 0 but files exist, Full Disk Access may not be configured"

