#!/bin/bash
# Create Linux desktop entry for Pyramid Toolkit

INSTALL_DIR="$(pwd)/dist/PyramidDetector"
DESKTOP_FILE="$HOME/.local/share/applications/pyramid-toolkit.desktop"

echo "Creating desktop entry..."

mkdir -p "$HOME/.local/share/applications"

cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Pyramid Toolkit
Comment=Terraria Pyramid Toolkit
Exec=$INSTALL_DIR/PyramidDetector
Icon=$INSTALL_DIR/icon.png
Terminal=false
Categories=Game;Utility;
EOF

chmod +x "$DESKTOP_FILE"

echo "Desktop entry created at: $DESKTOP_FILE"
echo "The application should now appear in your applications menu"
echo ""
echo "Note: If you move the dist/PyramidDetector folder, you'll need to run this script again"
