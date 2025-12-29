"""
Unix (macOS/Linux) platform implementation.

This module implements platform-specific operations for Unix-like systems.
"""

import os
import subprocess
import time
import tempfile
import platform as platform_module
from pathlib import Path
from typing import Optional

from .base import PlatformAdapter
from ..core.models import WorldGenerationParams


class UnixPlatform(PlatformAdapter):
    """
    Platform adapter for Unix-like systems (macOS and Linux).

    Handles TerrariaServer interaction using bash commands.
    """

    def __init__(self):
        """Initialize Unix platform adapter."""
        self.terraria_server = None
        self.world_directory = None
        self._detect_paths()

    def _detect_paths(self):
        """Auto-detect TerrariaServer and world directory paths."""
        self.terraria_server = self.find_terraria_server()
        self.world_directory = self.find_world_directory()

    def find_terraria_server(self) -> Optional[str]:
        """Find TerrariaServer executable on Unix systems."""
        # Check environment variable first
        if os.environ.get('TERRARIA_SERVER_PATH'):
            path = os.environ['TERRARIA_SERVER_PATH']
            if os.path.isfile(path):
                return path

        # Detect OS
        system = platform_module.system()

        if system == 'Darwin':  # macOS
            possible_paths = [
                os.path.expanduser(
                    "~/Library/Application Support/Steam/steamapps/common/Terraria/"
                    "Terraria.app/Contents/MacOS/TerrariaServer"
                ),
                "/Applications/Terraria.app/Contents/MacOS/TerrariaServer",
            ]
        elif system == 'Linux':
            possible_paths = [
                os.path.expanduser(
                    "~/.local/share/Steam/steamapps/common/Terraria/TerrariaServer.bin.x86_64"
                ),
                os.path.expanduser(
                    "~/.steam/steam/steamapps/common/Terraria/TerrariaServer.bin.x86_64"
                ),
            ]
        else:
            return None

        # Find first existing path
        for path in possible_paths:
            if os.path.isfile(path):
                return path

        return None

    def find_world_directory(self) -> Optional[str]:
        """Find Terraria world directory on Unix systems."""
        # Check environment variable first
        if os.environ.get('TERRARIA_WORLD_DIR'):
            return os.environ['TERRARIA_WORLD_DIR']

        # Detect OS
        system = platform_module.system()

        if system == 'Darwin':  # macOS
            return os.path.expanduser("~/Library/Application Support/Terraria/Worlds")
        elif system == 'Linux':
            return os.path.expanduser("~/.local/share/Terraria/Worlds")
        else:
            return None

    def get_world_directory(self) -> str:
        """Get world directory, use detected or raise error."""
        if self.world_directory:
            return self.world_directory

        raise RuntimeError(
            "World directory not found. Please set TERRARIA_WORLD_DIR environment variable."
        )

    def generate_world(self, params: WorldGenerationParams) -> Optional[Path]:
        """
        Generate world using TerrariaServer on Unix.

        Args:
            params: World generation parameters

        Returns:
            Path to generated world file, or None if failed
        """
        if not self.terraria_server:
            raise RuntimeError(
                "TerrariaServer not found. Please install Terraria or set "
                "TERRARIA_SERVER_PATH environment variable."
            )

        # Ensure world directory exists
        world_dir = self.ensure_world_directory_exists()
        world_path = world_dir / f"{params.world_name}.wld"

        # Count files before generation
        before_files = len(list(world_dir.glob("*.wld")))

        # Create temporary input file for TerrariaServer
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            input_file = f.name
            # Write commands for TerrariaServer
            f.write("n\n")                      # Create new world
            f.write(f"{params.size}\n")         # World size
            f.write(f"{params.difficulty}\n")   # Difficulty
            f.write(f"{params.evil}\n")         # Evil type
            f.write(f"{params.world_name}\n")   # World name
            f.write("\n")                       # Seed (blank for random)
            f.write("exit\n")                   # Exit

        try:
            # Run TerrariaServer
            with open(input_file, 'r') as stdin_file:
                process = subprocess.Popen(
                    [self.terraria_server],
                    stdin=stdin_file,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )

                # Wait for world file to be created (max 5 minutes)
                max_wait = 300  # seconds
                wait_time = 0
                world_created = False

                while wait_time < max_wait:
                    time.sleep(2)
                    wait_time += 2

                    # Check if new world file appeared
                    after_files = len(list(world_dir.glob("*.wld")))
                    if after_files > before_files:
                        world_created = True
                        break

                # Kill TerrariaServer process
                try:
                    process.terminate()
                    time.sleep(1)
                    process.kill()
                except:
                    pass

                # Kill any remaining TerrariaServer processes
                self.kill_terraria_server()

                # Wait for filesystem sync
                time.sleep(1)

                # Find the generated world file
                if world_path.exists() and world_path.stat().st_size > 0:
                    return world_path
                else:
                    # Try to find most recently created world
                    worlds = sorted(
                        world_dir.glob("*.wld"),
                        key=lambda p: p.stat().st_mtime,
                        reverse=True
                    )
                    if worlds and len(worlds) > before_files:
                        return worlds[0]

                return None

        finally:
            # Clean up temp file
            try:
                os.unlink(input_file)
            except:
                pass

    def delete_world(self, world_path: Path) -> bool:
        """Delete world file and associated .twld file."""
        try:
            # Delete .wld file
            if world_path.exists():
                world_path.unlink()

            # Delete .twld file if exists
            twld_path = world_path.with_suffix('.twld')
            if twld_path.exists():
                twld_path.unlink()

            return True

        except Exception:
            return False

    def open_directory(self, path: str) -> bool:
        """Open directory in file manager on Unix."""
        try:
            system = platform_module.system()

            if system == 'Darwin':  # macOS
                subprocess.Popen(['open', path])
            elif system == 'Linux':
                subprocess.Popen(['xdg-open', path])
            else:
                return False

            return True

        except Exception:
            return False

    def kill_terraria_server(self) -> bool:
        """Kill all TerrariaServer processes (not the game client)."""
        try:
            # Only kill TerrariaServer, not Terraria game
            subprocess.run(
                ['pkill', '-9', '-f', 'TerrariaServer'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return True

        except Exception:
            return False
