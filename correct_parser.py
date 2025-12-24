#!/usr/bin/env python3
"""
Correct Terraria 1.4.4.9 World File Parser
Finds Sandstone Brick (tile ID 151) and reports the highest point
"""
import struct
import sys

SANDSTONE_BRICK = 151

def read_int32(f):
    return struct.unpack("<i", f.read(4))[0]

def read_int16(f):
    return struct.unpack("<h", f.read(2))[0]

def read_uint16(f):
    return struct.unpack("<H", f.read(2))[0]

def read_byte(f):
    return struct.unpack("<B", f.read(1))[0]

def read_bool(f):
    return struct.unpack("<?", f.read(1))[0]

def read_string(f):
    length = read_byte(f)
    if length == 0:
        return ""
    return f.read(length).decode("utf-8", errors="ignore")

def parse_world(filename, verbose=False):
    """Parse Terraria world file and find all Sandstone Brick tiles"""

    with open(filename, "rb") as f:
        # Read version
        version = read_int32(f)
        if verbose:
            print(f"World version: {version}")

        if version < 88:
            raise RuntimeError("World version too old (< 88)")

        # Read magic header (version >= 135)
        if version >= 135:
            magic = f.read(7).decode('ascii')  # "relogic" - fixed 7 bytes, no length prefix
            file_type = read_byte(f)  # 2 for world
            revision = read_int32(f)
            is_favorite = struct.unpack("<Q", f.read(8))[0]  # Int64 favorite flags
            if verbose:
                print(f"Magic: {magic}, File type: {file_type}, Revision: {revision}, Favorite: {is_favorite}")

        # Read section pointers (version >= 88)
        num_sections = read_int16(f)
        if verbose:
            print(f"Number of sections: {num_sections}")

        section_pointers = []
        for i in range(num_sections):
            pointer = read_int32(f)
            section_pointers.append(pointer)
            if verbose and i < 10:
                section_names = ["Header", "Tiles", "Chests", "Signs", "NPCs", "Entities",
                               "Pressure Plates", "Town Manager", "Bestiary", "Creative Powers"]
                name = section_names[i] if i < len(section_names) else f"Section {i}"
                print(f"  {name} pointer: 0x{pointer:08x} ({pointer})")

        # Read tile frame importants
        num_tile_types = read_int16(f)
        tile_frame_important = []
        for i in range(num_tile_types):
            tile_id = read_int16(f)
            tile_frame_important.append(tile_id)

        if verbose:
            print(f"Tile frame important count: {num_tile_types}")
            print(f"Important tiles: {tile_frame_important[:20]}...")

        # Jump to Tiles section
        if len(section_pointers) < 2:
            raise RuntimeError("No Tiles section pointer found")

        tiles_offset = section_pointers[1]
        f.seek(tiles_offset)

        if verbose:
            print(f"\nJumping to Tiles section at offset: 0x{tiles_offset:08x}")

        # We need world dimensions - they're in the Header section
        # Jump to Header section to read world size
        header_offset = section_pointers[0]
        current_pos = f.tell()
        f.seek(header_offset)

        # Read minimal header to get world dimensions
        world_name = read_string(f)
        seed = read_string(f)
        world_gen_version = struct.unpack("<q", f.read(8))[0]  # Int64 for version >= 181

        if version >= 179:
            guid = f.read(16)

        world_id = read_int32(f)
        left = read_int32(f)
        right = read_int32(f)
        top = read_int32(f)
        bottom = read_int32(f)
        max_tiles_y = read_int32(f)
        max_tiles_x = read_int32(f)

        if verbose:
            print(f"\nWorld: {world_name}")
            print(f"World size: {max_tiles_x} x {max_tiles_y}")

        # Go back to tiles section
        f.seek(tiles_offset)

        # Parse tiles - COLUMN FIRST (x then y)
        sandstone_coords = []
        tile_counts = {}

        if verbose:
            print(f"\nParsing tiles (column-first)...")

        for x in range(max_tiles_x):
            y = 0
            while y < max_tiles_y:
                # Read ActiveFlags
                active_flags = read_byte(f)

                # Check if TileFlags present (bit 0)
                tile_flags = 0
                tile_flags2 = 0
                tile_flags3 = 0

                if active_flags & 0x01:  # Has TileFlags
                    tile_flags = read_byte(f)
                    if tile_flags & 0x01:  # Has TileFlags2
                        tile_flags2 = read_byte(f)
                        if tile_flags2 & 0x01:  # Has TileFlags3
                            tile_flags3 = read_byte(f)

                # Check if tile present (bit 1 of ActiveFlags)
                tile_type = None
                if active_flags & 0x02:  # Tile present
                    tile_type = read_byte(f)
                    # Check if high byte present (bit 5 of TileFlags)
                    if tile_flags & 0x20:
                        high_byte = read_byte(f)
                        tile_type = tile_type | (high_byte << 8)

                    # Track tile types
                    tile_counts[tile_type] = tile_counts.get(tile_type, 0) + 1

                    # Debug: log tiles near ID 151
                    if verbose and 145 <= tile_type <= 155:
                        print(f"\n  Found tile ID {tile_type} at ({x}, {y})")

                    # Check for important tiles (need UV coordinates)
                    if tile_type in tile_frame_important:
                        texture_u = read_int16(f)
                        texture_v = read_int16(f)

                    # Found Sandstone Brick!
                    if tile_type == SANDSTONE_BRICK:
                        sandstone_coords.append((x, y))
                        if verbose:
                            print(f"\n*** FOUND SANDSTONE BRICK at ({x}, {y}) ***")

                # Wall (bit 2 of ActiveFlags)
                if active_flags & 0x04:
                    wall_type = read_byte(f)
                    # High byte of wall if bit 6 of TileFlags set
                    if tile_flags & 0x40:
                        wall_high = read_byte(f)

                # Liquid (bits 3-4 of ActiveFlags)
                liquid_type = (active_flags >> 3) & 0x03
                if liquid_type != 0:
                    liquid_amount = read_byte(f)

                # Wire/slope info in TileFlags (bits 2-7)
                # Actuator info in TileFlags2 (bits 2-3)

                # Colors (bits 4-5 of TileFlags2)
                if tile_flags2 & 0x08:  # Has tile color
                    tile_color = read_byte(f)
                if tile_flags2 & 0x10:  # Has wall color
                    wall_color = read_byte(f)

                # RLE (bits 6-7 of ActiveFlags)
                rle_storage = (active_flags >> 6) & 0x03
                rle_count = 0

                if rle_storage == 1:
                    rle_count = read_byte(f)
                elif rle_storage == 2:
                    rle_count = read_uint16(f)

                # RLE means: current tile + next rle_count tiles are the same
                # So total tiles = rle_count + 1
                num_tiles = rle_count + 1

                # If this is Sandstone Brick, record all coordinates
                if tile_type == SANDSTONE_BRICK:
                    for dy in range(num_tiles):
                        if y + dy < max_tiles_y:
                            sandstone_coords.append((x, y + dy))
                            if verbose:
                                print(f"\n*** FOUND SANDSTONE BRICK at ({x}, {y + dy}) ***")

                # Advance y by number of tiles covered
                y += num_tiles

            if verbose and x % 100 == 0:
                print(f"  Processed column {x}/{max_tiles_x}...", end='\r')

        if verbose:
            print(f"\nParsing complete!")
            print(f"\nUnique tile types found: {len(tile_counts)}")
            if SANDSTONE_BRICK in tile_counts:
                print(f"Sandstone Brick (ID {SANDSTONE_BRICK}): {tile_counts[SANDSTONE_BRICK]} tiles")
            else:
                print(f"Sandstone Brick (ID {SANDSTONE_BRICK}): NOT FOUND")
                print(f"Sample tile types: {sorted(tile_counts.keys())[:30]}")

        return sandstone_coords

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 correct_parser.py <world_file.wld> [--verbose]")
        sys.exit(1)

    world_file = sys.argv[1]
    verbose = "--verbose" in sys.argv or "-v" in sys.argv

    try:
        coords = parse_world(world_file, verbose=verbose)

        print("\n" + "="*60)
        if len(coords) == 0:
            print("No Sandstone Brick (tile ID: 151) found in the world.")
        else:
            print(f"Found {len(coords)} Sandstone Brick tiles.")

            # Find highest point (smallest Y coordinate)
            highest = min(coords, key=lambda c: c[1])
            print(f"Highest point coordinates: X={highest[0]}, Y={highest[1]}")
        print("="*60)

    except FileNotFoundError:
        print(f"Error: World file '{world_file}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error parsing world file: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
