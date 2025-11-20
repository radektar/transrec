#!/bin/bash
#
# Whisper.cpp Installation Script
# Installs whisper.cpp with Core ML support for Apple Silicon
#

set -e  # Exit on any error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
WHISPER_DIR="$HOME/whisper.cpp"
MODEL_SIZE="small"

echo ""
echo "========================================================"
echo "  Whisper.cpp Installation with Core ML Support"
echo "========================================================"
echo ""

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo -e "${RED}Error: This script is designed for macOS${NC}"
    exit 1
fi

# Check if already installed
if [ -d "$WHISPER_DIR" ] && [ -f "$WHISPER_DIR/main" ]; then
    echo -e "${YELLOW}Whisper.cpp is already installed at $WHISPER_DIR${NC}"
    read -p "Reinstall? This will rebuild from scratch (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Cleaning existing installation..."
        cd "$WHISPER_DIR"
        make clean 2>/dev/null || true
    else
        echo "Using existing installation."
        exit 0
    fi
else
    # Clone whisper.cpp repository
    echo ""
    echo -e "${BLUE}Step 1/5: Cloning whisper.cpp repository...${NC}"
    if [ -d "$WHISPER_DIR" ]; then
        echo "Directory exists, updating..."
        cd "$WHISPER_DIR"
        git pull
    else
        git clone https://github.com/ggerganov/whisper.cpp "$WHISPER_DIR"
        cd "$WHISPER_DIR"
    fi
    echo -e "${GREEN}✓${NC} Repository ready"
fi

# Check for required tools
echo ""
echo -e "${BLUE}Step 2/5: Checking dependencies...${NC}"

if ! command -v git &> /dev/null; then
    echo -e "${RED}Error: git not found${NC}"
    echo "Please install Xcode Command Line Tools: xcode-select --install"
    exit 1
fi
echo -e "${GREEN}✓${NC} git found"

if ! command -v make &> /dev/null; then
    echo -e "${RED}Error: make not found${NC}"
    echo "Please install Xcode Command Line Tools: xcode-select --install"
    exit 1
fi
echo -e "${GREEN}✓${NC} make found"

# Check for cmake
if ! command -v cmake &> /dev/null; then
    echo -e "${YELLOW}Warning: cmake not found${NC}"
    echo "cmake is required for compiling whisper.cpp."
    read -p "Install cmake via Homebrew? (Y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        if command -v brew &> /dev/null; then
            echo "Installing cmake..."
            brew install cmake
            echo -e "${GREEN}✓${NC} cmake installed"
        else
            echo -e "${RED}Error: Homebrew not found${NC}"
            echo "Please install Homebrew from https://brew.sh or install cmake manually:"
            echo "  brew install cmake"
            exit 1
        fi
    else
        echo -e "${RED}Error: cmake is required${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓${NC} cmake found"
fi

# Check for ffmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo -e "${YELLOW}Warning: ffmpeg not found${NC}"
    echo "ffmpeg is required for audio processing."
    read -p "Install ffmpeg via Homebrew? (Y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        if command -v brew &> /dev/null; then
            brew install ffmpeg
            echo -e "${GREEN}✓${NC} ffmpeg installed"
        else
            echo -e "${RED}Error: Homebrew not found${NC}"
            echo "Please install Homebrew from https://brew.sh or install ffmpeg manually"
            exit 1
        fi
    fi
else
    echo -e "${GREEN}✓${NC} ffmpeg found"
fi

# Detect macOS SDK (required for clang standard headers)
SDK_PATH=""
if command -v xcrun &> /dev/null; then
    SDK_PATH=$(xcrun --sdk macosx --show-sdk-path 2>/dev/null || true)
fi

if [ -n "$SDK_PATH" ]; then
    echo -e "${GREEN}✓${NC} macOS SDK found at: $SDK_PATH"
    export SDKROOT="$SDK_PATH"
    
    # Ensure standard headers are discoverable
    CLT_CXX_HEADERS="/Library/Developer/CommandLineTools/usr/include/c++/v1"
    if [ -d "$CLT_CXX_HEADERS" ]; then
        export CPLUS_INCLUDE_PATH="$CLT_CXX_HEADERS:${CPLUS_INCLUDE_PATH:-}"
    fi
    CLT_C_HEADERS="/Library/Developer/CommandLineTools/usr/include"
    if [ -d "$CLT_C_HEADERS" ]; then
        export C_INCLUDE_PATH="$CLT_C_HEADERS:${C_INCLUDE_PATH:-}"
    fi
else
    echo -e "${YELLOW}Warning: Unable to detect macOS SDK path${NC}"
    echo "Some systems require running: xcode-select --install"
fi

# Download model
echo ""
echo -e "${BLUE}Step 3/5: Downloading $MODEL_SIZE model...${NC}"
cd "$WHISPER_DIR"
if [ -f "models/ggml-$MODEL_SIZE.bin" ]; then
    echo "Model already downloaded"
else
    bash models/download-ggml-model.sh "$MODEL_SIZE"
fi
echo -e "${GREEN}✓${NC} Model downloaded: models/ggml-$MODEL_SIZE.bin"

# Check if on Apple Silicon
IS_APPLE_SILICON=false
if [[ $(uname -m) == "arm64" ]]; then
    IS_APPLE_SILICON=true
    echo ""
    echo -e "${GREEN}✓${NC} Apple Silicon detected - Core ML support will be enabled"
fi

# Compile with Core ML support
echo ""
echo -e "${BLUE}Step 4/5: Compiling whisper.cpp...${NC}"
cd "$WHISPER_DIR"

# Common CMake arguments
CMAKE_ARGS=("-B" "build")
if [ -n "$SDK_PATH" ]; then
    CMAKE_ARGS+=("-DCMAKE_OSX_SYSROOT=$SDK_PATH")
fi
if [ "$IS_APPLE_SILICON" = true ]; then
    CMAKE_ARGS+=("-DCMAKE_OSX_ARCHITECTURES=arm64")
fi

# Check if Makefile exists (simpler build method)
USE_CMAKE=true
if [ -f "Makefile" ] && [ "$IS_APPLE_SILICON" = true ]; then
    echo "Found Makefile - trying simple build method first..."
    make clean 2>/dev/null || true
    
    # Try building with Core ML using make
    if WHISPER_COREML=1 make -j 2>/dev/null; then
        if [ -f "$WHISPER_DIR/main" ]; then
            EXECUTABLE_PATH="$WHISPER_DIR/main"
            USE_CMAKE=false
            echo -e "${GREEN}✓${NC} Built successfully with Makefile"
        fi
    fi
fi

# If Makefile build failed or not available, use cmake
if [ "$USE_CMAKE" = true ]; then
    echo "Using cmake build method..."
    
    if [ "$IS_APPLE_SILICON" = true ]; then
        echo "Building with Core ML support..."
        # Clean any previous build
        rm -rf build 2>/dev/null || true
        
        # Configure with cmake for Core ML
        if ! cmake "${CMAKE_ARGS[@]}" -DWHISPER_COREML=ON; then
            echo -e "${YELLOW}Core ML cmake configuration failed, trying standard build...${NC}"
            rm -rf build
            cmake "${CMAKE_ARGS[@]}"
        fi
        
        # Build
        if ! cmake --build build -j; then
            echo -e "${YELLOW}Core ML build failed, trying standard build...${NC}"
            rm -rf build
            cmake "${CMAKE_ARGS[@]}"
            cmake --build build -j
        fi
        
        # Check for executable (whisper.cpp uses different output names)
        if [ -f "$WHISPER_DIR/build/bin/whisper-cli" ]; then
            EXECUTABLE_PATH="$WHISPER_DIR/build/bin/whisper-cli"
        elif [ -f "$WHISPER_DIR/build/bin/main" ]; then
            EXECUTABLE_PATH="$WHISPER_DIR/build/bin/main"
        elif [ -f "$WHISPER_DIR/main" ]; then
            EXECUTABLE_PATH="$WHISPER_DIR/main"
        else
            echo -e "${RED}Error: Compilation failed - executable not found${NC}"
            echo "Checked: build/bin/whisper-cli, build/bin/main, main"
            exit 1
        fi
    else
        echo "Building for Intel Mac (no Core ML)..."
        rm -rf build 2>/dev/null || true
        cmake "${CMAKE_ARGS[@]}"
        cmake --build build -j
        
        if [ -f "$WHISPER_DIR/build/bin/whisper-cli" ]; then
            EXECUTABLE_PATH="$WHISPER_DIR/build/bin/whisper-cli"
        elif [ -f "$WHISPER_DIR/build/bin/main" ]; then
            EXECUTABLE_PATH="$WHISPER_DIR/build/bin/main"
        elif [ -f "$WHISPER_DIR/main" ]; then
            EXECUTABLE_PATH="$WHISPER_DIR/main"
        else
            echo -e "${RED}Error: Compilation failed - executable not found${NC}"
            exit 1
        fi
    fi
fi

echo -e "${GREEN}✓${NC} Compilation successful"
echo "Executable: $EXECUTABLE_PATH"

# Generate Core ML model if on Apple Silicon
if [ "$IS_APPLE_SILICON" = true ]; then
    echo ""
    echo -e "${BLUE}Step 5/5: Generating Core ML model...${NC}"
    
    # Check if Core ML model script exists
    if [ -f "models/generate-coreml-model.sh" ]; then
        # Check for Python dependencies
        if command -v python3 &> /dev/null; then
            echo "Checking Python dependencies..."
            
            # Try to generate Core ML model
            cd "$WHISPER_DIR/models"
            if bash generate-coreml-model.sh "$MODEL_SIZE" 2>/dev/null; then
                echo -e "${GREEN}✓${NC} Core ML model generated"
            else
                echo -e "${YELLOW}Warning: Core ML model generation failed${NC}"
                echo "This is optional - whisper.cpp will still work with the regular model"
                echo "To enable Core ML later, install: pip install ane_transformers coremltools"
            fi
        else
            echo -e "${YELLOW}Warning: Python3 not found${NC}"
            echo "Core ML model generation skipped (optional)"
        fi
    else
        echo -e "${YELLOW}Note: Core ML model generation script not found${NC}"
        echo "Your whisper.cpp version may not support Core ML model generation"
    fi
else
    echo ""
    echo -e "${BLUE}Step 5/5: Skipping Core ML (Intel Mac)${NC}"
fi

# Test installation
echo ""
echo "========================================================"
echo -e "${GREEN}Installation Complete!${NC}"
echo "========================================================"
echo ""
echo "Whisper.cpp installed at: $WHISPER_DIR"
echo "Binary: $WHISPER_DIR/main"
echo "Model: $WHISPER_DIR/models/ggml-$MODEL_SIZE.bin"
echo ""

# Quick test
echo "Testing installation..."
if [ -f "$EXECUTABLE_PATH" ]; then
    if "$EXECUTABLE_PATH" -h &> /dev/null || "$EXECUTABLE_PATH" --help &> /dev/null; then
        echo -e "${GREEN}✓${NC} whisper.cpp is working"
    else
        echo -e "${YELLOW}Warning: Could not test whisper.cpp help${NC}"
        echo "But executable exists at: $EXECUTABLE_PATH"
    fi
else
    echo -e "${RED}Error: Executable not found at $EXECUTABLE_PATH${NC}"
    exit 1
fi

echo ""
echo "You can now use whisper.cpp for transcription!"
echo ""

