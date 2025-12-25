#!/bin/bash

# Scan existing Terraria worlds for pyramids
# Usage: ./scan_existing_worlds.sh [WORLD_DIR]

# Auto-detect world save directory
if [ -n "$1" ]; then
    WORLD_DIR="$1"
elif [ -n "$TERRARIA_WORLD_DIR" ]; then
    WORLD_DIR="$TERRARIA_WORLD_DIR"
else
    if [ "$(uname)" == "Darwin" ]; then
        WORLD_DIR="$HOME/Library/Application Support/Terraria/Worlds"
    elif [ "$(uname)" == "Linux" ]; then
        WORLD_DIR="$HOME/.local/share/Terraria/Worlds"
    else
        WORLD_DIR="$HOME/Documents/My Games/Terraria/Worlds"
    fi
fi

# Python checker script (use lihzahrd library - most reliable)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_CHECKER="$SCRIPT_DIR/lihzahrd_parser.py"

# Check if directory exists
if [ ! -d "$WORLD_DIR" ]; then
    echo "Error: World directory not found: $WORLD_DIR"
    exit 1
fi

# Check if Python checker exists
if [ ! -f "$PYTHON_CHECKER" ]; then
    echo "Error: Python checker not found at: $PYTHON_CHECKER"
    exit 1
fi

echo "========================================="
echo "Terraria World Pyramid Scanner"
echo "========================================="
echo "Scanning directory: $WORLD_DIR"
echo "========================================="
echo ""

# Find all .wld files
WORLD_FILES=("$WORLD_DIR"/*.wld)

# Check if any world files exist
if [ ! -e "${WORLD_FILES[0]}" ]; then
    echo "No world files found in directory."
    exit 0
fi

# Count files
TOTAL_WORLDS=${#WORLD_FILES[@]}
echo "Found $TOTAL_WORLDS world file(s)"
echo ""

# Statistics
WORLDS_WITH_PYRAMIDS=0
WORLDS_WITHOUT_PYRAMIDS=0
PYRAMID_WORLDS=()
PYRAMID_COORDS=()

# Scan each world
for WORLD_FILE in "${WORLD_FILES[@]}"; do
    WORLD_NAME=$(basename "$WORLD_FILE")
    echo "Checking: $WORLD_NAME"

    # Run Python checker
    PYTHON_OUTPUT=$(python3 "$PYTHON_CHECKER" "$WORLD_FILE" 2>&1)

    # Check if pyramid found
    if echo "$PYTHON_OUTPUT" | grep -q "Found [0-9]* Sandstone Brick"; then
        WORLDS_WITH_PYRAMIDS=$((WORLDS_WITH_PYRAMIDS + 1))

        # Extract coordinates
        HIGHEST_POINT=$(echo "$PYTHON_OUTPUT" | grep "Highest point coordinates" | sed 's/.*Highest point coordinates: //')

        echo "  ✓ PYRAMID FOUND! $HIGHEST_POINT"

        PYRAMID_WORLDS+=("$WORLD_NAME")
        PYRAMID_COORDS+=("$HIGHEST_POINT")
    else
        WORLDS_WITHOUT_PYRAMIDS=$((WORLDS_WITHOUT_PYRAMIDS + 1))
        echo "  ○ No pyramid"
    fi
    echo ""
done

# Summary
echo "========================================="
echo "Scan complete!"
echo "========================================="
echo "Total worlds scanned: $TOTAL_WORLDS"
echo "Worlds with pyramids: $WORLDS_WITH_PYRAMIDS"
echo "Worlds without pyramids: $WORLDS_WITHOUT_PYRAMIDS"

if [ $TOTAL_WORLDS -gt 0 ]; then
    PERCENTAGE=$((WORLDS_WITH_PYRAMIDS * 100 / TOTAL_WORLDS))
    echo "Pyramid rate: ${PERCENTAGE}%"
fi

echo ""

if [ ${#PYRAMID_WORLDS[@]} -gt 0 ]; then
    echo "Worlds with pyramids:"
    for i in "${!PYRAMID_WORLDS[@]}"; do
        echo "  $((i+1)). ${PYRAMID_WORLDS[$i]}"
        echo "      Coordinates: ${PYRAMID_COORDS[$i]}"
    done
else
    echo "No pyramids found in any world."
fi

echo ""
echo "========================================="
