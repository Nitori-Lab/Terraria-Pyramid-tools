#!/bin/bash

# Terraria Pyramid World Generator - Target Mode
# Generates worlds until finding a specified number with pyramids
# Usage: ./find_pyramid_worlds.sh [SIZE] [DIFFICULTY] [EVIL] [PYRAMID_TARGET] [MAX_ATTEMPTS]
# SIZE: 1=Small, 2=Medium, 3=Large (default: 2)
# DIFFICULTY: 1=Normal, 2=Expert, 3=Master (default: 1)
# EVIL: 1=Random, 2=Corruption, 3=Crimson (default: 1)
# PYRAMID_TARGET: Number of pyramid worlds to find (default: 1, max: 50)
# MAX_ATTEMPTS: Maximum worlds to generate (default: 100, max: 500)

# Auto-detect TerrariaServer path or use custom path
if [ -n "$TERRARIA_SERVER_PATH" ]; then
    TERRARIA_SERVER="$TERRARIA_SERVER_PATH"
else
    # Common paths for different systems
    if [ "$(uname)" == "Darwin" ]; then
        POSSIBLE_PATHS=(
            "$HOME/Library/Application Support/Steam/steamapps/common/Terraria/Terraria.app/Contents/MacOS/TerrariaServer"
            "/Applications/Terraria.app/Contents/MacOS/TerrariaServer"
        )
    elif [ "$(uname)" == "Linux" ]; then
        POSSIBLE_PATHS=(
            "$HOME/.local/share/Steam/steamapps/common/Terraria/TerrariaServer.bin.x86_64"
            "$HOME/.steam/steam/steamapps/common/Terraria/TerrariaServer.bin.x86_64"
        )
    else
        POSSIBLE_PATHS=(
            "/c/Program Files (x86)/Steam/steamapps/common/Terraria/TerrariaServer.exe"
            "$HOME/.local/share/Steam/steamapps/common/Terraria/TerrariaServer.exe"
        )
    fi

    TERRARIA_SERVER=""
    for path in "${POSSIBLE_PATHS[@]}"; do
        if [ -f "$path" ]; then
            TERRARIA_SERVER="$path"
            break
        fi
    done

    if [ -z "$TERRARIA_SERVER" ] || [ ! -f "$TERRARIA_SERVER" ]; then
        echo "Error: Could not auto-detect TerrariaServer location."
        echo ""
        echo "Please specify the path using environment variable:"
        echo "export TERRARIA_SERVER_PATH=\"/path/to/TerrariaServer\""
        exit 1
    fi
fi

# Auto-detect world save directory
if [ -n "$TERRARIA_WORLD_DIR" ]; then
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

# Parse arguments with defaults
SIZE=${1:-2}
DIFFICULTY=${2:-1}
EVIL=${3:-1}
PYRAMID_TARGET=${4:-1}
MAX_ATTEMPTS=${5:-100}

# Parameter validation
if ! [[ "$SIZE" =~ ^[1-3]$ ]]; then
    echo "Error: SIZE must be 1, 2, or 3"
    exit 1
fi

if ! [[ "$DIFFICULTY" =~ ^[1-3]$ ]]; then
    echo "Error: DIFFICULTY must be 1, 2, or 3"
    exit 1
fi

if ! [[ "$EVIL" =~ ^[1-3]$ ]]; then
    echo "Error: EVIL must be 1, 2, or 3"
    exit 1
fi

if ! [[ "$PYRAMID_TARGET" =~ ^[0-9]+$ ]] || [ "$PYRAMID_TARGET" -lt 1 ] || [ "$PYRAMID_TARGET" -gt 50 ]; then
    echo "Error: PYRAMID_TARGET must be between 1 and 50"
    exit 1
fi

if ! [[ "$MAX_ATTEMPTS" =~ ^[0-9]+$ ]] || [ "$MAX_ATTEMPTS" -lt 1 ] || [ "$MAX_ATTEMPTS" -gt 500 ]; then
    echo "Error: MAX_ATTEMPTS must be between 1 and 500"
    exit 1
fi

# Check dependencies
if [ ! -f "$TERRARIA_SERVER" ]; then
    echo "Error: TerrariaServer not found at: $TERRARIA_SERVER"
    exit 1
fi

if [ ! -f "$PYTHON_CHECKER" ]; then
    echo "Error: Python checker not found at: $PYTHON_CHECKER"
    exit 1
fi

mkdir -p "$WORLD_DIR"

# Parameter names
SIZE_NAME=("" "Small" "Medium" "Large")
DIFFICULTY_NAME=("" "Normal" "Expert" "Master")
EVIL_NAME=("" "Random" "Corruption" "Crimson")

echo "========================================="
echo "Terraria Pyramid World Generator"
echo "========================================="
echo "World Size: ${SIZE_NAME[$SIZE]}"
echo "Difficulty: ${DIFFICULTY_NAME[$DIFFICULTY]}"
echo "Evil Type: ${EVIL_NAME[$EVIL]}"
echo "Target: Find $PYRAMID_TARGET world(s) with pyramids"
echo "Max Attempts: $MAX_ATTEMPTS"
echo "Delete Mode: ON (worlds without pyramids will be deleted)"
echo "========================================="
echo ""

# Statistics
TOTAL_GENERATED=0
PYRAMIDS_FOUND=0
PYRAMID_WORLDS=()
PYRAMID_COORDS=()

# Start time
START_TIME=$(date +%s)

# Generate worlds until target reached or max attempts exceeded
while [ $PYRAMIDS_FOUND -lt $PYRAMID_TARGET ] && [ $TOTAL_GENERATED -lt $MAX_ATTEMPTS ]; do
    TOTAL_GENERATED=$((TOTAL_GENERATED + 1))

    echo "[$TOTAL_GENERATED] Generating world (Pyramids: $PYRAMIDS_FOUND/$PYRAMID_TARGET)..."

    # Generate unique world name
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    WORLD_NAME="World_${TIMESTAMP}_${TOTAL_GENERATED}"
    WORLD_PATH="$WORLD_DIR/${WORLD_NAME}.wld"

    # Create input file for automation
    INPUT_FILE=$(mktemp)
    echo "n" > "$INPUT_FILE"
    echo "$SIZE" >> "$INPUT_FILE"
    echo "$DIFFICULTY" >> "$INPUT_FILE"
    echo "$EVIL" >> "$INPUT_FILE"
    echo "$WORLD_NAME" >> "$INPUT_FILE"
    echo "" >> "$INPUT_FILE"
    echo "exit" >> "$INPUT_FILE"

    # Run TerrariaServer
    "$TERRARIA_SERVER" < "$INPUT_FILE" > /dev/null 2>&1 &
    SERVER_PID=$!
    rm -f "$INPUT_FILE"

    # Wait for world file to be created
    WAIT_TIME=0
    MAX_WAIT=300
    WORLD_CREATED=false

    while [ $WAIT_TIME -lt $MAX_WAIT ]; do
        sleep 2
        WAIT_TIME=$((WAIT_TIME + 2))

        if [ -f "$WORLD_PATH" ] && [ -s "$WORLD_PATH" ]; then
            WORLD_CREATED=true
            break
        fi
    done

    # Kill the server process (but NOT the game client)
    kill $SERVER_PID 2>/dev/null
    sleep 1
    kill -9 $SERVER_PID 2>/dev/null
    # Only kill TerrariaServer processes, not Terraria game client
    pkill -9 -f "TerrariaServer" 2>/dev/null
    wait $SERVER_PID 2>/dev/null

    sleep 1

    # Find the actual generated world file
    ACTUAL_WORLD_PATH=""
    if [ -f "$WORLD_PATH" ]; then
        ACTUAL_WORLD_PATH="$WORLD_PATH"
    else
        LATEST_WORLD=$(ls -t "$WORLD_DIR"/*.wld 2>/dev/null | head -1)
        if [ -n "$LATEST_WORLD" ]; then
            ACTUAL_WORLD_PATH="$LATEST_WORLD"
        fi
    fi

    # Check if world was generated
    if [ -z "$ACTUAL_WORLD_PATH" ] || [ ! -f "$ACTUAL_WORLD_PATH" ]; then
        echo "  ✗ Error: World file not found, skipping..."
        continue
    fi

    FILE_SIZE=$(stat -f%z "$ACTUAL_WORLD_PATH" 2>/dev/null || stat -c%s "$ACTUAL_WORLD_PATH" 2>/dev/null || echo "0")
    if [ "$FILE_SIZE" -eq 0 ]; then
        echo "  ✗ Error: World file is empty, skipping..."
        rm -f "$ACTUAL_WORLD_PATH"
        continue
    fi

    echo "  ✓ Generated: $(basename "$ACTUAL_WORLD_PATH") ($(numfmt --to=iec-i --suffix=B $FILE_SIZE 2>/dev/null || echo "${FILE_SIZE} bytes"))"

    # Check for pyramids
    echo "  Checking for pyramids..."
    PYTHON_OUTPUT=$(python3 "$PYTHON_CHECKER" "$ACTUAL_WORLD_PATH" 2>&1)

    if echo "$PYTHON_OUTPUT" | grep -q "Found [0-9]* Sandstone Brick"; then
        PYRAMIDS_FOUND=$((PYRAMIDS_FOUND + 1))
        HIGHEST_POINT=$(echo "$PYTHON_OUTPUT" | grep "Highest point coordinates" | sed 's/.*Highest point coordinates: //')

        echo "  🎉 PYRAMID FOUND! $HIGHEST_POINT [$PYRAMIDS_FOUND/$PYRAMID_TARGET]"

        PYRAMID_WORLDS+=("$(basename "$ACTUAL_WORLD_PATH")")
        PYRAMID_COORDS+=("$HIGHEST_POINT")
    else
        echo "  ○ No pyramid - deleting..."
        rm -f "$ACTUAL_WORLD_PATH"
    fi

    echo ""
done

# End time
END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))

echo "========================================="
if [ $PYRAMIDS_FOUND -ge $PYRAMID_TARGET ]; then
    echo "SUCCESS! Target reached!"
else
    echo "Max attempts reached without finding target."
fi
echo "========================================="
echo "Total worlds generated: $TOTAL_GENERATED"
echo "Pyramids found: $PYRAMIDS_FOUND / $PYRAMID_TARGET"
if [ $TOTAL_GENERATED -gt 0 ]; then
    PERCENTAGE=$((PYRAMIDS_FOUND * 100 / TOTAL_GENERATED))
    echo "Success rate: ${PERCENTAGE}%"
fi
echo "Time elapsed: ${ELAPSED}s"
echo ""

if [ ${#PYRAMID_WORLDS[@]} -gt 0 ]; then
    echo "Worlds with pyramids:"
    for i in "${!PYRAMID_WORLDS[@]}"; do
        echo "  $((i+1)). ${PYRAMID_WORLDS[$i]} (${PYRAMID_COORDS[$i]})"
    done
else
    echo "No pyramids found."
fi
echo ""
echo "World directory: $WORLD_DIR"
echo "========================================="
