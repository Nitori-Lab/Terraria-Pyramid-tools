"""
World generation strategies (platform-agnostic business logic).

This module defines different strategies for world generation,
such as fixed-count generation or target-based generation.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from .config import WorldConfig
from .models import GenerationStatistics


class GenerationStrategy(ABC):
    """
    Abstract base class for world generation strategies.

    A strategy defines:
    - When to stop generating worlds
    - Whether to delete worlds without pyramids
    - How to report progress
    """

    @abstractmethod
    def should_continue(self, stats: GenerationStatistics) -> bool:
        """
        Determine if generation should continue.

        Args:
            stats: Current generation statistics

        Returns:
            True if generation should continue, False otherwise
        """
        pass

    @abstractmethod
    def should_delete_non_pyramid(self) -> bool:
        """
        Determine if worlds without pyramids should be deleted.

        Returns:
            True if non-pyramid worlds should be deleted
        """
        pass

    @abstractmethod
    def get_progress_message(self, stats: GenerationStatistics) -> str:
        """
        Get progress message for current state.

        Args:
            stats: Current generation statistics

        Returns:
            Progress message string
        """
        pass

    @abstractmethod
    def get_completion_message(self, stats: GenerationStatistics) -> str:
        """
        Get completion message after generation finishes.

        Args:
            stats: Final generation statistics

        Returns:
            Completion message string
        """
        pass


@dataclass
class FixedCountStrategy(GenerationStrategy):
    """
    Strategy: Generate a fixed number of worlds.

    This strategy generates exactly `total_count` worlds, optionally
    deleting worlds without pyramids based on `delete_mode`.

    Attributes:
        total_count: Total number of worlds to generate
        delete_mode: Whether to delete worlds without pyramids (0=keep, 1=delete)
    """
    total_count: int
    delete_mode: int = 0

    def __post_init__(self):
        """Validate parameters."""
        self.total_count = WorldConfig.validate_count(self.total_count)
        self.delete_mode = WorldConfig.validate_delete_mode(self.delete_mode)

    def should_continue(self, stats: GenerationStatistics) -> bool:
        """Continue until total_count worlds are generated."""
        return stats.total_generated < self.total_count

    def should_delete_non_pyramid(self) -> bool:
        """Delete based on delete_mode setting."""
        return self.delete_mode == 1

    def get_progress_message(self, stats: GenerationStatistics) -> str:
        """Show progress: [current/total]."""
        return f"[{stats.total_generated + 1}/{self.total_count}] Generating world..."

    def get_completion_message(self, stats: GenerationStatistics) -> str:
        """Show completion statistics."""
        success_rate = stats.success_rate
        delete_info = f", deleted {stats.worlds_deleted}" if self.delete_mode else ""

        return (f"Batch generation complete!\n"
                f"Total worlds generated: {stats.total_generated}\n"
                f"Pyramids found: {stats.pyramids_found}\n"
                f"Success rate: {success_rate:.1f}%{delete_info}\n"
                f"Time elapsed: {stats.total_time:.1f}s")


@dataclass
class TargetPyramidStrategy(GenerationStrategy):
    """
    Strategy: Generate worlds until finding target number of pyramids.

    This strategy continues generating worlds until either:
    1. Target number of pyramid worlds is reached, or
    2. Maximum attempts is reached

    Non-pyramid worlds are always deleted in this mode.

    Attributes:
        pyramid_target: Number of pyramid worlds to find
        max_attempts: Maximum worlds to generate before giving up
    """
    pyramid_target: int
    max_attempts: int = 100

    def __post_init__(self):
        """Validate parameters."""
        self.pyramid_target = WorldConfig.validate_pyramid_target(self.pyramid_target)
        self.max_attempts = WorldConfig.validate_max_attempts(self.max_attempts)

    def should_continue(self, stats: GenerationStatistics) -> bool:
        """
        Continue until target is reached or max attempts exceeded.

        Args:
            stats: Current statistics

        Returns:
            True if should continue generating
        """
        target_not_reached = stats.pyramids_found < self.pyramid_target
        attempts_remaining = stats.total_generated < self.max_attempts

        return target_not_reached and attempts_remaining

    def should_delete_non_pyramid(self) -> bool:
        """Always delete non-pyramid worlds in target mode."""
        return True

    def get_progress_message(self, stats: GenerationStatistics) -> str:
        """Show progress with remaining pyramids needed."""
        remaining = self.pyramid_target - stats.pyramids_found
        current = stats.total_generated + 1

        return (f"[{current}/{self.max_attempts}] Generating world "
                f"(need {remaining} more pyramid{'s' if remaining != 1 else ''})...")

    def get_completion_message(self, stats: GenerationStatistics) -> str:
        """Show completion with target achievement status."""
        success_rate = stats.success_rate
        target_reached = stats.pyramids_found >= self.pyramid_target

        if target_reached:
            status = f"✓ Target reached! Found {stats.pyramids_found}/{self.pyramid_target} pyramids"
        else:
            status = (f"⚠ Max attempts reached. "
                     f"Found {stats.pyramids_found}/{self.pyramid_target} pyramids")

        return (f"Search complete!\n"
                f"{status}\n"
                f"Total worlds generated: {stats.total_generated}\n"
                f"Success rate: {success_rate:.1f}%\n"
                f"Time elapsed: {stats.total_time:.1f}s")


@dataclass
class BasicGenerationStrategy(GenerationStrategy):
    """
    Strategy: Basic world generation without pyramid detection.

    This strategy simply generates worlds without checking for pyramids.
    Used by the tWorldGen mode.

    Attributes:
        total_count: Total number of worlds to generate
    """
    total_count: int

    def __post_init__(self):
        """Validate parameters."""
        self.total_count = WorldConfig.validate_count(self.total_count)

    def should_continue(self, stats: GenerationStatistics) -> bool:
        """Continue until total_count worlds are generated."""
        return stats.total_generated < self.total_count

    def should_delete_non_pyramid(self) -> bool:
        """Never delete in basic mode (no pyramid detection)."""
        return False

    def get_progress_message(self, stats: GenerationStatistics) -> str:
        """Show simple progress counter."""
        return f"[{stats.total_generated + 1}/{self.total_count}] Generating world..."

    def get_completion_message(self, stats: GenerationStatistics) -> str:
        """Show simple completion message."""
        avg_time = stats.average_time_per_world

        return (f"Batch generation complete!\n"
                f"Total worlds generated: {stats.total_generated}\n"
                f"Average time per world: {avg_time:.1f}s\n"
                f"Total time: {stats.total_time:.1f}s")


def create_strategy(mode: str, **kwargs) -> GenerationStrategy:
    """
    Factory function to create generation strategies.

    Args:
        mode: Strategy mode ('fixed', 'target', or 'basic')
        **kwargs: Strategy-specific parameters

    Returns:
        Appropriate GenerationStrategy instance

    Raises:
        ValueError: If mode is unknown or parameters are invalid

    Examples:
        >>> strategy = create_strategy('fixed', total_count=10, delete_mode=1)
        >>> strategy = create_strategy('target', pyramid_target=5, max_attempts=50)
        >>> strategy = create_strategy('basic', total_count=5)
    """
    if mode == 'fixed':
        return FixedCountStrategy(
            total_count=kwargs.get('total_count', WorldConfig.DEFAULT_COUNT),
            delete_mode=kwargs.get('delete_mode', WorldConfig.DEFAULT_DELETE_MODE)
        )
    elif mode == 'target':
        return TargetPyramidStrategy(
            pyramid_target=kwargs.get('pyramid_target', WorldConfig.DEFAULT_PYRAMID_TARGET),
            max_attempts=kwargs.get('max_attempts', WorldConfig.DEFAULT_MAX_ATTEMPTS)
        )
    elif mode == 'basic':
        return BasicGenerationStrategy(
            total_count=kwargs.get('total_count', WorldConfig.DEFAULT_COUNT)
        )
    else:
        raise ValueError(f"Unknown strategy mode: {mode}. "
                        f"Valid modes are: 'fixed', 'target', 'basic'")
