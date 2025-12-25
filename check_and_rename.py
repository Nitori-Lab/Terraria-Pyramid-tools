#!/usr/bin/env python3
"""
Check if a Terraria world contains pyramids (Sandstone Brick)
and rename it by adding "1 " prefix if found
"""
import sys
import os
from correct_parser import parse_world

def check_and_rename_world(world_path, verbose=False):
    """
    Check if world contains Sandstone Brick and rename if found

    Args:
        world_path: Path to the .wld file
        verbose: Print detailed information

    Returns:
        bool: True if pyramid found, False otherwise
    """
    try:
        # Parse world file
        coords = parse_world(world_path, verbose=verbose)

        if len(coords) > 0:
            # Pyramid found!
            highest = min(coords, key=lambda c: c[1])

            if not verbose:
                print(f"Found {len(coords)} Sandstone Brick tiles.")
                print(f"Highest point coordinates: X={highest[0]}, Y={highest[1]}")

            # Rename the file: add "1 " prefix
            directory = os.path.dirname(world_path)
            filename = os.path.basename(world_path)

            # Check if already has "1 " prefix
            if filename.startswith("1 "):
                print(f"World already has '1 ' prefix: {filename}")
                return True

            new_path = os.path.join(directory, "1 " + filename)

            # Rename the file
            os.rename(world_path, new_path)
            print(f"✓ Renamed to: {os.path.basename(new_path)}")

            return True
        else:
            if not verbose:
                print("No Sandstone Brick (tile ID: 151) found in the world.")
            return False

    except Exception as e:
        print(f"Error: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 check_and_rename.py <world_file.wld> [--verbose]")
        print("\nChecks if the world contains pyramids (Sandstone Brick)")
        print("and renames it by adding '1 ' prefix if found.")
        sys.exit(1)

    world_file = sys.argv[1]
    verbose = "--verbose" in sys.argv or "-v" in sys.argv

    if not os.path.exists(world_file):
        print(f"Error: File not found: {world_file}")
        sys.exit(1)

    print(f"Checking world: {os.path.basename(world_file)}")
    print("="*60)

    has_pyramid = check_and_rename_world(world_file, verbose=verbose)

    print("="*60)

    # Exit code: 0 if pyramid found, 1 if not
    sys.exit(0 if has_pyramid else 1)

if __name__ == "__main__":
    main()
