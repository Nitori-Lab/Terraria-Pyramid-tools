"""
Platform-specific implementations for Terraria Pyramid Detector.

This package contains platform adapters that handle OS-specific
operations such as running TerrariaServer and managing files.

Usage:
    from pyramid_detector.platform import get_platform_adapter

    platform = get_platform_adapter()
    world_path = platform.generate_world(params)
"""

from .base import PlatformAdapter
from .unix import UnixPlatform
from .windows import WindowsPlatform
from .factory import get_platform_adapter, get_platform_name

__all__ = [
    'PlatformAdapter',
    'UnixPlatform',
    'WindowsPlatform',
    'get_platform_adapter',
    'get_platform_name',
]
