#!/usr/bin/env python3
"""
Simple Terraria 1.4.4.9 Sandstone Brick finder
Scans the world file for tile ID 151 (Sandstone Brick) and reports the highest point
"""
import struct
import sys

SANDSTONE_BRICK = 151

def read_byte(f):
    data = f.read(1)
    if not data:
        return None
    return struct.unpack("<B", data)[0]

def read_short(f):
    data = f.read(2)
    if len(data) < 2:
        return None
    return struct.unpack("<H", data)[0]

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 sandstone_finder.py <world_file.wld>")
        sys.exit(1)

    world_file = sys.argv[1]

    print(f"Scanning {world_file} for Sandstone Brick (tile ID: {SANDSTONE_BRICK})...")

    # Search for the tile ID pattern in the file
    found_tiles = []

    with open(world_file, "rb") as f:
        # Read entire file into memory (world files are typically < 100MB)
        data = f.read()

    # Search for little-endian short value of 151 (0x0097)
    # In little-endian: 0x97 0x00
    target_bytes = struct.pack("<H", SANDSTONE_BRICK)

    print(f"Searching for byte pattern: {target_bytes.hex()}...")

    offset = 0
    count = 0
    while True:
        offset = data.find(target_bytes, offset)
        if offset == -1:
            break
        count += 1
        found_tiles.append(offset)
        offset += 1

    print(f"\nFound {count} occurrences of tile ID {SANDSTONE_BRICK} pattern in file")

    if count > 0:
        print(f"\nFirst few occurrences at file offsets:")
        for i, off in enumerate(found_tiles[:10]):
            context_start = max(0, off - 4)
            context_end = min(len(data), off + 6)
            context = data[context_start:context_end]
            print(f"  Offset 0x{off:08x}: {context.hex()}")
    else:
        print(f"\nNo Sandstone Brick (tile ID {SANDSTONE_BRICK}) found in world file.")

if __name__ == "__main__":
    main()
