#!/usr/bin/env python3
"""
Terraria Pyramid Detector GUI
Main graphical user interface for pyramid world generation
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import subprocess
import threading
import os
import sys

from gui_validators import VALIDATORS, SCRIPT_CONFIGS, ParameterValidator, ChoiceValidator


class PyramidDetectorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Terraria Pyramid Detector")
        self.root.geometry("900x750")
        self.root.resizable(True, True)

        # State
        self.current_script = 'auto_pyramid_finder'
        self.process = None
        self.is_running = False
        self.param_widgets = {}  # Store references to parameter input widgets
        self.common_param_widgets = {}  # Store common parameter widgets

        # Get script directory for executing shell scripts
        self.script_dir = os.path.dirname(os.path.abspath(__file__))

        # Build UI
        self.create_widgets()
        self.update_parameter_panel()
        self.update_button_states()

    def create_widgets(self):
        """Build all GUI components"""

        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights for resizing
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)

        current_row = 0

        # === Script Selection Section ===
        script_frame = ttk.LabelFrame(main_frame, text="Script Selection", padding="10")
        script_frame.grid(row=current_row, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        current_row += 1

        self.script_var = tk.StringVar(value='auto_pyramid_finder')

        for script_id, config in SCRIPT_CONFIGS.items():
            rb = ttk.Radiobutton(
                script_frame,
                text=config['name'],
                variable=self.script_var,
                value=script_id,
                command=self.on_script_change
            )
            rb.pack(anchor=tk.W, pady=2)

            # Add description label
            desc_label = ttk.Label(
                script_frame,
                text=f"  {config['description']}",
                font=('TkDefaultFont', 9),
                foreground='gray'
            )
            desc_label.pack(anchor=tk.W, padx=20)

        # === Common Parameters Section ===
        common_frame = ttk.LabelFrame(main_frame, text="Common Parameters", padding="10")
        common_frame.grid(row=current_row, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        current_row += 1

        # SIZE
        ttk.Label(common_frame, text="World Size:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.size_combo = ttk.Combobox(common_frame, state='readonly', width=15)
        size_validator = VALIDATORS['SIZE']
        self.size_combo['values'] = size_validator.get_labels()
        self.size_combo.current(list(size_validator.choices.keys()).index(size_validator.default))
        self.size_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        self.common_param_widgets['SIZE'] = self.size_combo

        # DIFFICULTY
        ttk.Label(common_frame, text="Difficulty:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.difficulty_combo = ttk.Combobox(common_frame, state='readonly', width=15)
        diff_validator = VALIDATORS['DIFFICULTY']
        self.difficulty_combo['values'] = diff_validator.get_labels()
        self.difficulty_combo.current(list(diff_validator.choices.keys()).index(diff_validator.default))
        self.difficulty_combo.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        self.common_param_widgets['DIFFICULTY'] = self.difficulty_combo

        # EVIL
        ttk.Label(common_frame, text="Evil Type:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.evil_combo = ttk.Combobox(common_frame, state='readonly', width=15)
        evil_validator = VALIDATORS['EVIL']
        self.evil_combo['values'] = evil_validator.get_labels()
        self.evil_combo.current(list(evil_validator.choices.keys()).index(evil_validator.default))
        self.evil_combo.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        self.common_param_widgets['EVIL'] = self.evil_combo

        # === Script-Specific Parameters Section ===
        self.param_frame = ttk.LabelFrame(main_frame, text="Script Parameters", padding="10")
        self.param_frame.grid(row=current_row, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        self.param_frame.columnconfigure(1, weight=1)
        current_row += 1

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

    def update_parameter_panel(self):
        """Rebuild parameter inputs based on selected script"""
        # Clear existing widgets
        for widget in self.param_frame.winfo_children():
            widget.destroy()
        self.param_widgets.clear()

        # Get parameters for current script
        params = SCRIPT_CONFIGS[self.current_script]['parameters']

        row = 0
        for param_name in params:
            if param_name in ['SIZE', 'DIFFICULTY', 'EVIL']:
                # Already in common section, skip
                continue

            validator = VALIDATORS[param_name]

            # Create label
            label = ttk.Label(self.param_frame, text=f"{param_name.replace('_', ' ').title()}:")
            label.grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)

            # Create input widget based on validator type
            if isinstance(validator, ChoiceValidator):
                self.create_choice_widget(param_name, validator, row)
            else:
                self.create_numeric_widget(param_name, validator, row)

            row += 1

    def create_choice_widget(self, param_name, validator, row):
        """Create dropdown for choice parameter"""
        combo = ttk.Combobox(self.param_frame, state='readonly', width=30)
        combo['values'] = validator.get_labels()
        combo.current(list(validator.choices.keys()).index(validator.default))
        combo.grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)

        self.param_widgets[param_name] = combo

    def create_numeric_widget(self, param_name, validator, row):
        """Create validated numeric input with spinbox"""
        # Validation command
        vcmd = (self.root.register(self.validate_numeric_input), '%P', param_name)

        spinbox = ttk.Spinbox(
            self.param_frame,
            from_=validator.min_val,
            to=validator.max_val,
            validate='key',
            validatecommand=vcmd,
            width=15
        )
        spinbox.set(validator.default)
        spinbox.grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)

        self.param_widgets[param_name] = spinbox

        # Add help text
        help_label = ttk.Label(
            self.param_frame,
            text=validator.description,
            font=('TkDefaultFont', 8),
            foreground='gray'
        )
        help_label.grid(row=row, column=2, sticky=tk.W, padx=10)

    def validate_numeric_input(self, value, param_name):
        """Real-time input validation for numeric fields"""
        if value == "":
            return True

        try:
            validator = VALIDATORS[param_name]
            val = int(value)
            return validator.min_val <= val <= validator.max_val
        except:
            return False

    def get_parameter_value(self, param_name):
        """Get current value of a parameter"""
        if param_name in self.common_param_widgets:
            # Common parameter (combobox)
            widget = self.common_param_widgets[param_name]
            validator = VALIDATORS[param_name]
            label = widget.get()
            # Find value for this label
            for val, lbl in validator.choices.items():
                if lbl == label:
                    return val
        elif param_name in self.param_widgets:
            # Script-specific parameter
            widget = self.param_widgets[param_name]
            validator = VALIDATORS[param_name]

            if isinstance(validator, ChoiceValidator):
                # Combobox
                label = widget.get()
                for val, lbl in validator.choices.items():
                    if lbl == label:
                        return val
            else:
                # Spinbox
                return widget.get()

        return None

    def validate_all_parameters(self):
        """Validate all current parameters before execution"""
        try:
            params = []
            for param_name in SCRIPT_CONFIGS[self.current_script]['parameters']:
                validator = VALIDATORS[param_name]
                value = self.get_parameter_value(param_name)
                validated = validator.validate(value)
                params.append(str(validated))
            return params
        except ValueError as e:
            messagebox.showerror("Validation Error", str(e))
            return None

    def on_script_change(self):
        """Handle script selection change"""
        self.current_script = self.script_var.get()
        self.update_parameter_panel()
        self.update_status(f"Switched to: {SCRIPT_CONFIGS[self.current_script]['name']}")

    def start_generation(self):
        """Start world generation in background thread"""
        params = self.validate_all_parameters()
        if params is None:
            return

        self.is_running = True
        self.update_button_states()
        self.clear_output()
        self.update_status("Starting generation...")

        # Run script in background thread
        thread = threading.Thread(target=self._run_script, args=(params,), daemon=True)
        thread.start()

    def _run_script(self, params):
        """Execute script and stream output to GUI"""
        script_path = SCRIPT_CONFIGS[self.current_script]['script']
        script_full_path = os.path.join(self.script_dir, script_path)

        # Detect platform and build appropriate command
        import platform
        system = platform.system()

        if system == 'Windows':
            # On Windows, run PowerShell script
            cmd = ['powershell.exe', '-ExecutionPolicy', 'Bypass', '-File', script_full_path] + params
        else:
            # On Unix (macOS/Linux), run bash script
            cmd = [script_full_path] + params

        try:
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                cwd=self.script_dir
            )

            # Stream output line by line
            for line in iter(self.process.stdout.readline, ''):
                if line:
                    self.append_output(line)

            self.process.wait()
            self.on_completion(self.process.returncode)

        except FileNotFoundError:
            self.append_output(f"Error: Script not found: {script_full_path}\n")
            self.append_output("Please ensure all shell scripts are in the same directory as gui.py\n")
            self.update_status("Error: Script not found")
        except Exception as e:
            self.append_output(f"Error: {e}\n")
            self.update_status(f"Error: {e}")
        finally:
            self.is_running = False
            self.root.after(0, self.update_button_states)

    def append_output(self, text):
        """Thread-safe output append"""
        self.root.after(0, self._append_output_impl, text)

    def _append_output_impl(self, text):
        """Actual output append (must run in main thread)"""
        self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)

    def clear_output(self):
        """Clear output log"""
        self.output_text.delete(1.0, tk.END)

    def on_completion(self, return_code):
        """Handle script completion"""
        if return_code == 0:
            self.append_output("\n✓ Generation completed successfully!\n")
            self.update_status("Completed successfully")
        else:
            self.append_output(f"\n✗ Generation failed with exit code {return_code}\n")
            self.update_status(f"Failed with exit code {return_code}")

    def stop_generation(self):
        """Stop running generation"""
        if self.process and self.is_running:
            self.process.terminate()
            self.append_output("\n[STOPPED BY USER]\n")
            self.update_status("Stopped by user")
            self.is_running = False
            self.update_button_states()

    def open_world_directory(self):
        """Open world directory in file manager"""
        # Try macOS path
        world_dir = os.path.expanduser("~/Library/Application Support/Terraria/Worlds")

        if not os.path.exists(world_dir):
            # Try Linux path
            world_dir = os.path.expanduser("~/.local/share/Terraria/Worlds")

        if not os.path.exists(world_dir):
            # Try Windows path
            world_dir = os.path.expanduser("~/Documents/My Games/Terraria/Worlds")

        if os.path.exists(world_dir):
            # Open directory based on platform
            import platform
            system = platform.system()

            try:
                if system == 'Darwin':  # macOS
                    subprocess.Popen(['open', world_dir])
                elif system == 'Linux':
                    subprocess.Popen(['xdg-open', world_dir])
                elif system == 'Windows':
                    subprocess.Popen(['explorer', world_dir])
                else:
                    messagebox.showinfo("World Directory", f"World directory:\n{world_dir}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not open directory:\n{e}")
        else:
            messagebox.showwarning(
                "Directory Not Found",
                "Could not find Terraria world directory.\n"
                "Please ensure Terraria is installed."
            )

    def update_button_states(self):
        """Update button states based on running status"""
        if self.is_running:
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
        else:
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)

    def update_status(self, message):
        """Update status bar message"""
        self.status_var.set(message)


def main():
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
