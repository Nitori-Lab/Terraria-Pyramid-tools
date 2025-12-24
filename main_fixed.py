import struct
import sys

SANDSTONE_BRICK = 151  # Terraria 1.4.x

def read_int(f):
    return struct.unpack("<i", f.read(4))[0]

def read_short(f):
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

def read_double(f):
    return struct.unpack("<d", f.read(8))[0]

def skip_bytes(f, count):
    f.read(count)

def parse_wld(filename, verbose=False):
    coords = []

    with open(filename, "rb") as f:
        # File Header
        version = read_int(f)
        if verbose:
            print(f"World version: {version}")

        magic = read_string(f)  # "relogic"
        file_type = read_byte(f)
        revision = read_int(f)
        is_favorite = read_bool(f)

        # Pointers section
        num_pointers = read_short(f)
        pointers = []
        for i in range(num_pointers):
            section_id = read_short(f)
            offset = read_int(f)
            pointers.append((section_id, offset))
            if verbose and section_id == 2:  # Tiles section
                print(f"Tiles section offset: {offset}")

        # Tile frame importants
        num_tile_frame_important = read_short(f)
        for i in range(num_tile_frame_important):
            read_short(f)

        # World header
        world_name = read_string(f)
        if verbose:
            print(f"World name: {world_name}")

        seed = read_string(f)
        world_gen_version = read_int(f)
        world_id = read_int(f)

        left_world = read_int(f)
        right_world = read_int(f)
        top_world = read_int(f)
        bottom_world = read_int(f)

        world_height = read_int(f)
        world_width = read_int(f)

        if verbose:
            print(f"World size: {world_width}x{world_height}")

        # Skip the rest of header - find tiles section using pointer
        tiles_offset = None
        for section_id, offset in pointers:
            if section_id == 2:  # Tiles section
                tiles_offset = offset
                break

        if tiles_offset is None:
            raise RuntimeError("Could not find tiles section offset")

        # Jump to tiles section
        f.seek(tiles_offset)

        # Read tiles
        tile_type_counts = {}
        if verbose:
            print(f"\nScanning tiles from offset {tiles_offset}...")

        for y in range(world_height):
            x = 0
            while x < world_width:
                flags1 = read_byte(f)

                active = flags1 & 0x01
                has_flags2 = flags1 & 0x80

                flags2 = read_byte(f) if has_flags2 else 0
                has_flags3 = flags2 & 0x80

                if has_flags3:
                    read_byte(f)  # flags3

                tile_type = None

                if active:
                    tile_type = read_short(f)
                    if verbose:
                        tile_type_counts[tile_type] = tile_type_counts.get(tile_type, 0) + 1

                # Skip wall
                if flags1 & 0x02:
                    read_short(f)

                # Skip liquid
                if flags1 & 0x04:
                    read_byte(f)

                # Skip colors
                if flags1 & 0x10:
                    read_byte(f)
                if flags1 & 0x20:
                    read_byte(f)

                # RLE
                rle = 0
                if flags2 & 0x01:
                    rle = read_byte(f)
                elif flags2 & 0x02:
                    rle = read_short(f)

                count = rle + 1

                if tile_type == SANDSTONE_BRICK:
                    for i in range(count):
                        coords.append((x + i, y))

                x += count

        if verbose:
            print(f"\nTotal unique tile types found: {len(tile_type_counts)}")
            if SANDSTONE_BRICK in tile_type_counts:
                print(f"Sandstone Brick (ID {SANDSTONE_BRICK}) count: {tile_type_counts[SANDSTONE_BRICK]}")
            else:
                print(f"Sandstone Brick (ID {SANDSTONE_BRICK}) NOT found in tile types")
                print(f"\nAll tile types found: {sorted(tile_type_counts.keys())}")

    return coords


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 main_fixed.py <path_to_world_file.wld> [--verbose]")
        sys.exit(1)

    world_file = sys.argv[1]
    verbose = "--verbose" in sys.argv or "-v" in sys.argv

    try:
        sandstone_tiles = parse_wld(world_file, verbose=verbose)

        print("\n" + "="*50)
        if len(sandstone_tiles) == 0:
            print("No Sandstone Brick (tile ID: 151) found in the world.")
        else:
            print(f"Found {len(sandstone_tiles)} Sandstone Brick tiles.")

            # Find the highest point (smallest Y coordinate)
            highest_tile = min(sandstone_tiles, key=lambda coord: coord[1])
            print(f"Highest point coordinates: X={highest_tile[0]}, Y={highest_tile[1]}")
        print("="*50)

    except FileNotFoundError:
        print(f"Error: World file '{world_file}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error parsing world file: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
