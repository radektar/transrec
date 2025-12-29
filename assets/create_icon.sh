#!/bin/bash
# Create a simple icon using macOS tools

# Create a simple PNG with text using sips (we'll use a simple approach)
# For now, we'll create a placeholder icon using iconutil

# Create icon.iconset directory structure
ICONSET="icon.iconset"

# Create a simple 1024x1024 PNG using sips from a solid color
# We'll create a simple blue square as placeholder
sips -z 1024 1024 --setProperty format png /System/Library/CoreServices/CoreTypes.bundle/Contents/Resources/GenericApplicationIcon.icns --out "${ICONSET}/icon_512x512@2x.png" 2>/dev/null || \
sips -z 1024 1024 --setProperty format png /System/Library/CoreServices/CoreTypes.bundle/Contents/Resources/GenericDocumentIcon.icns --out "${ICONSET}/icon_512x512@2x.png" 2>/dev/null || \
echo "Creating placeholder icon..."

# Create all required sizes from the 1024x1024 version
if [ -f "${ICONSET}/icon_512x512@2x.png" ]; then
    sips -z 512 512 "${ICONSET}/icon_512x512@2x.png" --out "${ICONSET}/icon_512x512.png"
    sips -z 256 256 "${ICONSET}/icon_512x512@2x.png" --out "${ICONSET}/icon_256x256.png"
    sips -z 256 256 "${ICONSET}/icon_512x512@2x.png" --out "${ICONSET}/icon_256x256@2x.png"
    sips -z 128 128 "${ICONSET}/icon_512x512@2x.png" --out "${ICONSET}/icon_128x128.png"
    sips -z 128 128 "${ICONSET}/icon_512x512@2x.png" --out "${ICONSET}/icon_128x128@2x.png"
    sips -z 64 64 "${ICONSET}/icon_512x512@2x.png" --out "${ICONSET}/icon_32x32@2x.png"
    sips -z 32 32 "${ICONSET}/icon_512x512@2x.png" --out "${ICONSET}/icon_32x32.png"
    sips -z 32 32 "${ICONSET}/icon_512x512@2x.png" --out "${ICONSET}/icon_16x16@2x.png"
    sips -z 16 16 "${ICONSET}/icon_512x512@2x.png" --out "${ICONSET}/icon_16x16.png"
    
    # Convert to .icns
    iconutil -c icns "${ICONSET}" -o icon.icns
    echo "Created icon.icns"
else
    echo "Could not create icon from system resources, creating minimal placeholder..."
    # Create minimal placeholder using Python (if available)
    python3 << 'PYEOF'
from pathlib import Path
import subprocess

iconset = Path("icon.iconset")
iconset.mkdir(exist_ok=True)

# Create a simple 1024x1024 blue square as placeholder
# Using sips to create a solid color image
subprocess.run([
    "sips", "-z", "1024", "1024",
    "--setProperty", "format", "png",
    "/System/Library/CoreServices/CoreTypes.bundle/Contents/Resources/GenericApplicationIcon.icns",
    "--out", str(iconset / "icon_512x512@2x.png")
], check=False)

# Create all sizes
sizes = [
    ("512x512", "512x512"),
    ("256x256@2x", "512x512"),
    ("256x256", "256x256"),
    ("128x128@2x", "256x256"),
    ("128x128", "128x128"),
    ("32x32@2x", "64x64"),
    ("32x32", "32x32"),
    ("16x16@2x", "32x32"),
    ("16x16", "16x16"),
]

for target, source_size in sizes:
    source = iconset / f"icon_{source_size}.png"
    if not source.exists():
        source = iconset / "icon_512x512@2x.png"
    subprocess.run([
        "sips", "-z", target.split("@")[0].split("x")[1], target.split("@")[0].split("x")[0],
        str(source), "--out", str(iconset / f"icon_{target}.png")
    ], check=False)

# Convert to icns
subprocess.run(["iconutil", "-c", "icns", str(iconset), "-o", "icon.icns"], check=False)
print("Created placeholder icon.icns")
PYEOF
fi
