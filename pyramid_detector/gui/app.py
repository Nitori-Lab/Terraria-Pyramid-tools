"""
Terraria Pyramid Detector GUI Application.

This module provides a Tkinter-based graphical interface using the
new core architecture.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading

from ..core import (
    WorldConfig,
    WorldGenerationParams,
    GenerationOrchestrator,
    create_strategy,
)
from ..platform import get_platform_adapter, get_platform_name


class PyramidDetectorGUI:
    """Main GUI application for Terraria Pyramid Detector."""

    def __init__(self, root):
        """Initialize GUI application."""
        self.root = root
        self.root.title("Terraria Pyramid Detector (v2.0)")
        self.root.geometry("900x750")
        self.root.resizable(True, True)

        # State
        self.is_running = False
        self.orchestrator = None
        self.current_mode = 'fixed'

        # Create platform adapter
        try:
            self.platform = get_platform_adapter()
            platform_name = get_platform_name()
        except Exception as e:
            messagebox.showerror("Platform Error", f"Failed to initialize platform: {e}")
            self.platform = None
            platform_name = "Unknown"

        # Build UI
        self.create_widgets()
        self.update_button_states()

        # Show platform info
        self.log(f"Platform: {platform_name}")
        self.log(f"Terraria Pyramid Detector v2.0")
        self.log("")

    def create_widgets(self):
        """Build all GUI components."""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)

        current_row = 0

        # === Mode Selection ===
        mode_frame = ttk.LabelFrame(main_frame, text="Generation Mode", padding="10")
        mode_frame.grid(row=current_row, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        current_row += 1

        self.mode_var = tk.StringVar(value='fixed')

        modes = [
            ('fixed', 'Auto Pyramid Finder', 'Generate fixed number of worlds'),
            ('target', 'Find Pyramid Worlds', 'Find specific number of pyramids'),
            ('basic', 'World Generator', 'Generate without detection')
        ]

        for mode_id, name, desc in modes:
            rb = ttk.Radiobutton(
                mode_frame,
                text=name,
                variable=self.mode_var,
                value=mode_id,
                command=self.on_mode_change
            )
            rb.pack(anchor=tk.W, pady=2)

            desc_label = ttk.Label(
                mode_frame,
                text=f"  {desc}",
                font=('TkDefaultFont', 9),
                foreground='gray'
            )
            desc_label.pack(anchor=tk.W, padx=20)

        # === Parameters ===
        param_frame = ttk.LabelFrame(main_frame, text="Parameters", padding="10")
        param_frame.grid(row=current_row, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        current_row += 1

        # Size
        ttk.Label(param_frame, text="World Size:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.size_combo = ttk.Combobox(param_frame, state='readonly', width=15)
        self.size_combo['values'] = ['Small', 'Medium', 'Large']
        self.size_combo.current(1)  # Default: Medium
        self.size_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

        # Difficulty
        ttk.Label(param_frame, text="Difficulty:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.difficulty_combo = ttk.Combobox(param_frame, state='readonly', width=15)
        self.difficulty_combo['values'] = ['Normal', 'Expert', 'Master']
        self.difficulty_combo.current(0)  # Default: Normal
        self.difficulty_combo.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

        # Evil
        ttk.Label(param_frame, text="Evil Type:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.evil_combo = ttk.Combobox(param_frame, state='readonly', width=15)
        self.evil_combo['values'] = ['Random', 'Corruption', 'Crimson']
        self.evil_combo.current(0)  # Default: Random
        self.evil_combo.grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)

        # Count (for fixed/basic modes)
        ttk.Label(param_frame, text="Count:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.count_spinbox = ttk.Spinbox(param_frame, from_=1, to=200, width=15)
        self.count_spinbox.set(5)
        self.count_spinbox.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)

        # Delete mode checkbox
        self.delete_var = tk.BooleanVar(value=False)
        self.delete_check = ttk.Checkbutton(
            param_frame,
            text="Delete worlds without pyramids",
            variable=self.delete_var
        )
        self.delete_check.grid(row=4, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)

        # === Control Buttons ===
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=current_row, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        current_row += 1

        self.start_button = ttk.Button(
            button_frame,
            text="Start Generation",
            command=self.start_generation
        )
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = ttk.Button(
            button_frame,
            text="Stop",
            command=self.stop_generation,
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)

        self.open_dir_button = ttk.Button(
            button_frame,
            text="Open World Directory",
            command=self.open_world_directory
        )
        self.open_dir_button.pack(side=tk.LEFT, padx=5)

        self.clear_button = ttk.Button(
            button_frame,
            text="Clear Log",
            command=self.clear_output
        )
        self.clear_button.pack(side=tk.LEFT, padx=5)

        # === Output Log ===
        output_frame = ttk.LabelFrame(main_frame, text="Output Log", padding="5")
        output_frame.grid(row=current_row, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        main_frame.rowconfigure(current_row, weight=1)
        current_row += 1

        self.output_text = scrolledtext.ScrolledText(
            output_frame,
            wrap=tk.WORD,
            height=20,
            font=('Courier', 10)
        )
        self.output_text.pack(fill=tk.BOTH, expand=True)

        # === Status Bar ===
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(
            main_frame,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        status_bar.grid(row=current_row, column=0, sticky=(tk.W, tk.E))

    def on_mode_change(self):
        """Handle mode selection change."""
        self.current_mode = self.mode_var.get()
        # Update UI based on mode (could hide/show relevant controls)

    def get_parameters(self):
        """Get and validate current parameters."""
        try:
            # Get values from UI
            size_label = self.size_combo.get()
            difficulty_label = self.difficulty_combo.get()
            evil_label = self.evil_combo.get()

            # Map to values
            size = list(WorldConfig.SIZE_LABELS.keys())[
                list(WorldConfig.SIZE_LABELS.values()).index(size_label)
            ]
            difficulty = list(WorldConfig.DIFFICULTY_LABELS.keys())[
                list(WorldConfig.DIFFICULTY_LABELS.values()).index(difficulty_label)
            ]
            evil = list(WorldConfig.EVIL_LABELS.keys())[
                list(WorldConfig.EVIL_LABELS.values()).index(evil_label)
            ]

            count = int(self.count_spinbox.get())
            delete_mode = 1 if self.delete_var.get() else 0

            # Validate using core config
            size = WorldConfig.validate_size(size)
            difficulty = WorldConfig.validate_difficulty(difficulty)
            evil = WorldConfig.validate_evil(evil)
            count = WorldConfig.validate_count(count)

            return size, difficulty, evil, count, delete_mode

        except ValueError as e:
            messagebox.showerror("Validation Error", str(e))
            return None

    def start_generation(self):
        """Start world generation in background thread."""
        if self.platform is None:
            messagebox.showerror("Error", "Platform not initialized")
            return

        params = self.get_parameters()
        if params is None:
            return

        size, difficulty, evil, count, delete_mode = params

        self.is_running = True
        self.update_button_states()
        self.clear_output()
        self.update_status("Starting generation...")

        # Run in background thread
        thread = threading.Thread(
            target=self._run_generation,
            args=(size, difficulty, evil, count, delete_mode),
            daemon=True
        )
        thread.start()

    def _run_generation(self, size, difficulty, evil, count, delete_mode):
        """Execute generation in background thread."""
        try:
            # Create orchestrator
            orchestrator = GenerationOrchestrator(
                platform=self.platform,
                progress_callback=self.log
            )

            # Create base params
            base_params = WorldGenerationParams(
                size=size,
                difficulty=difficulty,
                evil=evil,
                world_name="temp"  # Will be replaced
            )

            # Create strategy based on mode
            if self.current_mode == 'fixed':
                strategy = create_strategy(
                    'fixed',
                    total_count=count,
                    delete_mode=delete_mode
                )
            elif self.current_mode == 'target':
                strategy = create_strategy(
                    'target',
                    pyramid_target=count,  # Reuse count field
                    max_attempts=100
                )
            else:  # basic
                strategy = create_strategy(
                    'basic',
                    total_count=count
                )

            # Execute
            results, stats = orchestrator.execute_strategy(base_params, strategy)

            self.log("")
            self.log("✓ Generation completed!")
            self.update_status("Completed")

        except Exception as e:
            self.log(f"\n✗ Error: {e}")
            self.update_status(f"Error: {e}")

        finally:
            self.is_running = False
            self.root.after(0, self.update_button_states)

    def stop_generation(self):
        """Stop running generation."""
        # TODO: Implement graceful shutdown
        self.log("\n[STOP requested - will finish current world]")
        self.is_running = False
        self.update_button_states()

    def open_world_directory(self):
        """Open world directory in file manager."""
        if self.platform:
            try:
                world_dir = self.platform.get_world_directory()
                self.platform.open_directory(world_dir)
            except Exception as e:
                messagebox.showerror("Error", f"Could not open directory:\n{e}")
        else:
            messagebox.showerror("Error", "Platform not initialized")

    def log(self, message):
        """Thread-safe log message."""
        self.root.after(0, self._log_impl, message)

    def _log_impl(self, message):
        """Actual log implementation (must run in main thread)."""
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.see(tk.END)

    def clear_output(self):
        """Clear output log."""
        self.output_text.delete(1.0, tk.END)

    def update_button_states(self):
        """Update button states based on running status."""
        if self.is_running:
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
        else:
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)

    def update_status(self, message):
        """Update status bar message."""
        self.status_var.set(message)


def main():
    """Main entry point for GUI application."""
    root = tk.Tk()
    app = PyramidDetectorGUI(root)

    # Center window on screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')

    root.mainloop()


if __name__ == "__main__":
    main()
