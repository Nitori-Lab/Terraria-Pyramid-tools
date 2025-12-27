"""
Core configuration and business rules for Terraria Pyramid Detector.

This module defines the single source of truth for all business constraints,
validation rules, and configuration constants.
"""

from typing import Dict


class WorldConfig:
    """World generation configuration and business rules."""

    # ==================== Value Ranges (Business Rules) ====================
    SIZE_RANGE = (1, 3)           # Small, Medium, Large
    DIFFICULTY_RANGE = (1, 3)     # Normal, Expert, Master
    EVIL_RANGE = (1, 3)           # Random, Corruption, Crimson
    COUNT_RANGE = (1, 200)        # Max worlds per batch
    PYRAMID_TARGET_RANGE = (1, 50)    # Max pyramid worlds to find
    MAX_ATTEMPTS_RANGE = (1, 500)     # Max generation attempts

    # ==================== Display Labels ====================
    SIZE_LABELS: Dict[int, str] = {
        1: 'Small',
        2: 'Medium',
        3: 'Large'
    }

    DIFFICULTY_LABELS: Dict[int, str] = {
        1: 'Normal',
        2: 'Expert',
        3: 'Master'
    }

    EVIL_LABELS: Dict[int, str] = {
        1: 'Random',
        2: 'Corruption',
        3: 'Crimson'
    }

    DELETE_MODE_LABELS: Dict[int, str] = {
        0: 'Keep all worlds',
        1: 'Delete worlds without pyramids'
    }

    # ==================== Default Values ====================
    DEFAULT_SIZE = 2          # Medium
    DEFAULT_DIFFICULTY = 1    # Normal
    DEFAULT_EVIL = 1          # Random
    DEFAULT_COUNT = 1
    DEFAULT_DELETE_MODE = 0   # Keep all
    DEFAULT_PYRAMID_TARGET = 1
    DEFAULT_MAX_ATTEMPTS = 100

    # ==================== Validation Methods ====================
    @staticmethod
    def validate_size(value: int) -> int:
        """
        Validate world size parameter.

        Args:
            value: Size value to validate

        Returns:
            Validated size value

        Raises:
            ValueError: If value is out of range
        """
        if not (WorldConfig.SIZE_RANGE[0] <= value <= WorldConfig.SIZE_RANGE[1]):
            raise ValueError(
                f"Size must be between {WorldConfig.SIZE_RANGE[0]} and {WorldConfig.SIZE_RANGE[1]} "
                f"(1=Small, 2=Medium, 3=Large)"
            )
        return value

    @staticmethod
    def validate_difficulty(value: int) -> int:
        """
        Validate difficulty parameter.

        Args:
            value: Difficulty value to validate

        Returns:
            Validated difficulty value

        Raises:
            ValueError: If value is out of range
        """
        if not (WorldConfig.DIFFICULTY_RANGE[0] <= value <= WorldConfig.DIFFICULTY_RANGE[1]):
            raise ValueError(
                f"Difficulty must be between {WorldConfig.DIFFICULTY_RANGE[0]} "
                f"and {WorldConfig.DIFFICULTY_RANGE[1]} "
                f"(1=Normal, 2=Expert, 3=Master)"
            )
        return value

    @staticmethod
    def validate_evil(value: int) -> int:
        """
        Validate evil type parameter.

        Args:
            value: Evil type value to validate

        Returns:
            Validated evil type value

        Raises:
            ValueError: If value is out of range
        """
        if not (WorldConfig.EVIL_RANGE[0] <= value <= WorldConfig.EVIL_RANGE[1]):
            raise ValueError(
                f"Evil type must be between {WorldConfig.EVIL_RANGE[0]} "
                f"and {WorldConfig.EVIL_RANGE[1]} "
                f"(1=Random, 2=Corruption, 3=Crimson)"
            )
        return value

    @staticmethod
    def validate_count(value: int) -> int:
        """
        Validate world count parameter.

        Args:
            value: Count value to validate

        Returns:
            Validated count value

        Raises:
            ValueError: If value is out of range
        """
        if not (WorldConfig.COUNT_RANGE[0] <= value <= WorldConfig.COUNT_RANGE[1]):
            raise ValueError(
                f"Count must be between {WorldConfig.COUNT_RANGE[0]} "
                f"and {WorldConfig.COUNT_RANGE[1]}"
            )
        return value

    @staticmethod
    def validate_pyramid_target(value: int) -> int:
        """
        Validate pyramid target parameter.

        Args:
            value: Pyramid target value to validate

        Returns:
            Validated pyramid target value

        Raises:
            ValueError: If value is out of range
        """
        if not (WorldConfig.PYRAMID_TARGET_RANGE[0] <= value <= WorldConfig.PYRAMID_TARGET_RANGE[1]):
            raise ValueError(
                f"Pyramid target must be between {WorldConfig.PYRAMID_TARGET_RANGE[0]} "
                f"and {WorldConfig.PYRAMID_TARGET_RANGE[1]}"
            )
        return value

    @staticmethod
    def validate_max_attempts(value: int) -> int:
        """
        Validate max attempts parameter.

        Args:
            value: Max attempts value to validate

        Returns:
            Validated max attempts value

        Raises:
            ValueError: If value is out of range
        """
        if not (WorldConfig.MAX_ATTEMPTS_RANGE[0] <= value <= WorldConfig.MAX_ATTEMPTS_RANGE[1]):
            raise ValueError(
                f"Max attempts must be between {WorldConfig.MAX_ATTEMPTS_RANGE[0]} "
                f"and {WorldConfig.MAX_ATTEMPTS_RANGE[1]}"
            )
        return value

    @staticmethod
    def validate_delete_mode(value: int) -> int:
        """
        Validate delete mode parameter.

        Args:
            value: Delete mode value to validate

        Returns:
            Validated delete mode value

        Raises:
            ValueError: If value is invalid
        """
        if value not in (0, 1):
            raise ValueError("Delete mode must be 0 (keep all) or 1 (delete non-pyramid)")
        return value

    @staticmethod
    def get_size_label(value: int) -> str:
        """Get display label for size value."""
        return WorldConfig.SIZE_LABELS.get(value, f"Unknown ({value})")

    @staticmethod
    def get_difficulty_label(value: int) -> str:
        """Get display label for difficulty value."""
        return WorldConfig.DIFFICULTY_LABELS.get(value, f"Unknown ({value})")

    @staticmethod
    def get_evil_label(value: int) -> str:
        """Get display label for evil type value."""
        return WorldConfig.EVIL_LABELS.get(value, f"Unknown ({value})")

    @staticmethod
    def get_delete_mode_label(value: int) -> str:
        """Get display label for delete mode value."""
        return WorldConfig.DELETE_MODE_LABELS.get(value, f"Unknown ({value})")


class TileConfig:
    """Tile-related configuration."""

    # Sandstone Brick tile ID (pyramid indicator)
    SANDSTONE_BRICK_TILE_ID = 151

    # Minimum sandstone bricks to consider a valid pyramid
    MIN_PYRAMID_BLOCKS = 1  # At least 1 block to count as pyramid


class PathConfig:
    """Default paths for different platforms (can be overridden)."""

    # These are defined in platform layer, but defaults can be specified here
    WORLD_FILE_EXTENSION = ".wld"
    TEMP_WORLD_FILE_EXTENSION = ".twld"
