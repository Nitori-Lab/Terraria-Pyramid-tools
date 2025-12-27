"""
Command-line interface for Terraria Pyramid Detector.

This package provides Click-based CLI commands for all generation modes.

Usage:
    python -m pyramid_detector.cli auto-find --count 10
    pyramid-detector auto-find --count 10  # If installed
"""

from .main import cli

__all__ = ['cli']
