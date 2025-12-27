"""
Platform factory for automatic platform detection.

This module provides a factory function to automatically detect
the current platform and return the appropriate adapter.
"""

import platform

from .base import PlatformAdapter
from .unix import UnixPlatform
from .windows import WindowsPlatform


def get_platform_adapter() -> PlatformAdapter:
    """
    Automatically detect platform and return appropriate adapter.

    Returns:
        PlatformAdapter instance for the current platform

    Raises:
        RuntimeError: If platform is not supported

    Examples:
        >>> platform = get_platform_adapter()
        >>> print(f"Using platform: {platform.get_platform_name()}")
    """
    system = platform.system()

    if system == 'Windows':
        return WindowsPlatform()
    elif system in ('Darwin', 'Linux'):
        return UnixPlatform()
    else:
        raise RuntimeError(
            f"Unsupported platform: {system}. "
            f"Supported platforms: Windows, macOS (Darwin), Linux"
        )


def get_platform_name() -> str:
    """
    Get human-readable platform name without creating adapter.

    Returns:
        Platform name (e.g., "Windows", "macOS", "Linux")
    """
    system = platform.system()

    if system == 'Darwin':
        return 'macOS'
    elif system == 'Linux':
        return 'Linux'
    elif system == 'Windows':
        return 'Windows'
    else:
        return f"Unknown ({system})"
