#!/usr/bin/env python3
"""
Terraria Pyramid Detector GUI Launcher

Simple entry point for launching the GUI application.
This script can be run directly or packaged with PyInstaller.
"""

import sys
import os


def main():
    """Launch the GUI application."""
    # Ensure the parent directory is in the Python path
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

    try:
        from pyramid_detector.gui.app import main as gui_main
        gui_main()
    except ImportError as e:
        print(f"Error: Failed to import pyramid_detector module: {e}")
        print(f"Current directory: {os.getcwd()}")
        print(f"Script directory: {parent_dir}")
        print(f"Python path: {sys.path}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: Failed to start GUI: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
