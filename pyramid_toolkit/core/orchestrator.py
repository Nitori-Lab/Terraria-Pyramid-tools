"""
World generation orchestrator (platform-agnostic flow control).

This module orchestrates the world generation process by coordinating
between the platform layer (world generation) and core logic (pyramid detection).
"""

import time
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional, List

from .models import (
    WorldGenerationParams,
    WorldGenerationResult,
    GenerationStatistics
)
from .strategies import GenerationStrategy
from .pyramid_detector import PyramidDetector


class GenerationOrchestrator:
    """
    Orchestrates world generation and pyramid detection.

    This class coordinates the generation process without knowing
    platform-specific implementation details. It depends on abstractions
    (PlatformAdapter) provided through dependency injection.

    Attributes:
        platform: Platform adapter for world generation
        detector: Pyramid detector for world analysis
        progress_callback: Optional callback for progress updates
    """

    def __init__(
        self,
        platform,  # PlatformAdapter (abstract, defined in platform layer)
        detector: Optional[PyramidDetector] = None,
        progress_callback: Optional[Callable[[str], None]] = None
    ):
        """
        Initialize orchestrator with dependencies.

        Args:
            platform: Platform adapter implementing world generation
            detector: Pyramid detector (created if not provided)
            progress_callback: Optional callback for progress messages
        """
        self.platform = platform
        self.detector = detector or PyramidDetector()
        self.progress_callback = progress_callback

    def _log(self, message: str):
        """Log message via callback if available."""
        if self.progress_callback:
            self.progress_callback(message)

    def generate_single_world(
        self,
        params: WorldGenerationParams,
        detect_pyramid: bool = True
    ) -> WorldGenerationResult:
        """
        Generate a single world.

        Args:
            params: World generation parameters
            detect_pyramid: Whether to detect pyramid after generation

        Returns:
            WorldGenerationResult with generation outcome
        """
        start_time = time.time()

        try:
            # Call platform layer to generate world
            world_path = self.platform.generate_world(params)

            if world_path is None:
                return WorldGenerationResult(
                    params=params,
                    success=False,
                    error_message="Platform returned None for world path"
                )

            # Convert to Path object if needed
            if not isinstance(world_path, Path):
                world_path = Path(world_path)

            # Detect pyramid if requested
            pyramid_result = None
            if detect_pyramid:
                pyramid_result = self.detector.detect(world_path)

            generation_time = time.time() - start_time

            return WorldGenerationResult(
                params=params,
                world_path=world_path,
                success=True,
                pyramid_detection=pyramid_result,
                generation_time=generation_time
            )

        except Exception as e:
            generation_time = time.time() - start_time

            return WorldGenerationResult(
                params=params,
                success=False,
                error_message=f"Generation failed: {str(e)}",
                generation_time=generation_time
            )

    def execute_strategy(
        self,
        base_params: WorldGenerationParams,
        strategy: GenerationStrategy
    ) -> tuple:
        """
        Execute a generation strategy.

        Args:
            base_params: Base parameters for world generation
            strategy: Generation strategy to execute

        Returns:
            Tuple of (results_list, statistics)
        """
        stats = GenerationStatistics(start_time=datetime.now())
        results: List[WorldGenerationResult] = []

        self._log("Starting world generation...")
        self._log("")

        # Main generation loop
        while strategy.should_continue(stats):
            # Show progress
            progress_msg = strategy.get_progress_message(stats)
            self._log(progress_msg)

            # Create unique world name (timestamp + sequence)
            world_name = self._generate_world_name(
                sequence=stats.total_generated + 1,
                size=base_params.size,
                difficulty=base_params.difficulty,
                evil=base_params.evil
            )

            # Update params with new world name
            params = WorldGenerationParams(
                size=base_params.size,
                difficulty=base_params.difficulty,
                evil=base_params.evil,
                world_name=world_name
            )

            # Generate world (with pyramid detection for non-basic strategies)
            detect_pyramid = isinstance(strategy, GenerationStrategy)
            result = self.generate_single_world(params, detect_pyramid=detect_pyramid)

            if not result.success:
                self._log(f"✗ Generation failed: {result.error_message}")
                continue

            # Log world creation
            world_size_mb = self._get_file_size_mb(result.world_path)
            self._log(f"✓ Generated: {result.world_name}.wld ({world_size_mb:.2f}MB)")

            # Handle pyramid detection result
            if result.pyramid_detection:
                self._log("  Checking for pyramids...")
                pyramid_summary = self.detector.get_summary(result.pyramid_detection)
                self._log(f"  {pyramid_summary}")

                # Delete if needed
                if not result.has_pyramid and strategy.should_delete_non_pyramid():
                    self._log("  🗑️  Deleting world without pyramid...")
                    self.platform.delete_world(result.world_path)
                    result.deleted = True

            # Update statistics
            stats.add_result(result)

            # Keep result if not deleted
            if not result.deleted:
                results.append(result)

            self._log("")

        # Finalize statistics
        stats.end_time = datetime.now()

        # Show completion message
        completion_msg = strategy.get_completion_message(stats)
        self._log("=" * 50)
        self._log(completion_msg)

        # Show pyramid worlds if any
        if stats.pyramid_worlds:
            self._log("")
            self._log("Worlds with pyramids:")
            for world_name in stats.pyramid_worlds:
                self._log(f"  - {world_name}")

        self._log("")
        self._log(f"World directory: {self.platform.get_world_directory()}")
        self._log("=" * 50)

        return results, stats

    def _generate_world_name(self, sequence: int, size: int, difficulty: int, evil: int) -> str:
        """
        Generate unique world name with world settings and timestamp.

        Args:
            sequence: Sequence number for this world
            size: World size (1=Small, 2=Medium, 3=Large)
            difficulty: Difficulty level (1=Normal, 2=Expert, 3=Master, 4=Journey)
            evil: Evil biome type (1=Random, 2=Corruption, 3=Crimson)

        Returns:
            Unique world name in format: {size}_{difficulty}_{evil}_{timestamp}_{sequence}
        """
        # Size abbreviations
        size_abbr = {1: 's', 2: 'm', 3: 'l'}[size]

        # Difficulty abbreviations (empty for normal)
        difficulty_abbr = {1: '', 2: 'e', 3: 'm', 4: 'j'}[difficulty]

        # Evil type abbreviations
        evil_abbr = {1: 'rand', 2: 'corruption', 3: 'crimson'}[evil]

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Build name parts
        parts = [size_abbr]
        if difficulty_abbr:  # Only add difficulty if not normal
            parts.append(difficulty_abbr)
        parts.extend([evil_abbr, timestamp, str(sequence)])

        return '_'.join(parts)

    def _get_file_size_mb(self, file_path: Optional[Path]) -> float:
        """
        Get file size in megabytes.

        Args:
            file_path: Path to file

        Returns:
            File size in MB, or 0 if file doesn't exist
        """
        if file_path is None or not file_path.exists():
            return 0.0

        try:
            size_bytes = file_path.stat().st_size
            return size_bytes / (1024 * 1024)  # Convert to MB
        except Exception:
            return 0.0
