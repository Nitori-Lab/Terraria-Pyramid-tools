#!/bin/bash

# Cleanup script for stuck Terraria processes
# Run this if you see TerrariaServer processes stuck in the background

echo "Searching for Terraria processes..."

TERRARIA_PIDS=$(ps aux | grep -E "Terraria|TerrariaServer" | grep -v grep | awk '{print $2}')

if [ -z "$TERRARIA_PIDS" ]; then
    echo "No Terraria processes found."
    exit 0
fi

echo "Found the following Terraria processes:"
ps aux | grep -E "Terraria|TerrariaServer" | grep -v grep

echo ""
echo "Killing processes..."
echo "$TERRARIA_PIDS" | xargs kill -9 2>/dev/null

echo "Done! All Terraria processes terminated."
