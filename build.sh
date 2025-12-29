#!/bin/bash
# Build script for Terraria Pyramid Detector GUI (macOS/Linux)

set -e  # Exit on error

echo "==================================="
echo "Pyramid Detector GUI Builder"
echo "==================================="
echo ""

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo "Error: PyInstaller is not installed"
    echo "Installing PyInstaller..."
    pip install pyinstaller
fi

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist *.spec.bak

# Build the application
echo ""
echo "Building GUI application..."
pyinstaller pyramid_detector.spec --clean

# Check build result
if [ $? -eq 0 ]; then
    echo ""
    echo "==================================="
    echo "Build successful!"
    echo "==================================="
    echo ""

    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        echo "macOS app bundle created at: dist/PyramidDetector.app"
        echo ""
        echo "To run the app:"
        echo "  open dist/PyramidDetector.app"
        echo ""
        echo "To install the app:"
        echo "  cp -r dist/PyramidDetector.app /Applications/"
    else
        # Linux
        echo "Executable created at: dist/PyramidDetector/PyramidDetector"
        echo ""
        echo "To run the app:"
        echo "  ./dist/PyramidDetector/PyramidDetector"
        echo ""
        echo "To create a desktop shortcut, create a .desktop file:"
        echo "  See build_desktop_entry.sh for details"
    fi
else
    echo ""
    echo "==================================="
    echo "Build failed!"
    echo "==================================="
    exit 1
fi
