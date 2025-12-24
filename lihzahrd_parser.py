#!/usr/bin/env python3
"""
Use lihzahrd library to parse Terraria world and find Sandstone Brick
"""
import sys
import lihzahrd

SANDSTONE_BRICK = 151

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 lihzahrd_parser.py <world_file.wld>")
        sys.exit(1)

    world_file = sys.argv[1]
    verbose = "--verbose" in sys.argv or "-v" in sys.argv

    print(f"Parsing {world_file} with lihzahrd...")

    try:
        world = lihzahrd.World.create_from_file(world_file)

        if verbose:
            print(f"World name: {world.name}")
            print(f"World size: {world.size.x} x {world.size.y}")

        # Search for Sandstone Brick
        sandstone_coords = []

        for x in range(world.size.x):
            for y in range(world.size.y):
                tile = world.tiles[x, y]
                if tile.block is not None and tile.block.type == SANDSTONE_BRICK:
                    sandstone_coords.append((x, y))

            if verbose and x % 500 == 0:
                print(f"  Processed column {x}/{world.size.x}...", end='\r')

        if verbose:
            print(f"\nParsing complete!")

        print("\n" + "="*60)
        if len(sandstone_coords) == 0:
            print(f"No Sandstone Brick (tile ID: {SANDSTONE_BRICK}) found in the world.")
        else:
            print(f"Found {len(sandstone_coords)} Sandstone Brick tiles.")

            # Find highest point (smallest Y coordinate)
            highest = min(sandstone_coords, key=lambda c: c[1])
            print(f"Highest point coordinates: X={highest[0]}, Y={highest[1]}")

            if verbose:
                print(f"\nFirst 10 Sandstone Brick locations:")
                for i, (x, y) in enumerate(sandstone_coords[:10]):
                    print(f"  {i+1}. ({x}, {y})")

        print("="*60)

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
