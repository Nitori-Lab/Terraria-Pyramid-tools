#!/usr/bin/env python3
"""
Terraria 1.4.4.9 Sandstone Brick Detector
Finds all Sandstone Brick tiles (ID: 151) and reports the highest point
"""
import sys
import lihzahrd

SANDSTONE_BRICK = 151

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 main.py <path_to_world_file.wld>")
        sys.exit(1)

    world_file = sys.argv[1]

    try:
        print(f"Parsing world file: {world_file}")
        world = lihzahrd.World.create_from_file(world_file)

        print(f"World: {world.name}")
        print(f"Size: {world.size.x} x {world.size.y}")
        print(f"\nSearching for Sandstone Brick (tile ID: {SANDSTONE_BRICK})...")

        # Find all Sandstone Brick tiles
        sandstone_coords = []

        for x in range(world.size.x):
            for y in range(world.size.y):
                tile = world.tiles[x, y]
                if tile.block is not None and tile.block.type == SANDSTONE_BRICK:
                    sandstone_coords.append((x, y))

            # Progress indicator
            if x % 500 == 0:
                print(f"  Progress: {x}/{world.size.x} columns...", end='\r')

        print()  # New line after progress

        # Report results
        print("\n" + "="*60)
        if len(sandstone_coords) == 0:
            print("No Sandstone Brick (tile ID: 151) found in the world.")
        else:
            print(f"Found {len(sandstone_coords)} Sandstone Brick tiles.")

            # Find the highest point (smallest Y coordinate)
            highest_tile = min(sandstone_coords, key=lambda coord: coord[1])
            print(f"Highest point coordinates: X={highest_tile[0]}, Y={highest_tile[1]}")
        print("="*60)

    except FileNotFoundError:
        print(f"Error: World file '{world_file}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error parsing world file: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
