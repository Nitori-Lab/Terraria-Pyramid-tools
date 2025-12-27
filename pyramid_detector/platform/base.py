"""
Platform adapter abstract interface.

This module defines the contract that all platform-specific
implementations must follow.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from ..core.models import WorldGenerationParams


class PlatformAdapter(ABC):
    """
    Abstract base class for platform-specific operations.

    Platform adapters handle all OS-specific tasks such as:
    - Finding TerrariaServer executable
    - Finding world directory
    - Running TerrariaServer to generate worlds
    - Managing processes
    - Opening file manager

    All methods must be implemented by concrete platform classes.
    """

    @abstractmethod
    def find_terraria_server(self) -> Optional[str]:
        """
        Find TerrariaServer executable path.

        Returns:
            Path to TerrariaServer executable, or None if not found

        Note:
            Should check common locations and environment variables
        """
        pass

    @abstractmethod
    def find_world_directory(self) -> Optional[str]:
        """
        Find Terraria world save directory.

        Returns:
            Path to world directory, or None if not found

        Note:
            Should check common locations and environment variables
        """
        pass

    @abstractmethod
    def get_world_directory(self) -> str:
        """
        Get world directory (may create if doesn't exist).

        Returns:
            Path to world directory

        Raises:
            RuntimeError: If directory cannot be found or created
        """
        pass

    @abstractmethod
    def generate_world(self, params: WorldGenerationParams) -> Optional[Path]:
        """
        Generate a Terraria world using TerrariaServer.

        Args:
            params: World generation parameters

        Returns:
            Path to generated world file, or None if generation failed

        Note:
            This method should:
            1. Create input for TerrariaServer
            2. Run TerrariaServer process
            3. Wait for world file to be created
            4. Clean up TerrariaServer processes
            5. Return path to generated world
        """
        pass

    @abstractmethod
    def delete_world(self, world_path: Path) -> bool:
        """
        Delete a world file and its associated files.

        Args:
            world_path: Path to world file to delete

        Returns:
            True if deletion succeeded, False otherwise

        Note:
            Should also delete .twld file if it exists
        """
        pass

    @abstractmethod
    def open_directory(self, path: str) -> bool:
        """
        Open directory in system file manager.

        Args:
            path: Directory path to open

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    def kill_terraria_server(self) -> bool:
        """
        Kill all TerrariaServer processes.

        Returns:
            True if successful, False otherwise

        Note:
            Should NOT kill the game client, only TerrariaServer
        """
        pass

    # Helper methods with default implementations

    def ensure_world_directory_exists(self) -> Path:
        """
        Ensure world directory exists, create if needed.

        Returns:
            Path object for world directory

        Raises:
            RuntimeError: If directory cannot be created
        """
        world_dir = self.get_world_directory()
        world_path = Path(world_dir)

        if not world_path.exists():
            try:
                world_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                raise RuntimeError(f"Failed to create world directory: {e}")

        return world_path

    def get_platform_name(self) -> str:
        """
        Get human-readable platform name.

        Returns:
            Platform name (e.g., "Unix", "Windows")
        """
        return self.__class__.__name__.replace("Platform", "")
