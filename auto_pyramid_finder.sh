#!/bin/bash

# Terraria Pyramid World Finder
# Generates worlds and detects those containing Sandstone Brick (pyramids)
# Usage: ./auto_pyramid_finder.sh [SIZE] [DIFFICULTY] [EVIL] [COUNT] [DELETE_NO_PYRAMID]
# SIZE: 1=Small, 2=Medium, 3=Large (default: 2)
# DIFFICULTY: 1=Normal, 2=Expert, 3=Master (default: 1)
# EVIL: 1=Random, 2=Corruption, 3=Crimson (default: 1)
# COUNT: Number of worlds to generate, max 200 (default: 1)
# DELETE_NO_PYRAMID: 0=Keep all, 1=Delete worlds without pyramids (default: 0)

# Auto-detect TerrariaServer path or use custom path
# You can set custom path via environment variable: export TERRARIA_SERVER_PATH="/your/custom/path"
if [ -n "$TERRARIA_SERVER_PATH" ]; then
    TERRARIA_SERVER="$TERRARIA_SERVER_PATH"
else
    # Common paths for different systems
    if [ "$(uname)" == "Darwin" ]; then
        # macOS - try common Steam locations
        POSSIBLE_PATHS=(
            "$HOME/Library/Application Support/Steam/steamapps/common/Terraria/Terraria.app/Contents/MacOS/TerrariaServer"
            "/Applications/Terraria.app/Contents/MacOS/TerrariaServer"
        )
    elif [ "$(uname)" == "Linux" ]; then
        # Linux - try common Steam locations
        POSSIBLE_PATHS=(
            "$HOME/.local/share/Steam/steamapps/common/Terraria/TerrariaServer.bin.x86_64"
            "$HOME/.steam/steam/steamapps/common/Terraria/TerrariaServer.bin.x86_64"
        )
    else
        # Windows (Git Bash / WSL)
        POSSIBLE_PATHS=(
            "/c/Program Files (x86)/Steam/steamapps/common/Terraria/TerrariaServer.exe"
            "$HOME/.local/share/Steam/steamapps/common/Terraria/TerrariaServer.exe"
        )
    fi

    # Try to find TerrariaServer in common locations
    TERRARIA_SERVER=""
    for path in "${POSSIBLE_PATHS[@]}"; do
        if [ -f "$path" ]; then
            TERRARIA_SERVER="$path"
            break
        fi
    done

    # If still not found, prompt user
    if [ -z "$TERRARIA_SERVER" ] || [ ! -f "$TERRARIA_SERVER" ]; then
        echo "Error: Could not auto-detect TerrariaServer location."
        echo ""
        echo "Please specify the path using one of these methods:"
        echo "1. Set environment variable: export TERRARIA_SERVER_PATH=\"/path/to/TerrariaServer\""
        echo "2. Edit this script and set TERRARIA_SERVER variable manually"
        echo ""
        echo "Common locations:"
        echo "  macOS: ~/Library/Application Support/Steam/steamapps/common/Terraria/Terraria.app/Contents/MacOS/TerrariaServer"
        echo "  Linux: ~/.local/share/Steam/steamapps/common/Terraria/TerrariaServer.bin.x86_64"
        echo "  Windows: C:/Program Files (x86)/Steam/steamapps/common/Terraria/TerrariaServer.exe"
        exit 1
    fi
fi

# Auto-detect world save directory
if [ -n "$TERRARIA_WORLD_DIR" ]; then
    WORLD_DIR="$TERRARIA_WORLD_DIR"
else
    # Common paths for different systems
    if [ "$(uname)" == "Darwin" ]; then
        # macOS
        WORLD_DIR="$HOME/Library/Application Support/Terraria/Worlds"
    elif [ "$(uname)" == "Linux" ]; then
        # Linux
        WORLD_DIR="$HOME/.local/share/Terraria/Worlds"
    else
        # Windows (Git Bash / WSL)
        WORLD_DIR="$HOME/Documents/My Games/Terraria/Worlds"
    fi
fi

# Python checker script (use lihzahrd library - most reliable)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_CHECKER="$SCRIPT_DIR/lihzahrd_parser.py"

# Parse arguments with defaults
SIZE=${1:-2}
DIFFICULTY=${2:-1}
EVIL=${3:-1}
COUNT=${4:-1}
DELETE_NO_PYRAMID=${5:-0}

# Parameter validation
if ! [[ "$SIZE" =~ ^[1-3]$ ]]; then
    echo "Error: SIZE must be 1, 2, or 3"
    echo "1=Small, 2=Medium, 3=Large"
    exit 1
fi

if ! [[ "$DIFFICULTY" =~ ^[1-3]$ ]]; then
    echo "Error: DIFFICULTY must be 1, 2, or 3"
    echo "1=Normal, 2=Expert, 3=Master"
    exit 1
fi

if ! [[ "$EVIL" =~ ^[1-3]$ ]]; then
    echo "Error: EVIL must be 1, 2, or 3"
    echo "1=Random, 2=Corruption, 3=Crimson"
    exit 1
fi

if ! [[ "$COUNT" =~ ^[0-9]+$ ]] || [ "$COUNT" -lt 1 ] || [ "$COUNT" -gt 200 ]; then
    echo "Error: COUNT must be an integer between 1 and 200"
    exit 1
fi

if ! [[ "$DELETE_NO_PYRAMID" =~ ^[0-1]$ ]]; then
    echo "Error: DELETE_NO_PYRAMID must be 0 or 1"
    echo "0=Keep all worlds, 1=Delete worlds without pyramids"
    exit 1
fi

# Check if TerrariaServer exists
if [ ! -f "$TERRARIA_SERVER" ]; then
    echo "Error: TerrariaServer not found at: $TERRARIA_SERVER"
    exit 1
fi

# Check if Python checker exists
if [ ! -f "$PYTHON_CHECKER" ]; then
    echo "Error: Python checker not found at: $PYTHON_CHECKER"
    exit 1
fi

# Ensure world directory exists
mkdir -p "$WORLD_DIR"

# Parameter name mappings
SIZE_NAME=("" "Small" "Medium" "Large")
DIFFICULTY_NAME=("" "Normal" "Expert" "Master")
EVIL_NAME=("" "Random" "Corruption" "Crimson")

DELETE_MODE_TEXT="Keep all"
if [ "$DELETE_NO_PYRAMID" -eq 1 ]; then
    DELETE_MODE_TEXT="Delete worlds without pyramids"
fi

echo "========================================="
echo "Terraria Pyramid World Finder"
echo "========================================="
echo "World Size: ${SIZE_NAME[$SIZE]}"
echo "Difficulty: ${DIFFICULTY_NAME[$DIFFICULTY]}"
echo "Evil Type: ${EVIL_NAME[$EVIL]}"
echo "Count: $COUNT"
echo "Delete Mode: $DELETE_MODE_TEXT"
echo "========================================="
echo ""

# Statistics
TOTAL_GENERATED=0
PYRAMIDS_FOUND=0

# Arrays to track pyramid worlds
PYRAMID_WORLDS=()
PYRAMID_COORDS=()

# Generate worlds
for i in $(seq 1 $COUNT)
do
    echo "[$i/$COUNT] Generating world..."

    # Generate unique world name (timestamp + sequence)
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    WORLD_NAME="World_${TIMESTAMP}_${i}"
    WORLD_PATH="$WORLD_DIR/${WORLD_NAME}.wld"

    # Record file count before generation
    BEFORE_FILES=$(ls -1 "$WORLD_DIR"/*.wld 2>/dev/null | wc -l | tr -d ' ')

    # Create input file for automation
    INPUT_FILE=$(mktemp)
    echo "n" > "$INPUT_FILE"  # Create new world
    echo "$SIZE" >> "$INPUT_FILE"  # World size
    echo "$DIFFICULTY" >> "$INPUT_FILE"  # Difficulty
    echo "$EVIL" >> "$INPUT_FILE"  # Evil type
    echo "$WORLD_NAME" >> "$INPUT_FILE"  # World name
    echo "" >> "$INPUT_FILE"  # Seed (blank for random)
    echo "exit" >> "$INPUT_FILE"  # Exit

    # Run TerrariaServer to generate world in background
    "$TERRARIA_SERVER" < "$INPUT_FILE" > /dev/null 2>&1 &
    SERVER_PID=$!

    # Clean up temp file
    rm -f "$INPUT_FILE"

    # Wait for world file to be created (max 300 seconds = 5 minutes)
    WAIT_TIME=0
    MAX_WAIT=300
    WORLD_CREATED=false

    while [ $WAIT_TIME -lt $MAX_WAIT ]; do
        sleep 2
        WAIT_TIME=$((WAIT_TIME + 2))

        # Check if a new world file appeared
        AFTER_FILES=$(ls -1 "$WORLD_DIR"/*.wld 2>/dev/null | wc -l | tr -d ' ')
        if [ "$AFTER_FILES" -gt "$BEFORE_FILES" ]; then
            WORLD_CREATED=true
            break
        fi
    done

    # Kill the server process (but NOT the game client)
    # First try graceful termination
    kill $SERVER_PID 2>/dev/null
    sleep 1

    # Force kill if still running
    kill -9 $SERVER_PID 2>/dev/null

    # Only kill TerrariaServer processes, not Terraria game client
    pkill -9 -f "TerrariaServer" 2>/dev/null

    wait $SERVER_PID 2>/dev/null

    # Additional wait for filesystem sync
    sleep 1

    # Find the actual generated world file
    ACTUAL_WORLD_PATH=""

    if [ -f "$WORLD_PATH" ]; then
        ACTUAL_WORLD_PATH="$WORLD_PATH"
    else
        # Try to find the most recently created .wld file
        LATEST_WORLD=$(ls -t "$WORLD_DIR"/*.wld 2>/dev/null | head -1)
        AFTER_FILES=$(ls -1 "$WORLD_DIR"/*.wld 2>/dev/null | wc -l | tr -d ' ')

        if [ "$AFTER_FILES" -gt "$BEFORE_FILES" ] && [ -n "$LATEST_WORLD" ]; then
            ACTUAL_WORLD_PATH="$LATEST_WORLD"
        fi
    fi

    # Check if world file was successfully generated
    if [ -z "$ACTUAL_WORLD_PATH" ] || [ ! -f "$ACTUAL_WORLD_PATH" ]; then
        echo "✗ Error: Generated world file not found"
        echo "Generation failed, stopping execution"
        exit 1
    fi

    FILE_SIZE=$(stat -f%z "$ACTUAL_WORLD_PATH" 2>/dev/null || echo "0")
    if [ "$FILE_SIZE" -eq 0 ]; then
        echo "✗ Error: World file created but size is 0"
        echo "Generation failed, stopping execution"
        exit 1
    fi

    TOTAL_GENERATED=$((TOTAL_GENERATED + 1))
    echo "✓ Generated: $(basename "$ACTUAL_WORLD_PATH") ($(numfmt --to=iec-i --suffix=B $FILE_SIZE 2>/dev/null || echo "${FILE_SIZE} bytes"))"

    # Check for Sandstone Brick (pyramids) using Python
    echo "  Checking for pyramids..."

    # Run Python checker and capture output
    PYTHON_OUTPUT=$(python3 "$PYTHON_CHECKER" "$ACTUAL_WORLD_PATH" 2>&1)

    # Check if Sandstone Brick was found (look for "Found" in output, not "No Sandstone")
    if echo "$PYTHON_OUTPUT" | grep -q "Found [0-9]* Sandstone Brick"; then
        PYRAMIDS_FOUND=$((PYRAMIDS_FOUND + 1))

        # Extract coordinates for display
        HIGHEST_POINT=$(echo "$PYTHON_OUTPUT" | grep "Highest point coordinates" | sed 's/.*Highest point coordinates: //')

        echo "  🎉 PYRAMID FOUND! $HIGHEST_POINT"

        # Store pyramid world info
        PYRAMID_WORLDS+=("$(basename "$ACTUAL_WORLD_PATH")")
        PYRAMID_COORDS+=("$HIGHEST_POINT")
    else
        echo "  ○ No pyramid found in this world"

        # Delete world if delete mode is enabled
        if [ "$DELETE_NO_PYRAMID" -eq 1 ]; then
            rm -f "$ACTUAL_WORLD_PATH"
            echo "  ✗ Deleted (no pyramid)"
        fi
    fi

    echo ""
done

echo "========================================="
echo "Batch generation complete!"
echo "Total worlds generated: $TOTAL_GENERATED"
echo "Pyramids found: $PYRAMIDS_FOUND"
if [ $TOTAL_GENERATED -gt 0 ]; then
    PERCENTAGE=$((PYRAMIDS_FOUND * 100 / TOTAL_GENERATED))
    echo "Success rate: ${PERCENTAGE}%"
fi
echo ""

if [ ${#PYRAMID_WORLDS[@]} -gt 0 ]; then
    echo "Worlds with pyramids:"
    for i in "${!PYRAMID_WORLDS[@]}"; do
        echo "  - ${PYRAMID_WORLDS[$i]} (${PYRAMID_COORDS[$i]})"
    done
else
    echo "No pyramids found in any world."
fi
echo ""
echo "World directory: $WORLD_DIR"
echo "========================================="
