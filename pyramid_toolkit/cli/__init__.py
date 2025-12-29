"""
Command-line interface for Terraria Pyramid Toolkit.

This package provides Click-based CLI commands for all generation modes.

Usage:
    python -m pyramid_toolkit.cli auto-find --count 10
    pyramid-toolkit auto-find --count 10  # If installed
"""

from .main import cli

__all__ = ['cli']
