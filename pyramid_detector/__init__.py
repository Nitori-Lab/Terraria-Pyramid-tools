"""
Terraria Pyramid Detector

A cross-platform tool for automatically generating Terraria worlds
and detecting pyramids (Sandstone Brick structures).

Features:
- Platform-agnostic core logic
- Multiple generation strategies
- GUI and CLI interfaces
- Automatic pyramid detection using lihzahrd

Usage:
    # Using the orchestrator directly
    from pyramid_detector.platform.factory import get_platform_adapter
    from pyramid_detector.core import (
        GenerationOrchestrator,
        WorldGenerationParams,
        create_strategy
    )

    platform = get_platform_adapter()
    orchestrator = GenerationOrchestrator(platform)

    params = WorldGenerationParams(size=2, difficulty=1, evil=1, world_name="Test")
    strategy = create_strategy('fixed', total_count=5, delete_mode=0)

    results, stats = orchestrator.execute_strategy(params, strategy)

    # Using CLI
    $ pyramid-detector auto-find --size 2 --count 10

    # Using GUI
    $ pyramid-gui
"""

from .core import (
    WorldConfig,
    TileConfig,
    WorldGenerationParams,
    PyramidDetectionResult,
    WorldGenerationResult,
    GenerationStatistics,
    GenerationStrategy,
    create_strategy,
    PyramidDetector,
    GenerationOrchestrator,
)

__version__ = '1.0.0'
__author__ = 'Pyramid Detector Contributors'
__license__ = 'MIT'

__all__ = [
    # Core classes
    'WorldConfig',
    'TileConfig',
    'WorldGenerationParams',
    'PyramidDetectionResult',
    'WorldGenerationResult',
    'GenerationStatistics',
    'GenerationStrategy',
    'PyramidDetector',
    'GenerationOrchestrator',

    # Utilities
    'create_strategy',

    # Metadata
    '__version__',
]
