#!/bin/bash

# Terraria 1.4.4.9 Batch World Generator
# Usage: ./tworldGen.sh [SIZE] [DIFFICULTY] [EVIL] [COUNT]
# SIZE: 1=Small, 2=Medium, 3=Large (default: 2)
# DIFFICULTY: 1=Normal, 2=Expert, 3=Master (default: 1)
# EVIL: 1=Random, 2=Corruption, 3=Crimson (default: 1)
# COUNT: Number of worlds to generate, max 200 (default: 1)

# Path to TerrariaServer executable
TERRARIA_SERVER="/Users/lhy/Library/Application Support/Steam/steamapps/common/Terraria/Terraria.app/Contents/MacOS/TerrariaServer"

# World save directory
WORLD_DIR="$HOME/Library/Application Support/Terraria/Worlds"

# Parse arguments with defaults
SIZE=${1:-2}
DIFFICULTY=${2:-1}
EVIL=${3:-1}
COUNT=${4:-1}

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

# Check if TerrariaServer exists
if [ ! -f "$TERRARIA_SERVER" ]; then
    echo "Error: TerrariaServer not found at: $TERRARIA_SERVER"
    exit 1
fi

# Ensure world directory exists
mkdir -p "$WORLD_DIR"

# Parameter name mappings
SIZE_NAME=("" "Small" "Medium" "Large")
DIFFICULTY_NAME=("" "Normal" "Expert" "Master")
EVIL_NAME=("" "Random" "Corruption" "Crimson")

echo "========================================="
echo "Terraria Batch World Generator"
echo "========================================="
echo "World Size: ${SIZE_NAME[$SIZE]}"
echo "Difficulty: ${DIFFICULTY_NAME[$DIFFICULTY]}"
echo "Evil Type: ${EVIL_NAME[$EVIL]}"
echo "Count: $COUNT"
echo "========================================="
echo ""

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

    # Build server command parameters
    # -autocreate: 1=Small, 2=Medium, 3=Large
    # -worldname: World name
    # -difficulty: 0=Normal, 1=Expert, 2=Master (needs conversion)
    # -worldevil: corruption/crimson/random

    DIFFICULTY_PARAM=$((DIFFICULTY - 1))

    case $EVIL in
        1) EVIL_PARAM="" ;;  # Random - no parameter needed
        2) EVIL_PARAM="-worldevil corruption" ;;
        3) EVIL_PARAM="-worldevil crimson" ;;
    esac

    # Generate random seed
    SEED=$RANDOM$RANDOM

    # Create input file for automation
    INPUT_FILE=$(mktemp)
    echo "n" > "$INPUT_FILE"  # Create new world
    echo "$SIZE" >> "$INPUT_FILE"  # World size
    echo "$DIFFICULTY" >> "$INPUT_FILE"  # Difficulty
    echo "$EVIL" >> "$INPUT_FILE"  # Evil type (1=Random, 2=Corruption, 3=Crimson)
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

    # Kill the server process
    kill $SERVER_PID 2>/dev/null
    wait $SERVER_PID 2>/dev/null

    # Additional wait for filesystem sync
    sleep 1

    # Check if world file was successfully generated
    if [ -f "$WORLD_PATH" ]; then
        FILE_SIZE=$(stat -f%z "$WORLD_PATH" 2>/dev/null || echo "0")
        if [ "$FILE_SIZE" -gt 0 ]; then
            echo "✓ Generated: ${WORLD_NAME}.wld (Size: $(numfmt --to=iec-i --suffix=B $FILE_SIZE 2>/dev/null || echo "${FILE_SIZE} bytes"))"
        else
            echo "✗ Error: World file created but size is 0"
            echo "Generation failed, stopping execution"
            exit 1
        fi
    else
        # Try to find the most recently created .wld file
        LATEST_WORLD=$(ls -t "$WORLD_DIR"/*.wld 2>/dev/null | head -1)
        AFTER_FILES=$(ls -1 "$WORLD_DIR"/*.wld 2>/dev/null | wc -l | tr -d ' ')

        if [ "$AFTER_FILES" -gt "$BEFORE_FILES" ] && [ -n "$LATEST_WORLD" ]; then
            echo "✓ Detected new world file: $(basename "$LATEST_WORLD")"
        else
            echo "✗ Error: Generated world file not found in world directory"
            echo "Expected path: $WORLD_PATH"
            echo "World directory: $WORLD_DIR"
            echo "Generation failed, stopping execution"
            exit 1
        fi
    fi

    echo ""
done

echo "========================================="
echo "Batch generation complete!"
echo "Total worlds generated: $COUNT"
echo "World directory: $WORLD_DIR"
echo "========================================="
