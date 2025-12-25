#!/usr/bin/env python3
"""
Analyze all tile types in a Terraria world file
"""
import sys
from correct_parser import parse_world

def analyze_tiles(world_file):
    """Analyze all tile types in a world"""
    import struct

    tile_counts = {}

    with open(world_file, "rb") as f:
        # Read version
        version = struct.unpack("<i", f.read(4))[0]

        # Read magic header
        if version >= 135:
            f.read(7)  # "relogic"
            f.read(1)  # file_type
            f.read(4)  # revision
            f.read(8)  # is_favorite

        # Read section pointers
        num_sections = struct.unpack("<h", f.read(2))[0]
        section_pointers = []
        for i in range(num_sections):
            pointer = struct.unpack("<i", f.read(4))[0]
            section_pointers.append(pointer)

        # Read tile frame importants
        num_tile_types = struct.unpack("<h", f.read(2))[0]
        tile_frame_important = []
        for i in range(num_tile_types):
            tile_id = struct.unpack("<h", f.read(2))[0]
            tile_frame_important.append(tile_id)

        # Jump to Header section to get world dimensions
        header_offset = section_pointers[0]
        f.seek(header_offset)

        # Read world name
        name_len = struct.unpack("<B", f.read(1))[0]
        if name_len > 0:
            f.read(name_len)

        # Read seed
        seed_len = struct.unpack("<B", f.read(1))[0]
        if seed_len > 0:
            f.read(seed_len)

        # Read world gen version
        f.read(8)

        if version >= 179:
            f.read(16)  # guid

        # Read world boundaries
        f.read(4)  # world_id
        f.read(4)  # left
        f.read(4)  # right
        f.read(4)  # top
        f.read(4)  # bottom
        max_tiles_y = struct.unpack("<i", f.read(4))[0]
        max_tiles_x = struct.unpack("<i", f.read(4))[0]

        # Jump to tiles section
        tiles_offset = section_pointers[1]
        f.seek(tiles_offset)

        # Parse tiles
        for x in range(max_tiles_x):
            y = 0
            while y < max_tiles_y:
                active_flags = struct.unpack("<B", f.read(1))[0]

                tile_flags = 0
                tile_flags2 = 0
                tile_flags3 = 0

                if active_flags & 0x01:
                    tile_flags = struct.unpack("<B", f.read(1))[0]
                    if tile_flags & 0x01:
                        tile_flags2 = struct.unpack("<B", f.read(1))[0]
                        if tile_flags2 & 0x01:
                            tile_flags3 = struct.unpack("<B", f.read(1))[0]

                tile_type = None
                if active_flags & 0x02:
                    tile_type = struct.unpack("<B", f.read(1))[0]
                    if tile_flags & 0x20:
                        high_byte = struct.unpack("<B", f.read(1))[0]
                        tile_type = tile_type | (high_byte << 8)

                    tile_counts[tile_type] = tile_counts.get(tile_type, 0) + 1

                    if tile_type in tile_frame_important:
                        f.read(2)  # texture_u
                        f.read(2)  # texture_v

                if active_flags & 0x04:
                    f.read(1)  # wall_type
                    if tile_flags & 0x40:
                        f.read(1)  # wall_high

                liquid_type = (active_flags >> 3) & 0x03
                if liquid_type != 0:
                    f.read(1)  # liquid_amount

                if tile_flags2 & 0x08:
                    f.read(1)  # tile_color
                if tile_flags2 & 0x10:
                    f.read(1)  # wall_color

                rle_storage = (active_flags >> 6) & 0x03
                rle_count = 0

                if rle_storage == 1:
                    rle_count = struct.unpack("<B", f.read(1))[0]
                elif rle_storage == 2:
                    rle_count = struct.unpack("<H", f.read(2))[0]

                num_tiles = rle_count + 1
                y += num_tiles

    return tile_counts

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 analyze_tiles.py <world_file.wld>")
        sys.exit(1)

    world_file = sys.argv[1]

    print(f"Analyzing: {world_file}")
    print("="*60)

    tile_counts = analyze_tiles(world_file)

    print(f"Total unique tile types: {len(tile_counts)}")
    print(f"Min tile ID: {min(tile_counts.keys())}")
    print(f"Max tile ID: {max(tile_counts.keys())}")
    print("")

    print("All tile IDs found (sorted):")
    sorted_tiles = sorted(tile_counts.keys())
    for i in range(0, len(sorted_tiles), 20):
        print("  " + ", ".join(str(t) for t in sorted_tiles[i:i+20]))

    print("")
    print("Checking for Sandstone Brick (ID 151):")
    if 151 in tile_counts:
        print(f"  ✓ FOUND! Count: {tile_counts[151]}")
    else:
        print(f"  ✗ NOT FOUND")
        # Check nearby IDs
        nearby = [id for id in range(145, 160) if id in tile_counts]
        if nearby:
            print(f"  Nearby IDs found: {nearby}")
