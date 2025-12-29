"""
Entry point for running CLI as a module.

Usage:
    python -m pyramid_toolkit.cli --help
    python -m pyramid_toolkit.cli auto-find --count 5
"""

from .main import cli

if __name__ == '__main__':
    cli()
