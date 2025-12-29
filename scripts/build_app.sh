#!/bin/bash
# Build script for Transrec.app using py2app
# This script builds a macOS application bundle ready for distribution

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${PROJECT_ROOT}"

echo "🔨 Building Transrec.app..."
echo "Project root: ${PROJECT_ROOT}"

# Check if we're on macOS
if [[ "$(uname)" != "Darwin" ]]; then
    echo "❌ Error: This script must be run on macOS"
    exit 1
fi

# Check if we're on Apple Silicon
ARCH=$(uname -m)
if [[ "${ARCH}" != "arm64" ]]; then
    echo "⚠️  Warning: Building on ${ARCH}, but bundle will be for arm64 only"
fi

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
else
    echo "⚠️  Warning: venv not found, using system Python"
fi

# Check if py2app is installed
if ! python3 -c "import py2app" 2>/dev/null; then
    echo "📥 Installing py2app..."
    pip install py2app
else
    echo "✅ py2app already installed"
fi

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build dist

# Check if icon exists
if [ ! -f "assets/icon.icns" ]; then
    echo "⚠️  Warning: assets/icon.icns not found, building without icon"
fi

# Build the application
echo "🔨 Running py2app..."
# Note: py2app may segfault during import checking, but bundle is usually complete
# We check for bundle existence after build regardless of exit code
set +e  # Temporarily disable exit on error
python3 setup_app.py py2app
BUILD_EXIT_CODE=$?
set -e  # Re-enable exit on error

# Verify build - bundle should exist even if build ended with segfault
if [ ! -d "dist/Transrec.app" ]; then
    echo "❌ Error: Build failed - Transrec.app not found"
    exit 1
fi

# Warn if build ended with segfault but bundle exists
if [ $BUILD_EXIT_CODE -ne 0 ]; then
    echo "⚠️  Warning: Build ended with exit code $BUILD_EXIT_CODE (may be segfault during import checking)"
    echo "   Bundle exists and will be verified..."
fi

# Check bundle size
BUNDLE_SIZE=$(du -sh dist/Transrec.app | cut -f1)
BUNDLE_SIZE_BYTES=$(du -sk dist/Transrec.app | cut -f1)
BUNDLE_SIZE_MB=$((BUNDLE_SIZE_BYTES / 1024))

echo "✅ Build complete!"
echo "📦 Bundle location: dist/Transrec.app"
echo "📏 Bundle size: ${BUNDLE_SIZE} (${BUNDLE_SIZE_MB} MB)"

# Check if size is reasonable (<20MB without models)
if [ "${BUNDLE_SIZE_MB}" -gt 20 ]; then
    echo "⚠️  Warning: Bundle size (${BUNDLE_SIZE_MB} MB) exceeds 20MB target"
    echo "   Consider optimizing excludes in setup_app.py"
else
    echo "✅ Bundle size is within target (<20MB)"
fi

# Verify bundle structure
echo "🔍 Verifying bundle structure..."
if [ ! -f "dist/Transrec.app/Contents/Info.plist" ]; then
    echo "❌ Error: Info.plist not found"
    exit 1
fi

if [ ! -f "dist/Transrec.app/Contents/MacOS/Transrec" ]; then
    echo "❌ Error: Main executable not found"
    exit 1
fi

# Make executable
chmod +x dist/Transrec.app/Contents/MacOS/Transrec

echo ""
echo "✅ Build verification complete!"
echo ""
echo "To test the app:"
echo "  open dist/Transrec.app"
echo ""
echo "To check bundle info:"
echo "  plutil -p dist/Transrec.app/Contents/Info.plist"

