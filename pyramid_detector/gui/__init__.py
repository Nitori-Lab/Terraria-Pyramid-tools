"""
Graphical user interface for Terraria Pyramid Detector.

This package provides a Tkinter-based GUI using the new core architecture.

Usage:
    python -m pyramid_detector.gui
    pyramid-gui  # If installed
"""

from .app import PyramidDetectorGUI, main

__all__ = ['PyramidDetectorGUI', 'main']
