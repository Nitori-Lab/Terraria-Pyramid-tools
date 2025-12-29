"""
Core business logic for Terraria Pyramid Toolkit.

This package contains platform-agnostic business logic including:
- Configuration and validation rules
- Data models
- Generation strategies
- Pyramid detection
- Flow orchestration

All modules in this package are independent of platform-specific
implementation details.
"""

from .config import WorldConfig, TileConfig, PathConfig
from .models import (
    WorldGenerationParams,
    PyramidDetectionResult,
    WorldGenerationResult,
    GenerationStatistics
)
from .strategies import (
    GenerationStrategy,
    FixedCountStrategy,
    TargetPyramidStrategy,
    BasicGenerationStrategy,
    create_strategy
)
from .pyramid_detector import PyramidDetector
from .orchestrator import GenerationOrchestrator

__all__ = [
    # Configuration
    'WorldConfig',
    'TileConfig',
    'PathConfig',

    # Models
    'WorldGenerationParams',
    'PyramidDetectionResult',
    'WorldGenerationResult',
    'GenerationStatistics',

    # Strategies
    'GenerationStrategy',
    'FixedCountStrategy',
    'TargetPyramidStrategy',
    'BasicGenerationStrategy',
    'create_strategy',

    # Core functionality
    'PyramidDetector',
    'GenerationOrchestrator',
]

__version__ = '1.0.0'
