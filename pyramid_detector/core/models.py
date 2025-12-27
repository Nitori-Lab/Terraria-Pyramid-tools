"""
Data models for Terraria Pyramid Detector.

This module defines pure data structures used throughout the application.
All models are platform-agnostic and contain only business logic.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Tuple
from datetime import datetime

from .config import WorldConfig


@dataclass
class WorldGenerationParams:
    """
    Parameters for world generation (platform-agnostic).

    Attributes:
        size: World size (1=Small, 2=Medium, 3=Large)
        difficulty: Difficulty level (1=Normal, 2=Expert, 3=Master)
        evil: Evil biome type (1=Random, 2=Corruption, 3=Crimson)
        world_name: Name of the world to generate
    """
    size: int
    difficulty: int
    evil: int
    world_name: str

    def __post_init__(self):
        """Validate parameters after initialization."""
        self.size = WorldConfig.validate_size(self.size)
        self.difficulty = WorldConfig.validate_difficulty(self.difficulty)
        self.evil = WorldConfig.validate_evil(self.evil)

        if not self.world_name or not self.world_name.strip():
            raise ValueError("World name cannot be empty")

    @property
    def size_label(self) -> str:
        """Get human-readable size label."""
        return WorldConfig.get_size_label(self.size)

    @property
    def difficulty_label(self) -> str:
        """Get human-readable difficulty label."""
        return WorldConfig.get_difficulty_label(self.difficulty)

    @property
    def evil_label(self) -> str:
        """Get human-readable evil type label."""
        return WorldConfig.get_evil_label(self.evil)

    def __str__(self) -> str:
        """String representation for logging."""
        return (f"WorldGenerationParams(size={self.size_label}, "
                f"difficulty={self.difficulty_label}, "
                f"evil={self.evil_label}, "
                f"world_name='{self.world_name}')")


@dataclass
class PyramidDetectionResult:
    """
    Result of pyramid detection in a world.

    Attributes:
        world_path: Path to the world file
        found: Whether a pyramid was found
        block_count: Total number of sandstone brick blocks found
        first_coord: Coordinates of first pyramid block (x, y)
        detection_time: Time taken for detection (seconds)
        error_message: Error message if detection failed
    """
    world_path: Path
    found: bool
    block_count: int = 0
    first_coord: Optional[Tuple[int, int]] = None
    detection_time: float = 0.0
    error_message: str = ""

    @property
    def success(self) -> bool:
        """Whether detection completed successfully (even if no pyramid found)."""
        return not self.error_message

    def __str__(self) -> str:
        """String representation for logging."""
        if not self.success:
            return f"PyramidDetectionResult(error='{self.error_message}')"

        if self.found:
            coord_str = f"at {self.first_coord}" if self.first_coord else ""
            return (f"PyramidDetectionResult(found=True, blocks={self.block_count}, "
                   f"{coord_str})")
        else:
            return "PyramidDetectionResult(found=False)"


@dataclass
class WorldGenerationResult:
    """
    Result of a single world generation attempt.

    Attributes:
        params: Generation parameters used
        world_path: Path to generated world file (if successful)
        success: Whether generation succeeded
        pyramid_detection: Pyramid detection result (if performed)
        generation_time: Time taken for generation (seconds)
        error_message: Error message if generation failed
        deleted: Whether the world was deleted (e.g., no pyramid found)
    """
    params: WorldGenerationParams
    world_path: Optional[Path] = None
    success: bool = True
    pyramid_detection: Optional[PyramidDetectionResult] = None
    generation_time: float = 0.0
    error_message: str = ""
    deleted: bool = False

    @property
    def has_pyramid(self) -> bool:
        """Whether this world contains a pyramid."""
        return (self.pyramid_detection is not None
                and self.pyramid_detection.found)

    @property
    def world_name(self) -> str:
        """Get world name from parameters."""
        return self.params.world_name

    def __str__(self) -> str:
        """String representation for logging."""
        if not self.success:
            return f"WorldGenerationResult(failed: {self.error_message})"

        status = "DELETED" if self.deleted else ("PYRAMID" if self.has_pyramid else "NO_PYRAMID")
        return f"WorldGenerationResult({self.world_name}: {status})"


@dataclass
class GenerationStatistics:
    """
    Statistics for a batch of world generations.

    Attributes:
        total_generated: Total worlds generated
        pyramids_found: Number of worlds with pyramids
        worlds_deleted: Number of worlds deleted
        total_time: Total time elapsed (seconds)
        pyramid_worlds: List of world names that contain pyramids
        start_time: When generation started
        end_time: When generation ended
    """
    total_generated: int = 0
    pyramids_found: int = 0
    worlds_deleted: int = 0
    total_time: float = 0.0
    pyramid_worlds: list = field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    @property
    def success_rate(self) -> float:
        """Calculate pyramid success rate (0-100%)."""
        if self.total_generated == 0:
            return 0.0
        return (self.pyramids_found / self.total_generated) * 100

    @property
    def average_time_per_world(self) -> float:
        """Calculate average generation time per world (seconds)."""
        if self.total_generated == 0:
            return 0.0
        return self.total_time / self.total_generated

    def add_result(self, result: WorldGenerationResult):
        """
        Add a generation result to statistics.

        Args:
            result: World generation result to add
        """
        if result.success:
            self.total_generated += 1
            self.total_time += result.generation_time

            if result.has_pyramid:
                self.pyramids_found += 1
                self.pyramid_worlds.append(result.world_name)

            if result.deleted:
                self.worlds_deleted += 1

    def __str__(self) -> str:
        """String representation for logging."""
        return (f"GenerationStatistics(generated={self.total_generated}, "
                f"pyramids={self.pyramids_found}, "
                f"success_rate={self.success_rate:.1f}%, "
                f"total_time={self.total_time:.1f}s)")
