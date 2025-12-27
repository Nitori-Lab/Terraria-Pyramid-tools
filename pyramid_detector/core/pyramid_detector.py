"""
Pyramid detection logic using lihzahrd library.

This module provides platform-agnostic pyramid detection
by analyzing Terraria world files.
"""

import time
from pathlib import Path
from typing import Optional, Tuple

try:
    import lihzahrd
except ImportError:
    lihzahrd = None

from .config import TileConfig
from .models import PyramidDetectionResult


class PyramidDetector:
    """
    Pyramid detector using lihzahrd library.

    This class provides pyramid detection by scanning Terraria world files
    for Sandstone Brick tiles (tile ID 151).
    """

    def __init__(self):
        """Initialize pyramid detector."""
        if lihzahrd is None:
            raise ImportError(
                "lihzahrd library is required for pyramid detection. "
                "Install it with: pip install lihzahrd"
            )

        self.sandstone_tile_id = TileConfig.SANDSTONE_BRICK_TILE_ID
        self.min_blocks = TileConfig.MIN_PYRAMID_BLOCKS

    def detect(self, world_path: Path) -> PyramidDetectionResult:
        """
        Detect pyramids in a Terraria world file.

        Args:
            world_path: Path to the .wld world file

        Returns:
            PyramidDetectionResult with detection information
        """
        start_time = time.time()

        try:
            # Convert Path to string for lihzahrd
            world_file_str = str(world_path)

            # Load world file
            world = lihzahrd.World.create_from_file(world_file_str)

            # Scan for sandstone bricks
            sandstone_count = 0
            first_coord: Optional[Tuple[int, int]] = None

            for x in range(world.size.x):
                for y in range(world.size.y):
                    tile = world.tiles[x, y]

                    # Check if tile is Sandstone Brick
                    if tile.block is not None and tile.block.type == self.sandstone_tile_id:
                        sandstone_count += 1

                        # Record first occurrence
                        if first_coord is None:
                            first_coord = (x, y)

            # Calculate detection time
            detection_time = time.time() - start_time

            # Determine if pyramid was found
            found = sandstone_count >= self.min_blocks

            return PyramidDetectionResult(
                world_path=world_path,
                found=found,
                block_count=sandstone_count,
                first_coord=first_coord,
                detection_time=detection_time
            )

        except FileNotFoundError:
            return PyramidDetectionResult(
                world_path=world_path,
                found=False,
                error_message=f"World file not found: {world_path}"
            )

        except Exception as e:
            return PyramidDetectionResult(
                world_path=world_path,
                found=False,
                error_message=f"Error detecting pyramid: {str(e)}"
            )

    def detect_multiple(self, world_paths: list) -> list:
        """
        Detect pyramids in multiple world files.

        Args:
            world_paths: List of paths to world files

        Returns:
            List of PyramidDetectionResult objects
        """
        results = []

        for world_path in world_paths:
            result = self.detect(Path(world_path))
            results.append(result)

        return results

    def get_summary(self, result: PyramidDetectionResult) -> str:
        """
        Get human-readable summary of detection result.

        Args:
            result: Detection result to summarize

        Returns:
            Summary string
        """
        if not result.success:
            return f"✗ Detection failed: {result.error_message}"

        if result.found:
            coord_str = ""
            if result.first_coord:
                coord_str = f", First block at: ({result.first_coord[0]}, {result.first_coord[1]})"

            return (f"🎉 PYRAMID FOUND! "
                   f"Count: {result.block_count}{coord_str}")
        else:
            return "○ No pyramid found in this world"
