# Terraria Pyramid Detector

Automatically detect pyramids (Sandstone Brick) in Terraria worlds with both GUI and command-line interfaces.

## Features

- **🖥️ Graphical User Interface**: Easy-to-use Tkinter GUI with real-time output
- **Automatic World Generation**: Batch generate Terraria worlds
- **Pyramid Detection**: Scan world files for Sandstone Brick (tile ID: 151)
- **Parameter Validation**: Built-in validation prevents illegal values
- **Cross-Platform**: Supports macOS, Linux, and Windows (native PowerShell support, no WSL required)

## Files

### GUI Application

- **gui.py** - Tkinter GUI application (recommended way to use)
- **gui_validators.py** - Parameter validation framework

### Main Scripts

**Bash Scripts (macOS/Linux):**
1. **auto_pyramid_finder.sh** - Automated pyramid finder
   - Generate worlds → Detect pyramids → Optional delete
   - Display statistics (success rate, etc.)

2. **find_pyramid_worlds.sh** - Target-based world finder
   - Generate until finding X pyramid worlds
   - Auto-delete non-pyramid worlds

3. **tWorldGen.sh** - Batch world generator
   - Only generates worlds, no detection

**PowerShell Scripts (Windows):**
1. **auto_pyramid_finder.ps1** - Windows version of auto pyramid finder
2. **find_pyramid_worlds.ps1** - Windows version of target-based finder
3. **tWorldGen.ps1** - Windows version of batch generator

**Python Tools:**
- **check_and_rename.py** - Check a single world file
- **scan_existing_worlds.sh** - Scan all existing worlds for pyramids

### Parsers

- **correct_parser.py** - Most complete Terraria 1.4.4.9 world file parser
- **main_fixed.py** - Simplified binary parser
- **main.py** / **lihzahrd_parser.py** - Parser using lihzahrd library
- **sandstone_finder.py** - Simple byte pattern scanner

## Quick Start

### GUI (Recommended - All Platforms)

Simply run the GUI application:

```bash
# macOS/Linux
python3 gui.py

# Windows
python gui.py
```

The GUI automatically detects your platform and uses the correct scripts (bash on Unix, PowerShell on Windows).

## Usage

### GUI Usage

1. Launch `gui.py`
2. Select script mode (Auto Pyramid Finder / Find Pyramid Worlds / World Generator)
3. Set parameters using dropdowns and spinboxes (all validated)
4. Click "Start Generation"
5. View real-time output in the log window
6. Click "Open World Directory" to see generated worlds

### Command-Line Usage

### 1. Auto-find Pyramid Worlds

**macOS/Linux:**
```bash
./auto_pyramid_finder.sh [SIZE] [DIFFICULTY] [EVIL] [COUNT] [DELETE_NO_PYRAMID]
```

**Windows (PowerShell):**
```powershell
.\auto_pyramid_finder.ps1 [SIZE] [DIFFICULTY] [EVIL] [COUNT] [DELETE_NO_PYRAMID]
```

Parameters:
- `SIZE`: World size (1=Small, 2=Medium, 3=Large, default: 2)
- `DIFFICULTY`: Difficulty (1=Normal, 2=Expert, 3=Master, default: 1)
- `EVIL`: Evil type (1=Random, 2=Corruption, 3=Crimson, default: 1)
- `COUNT`: Number of worlds to generate, max 200 (default: 1)
- `DELETE_NO_PYRAMID`: Delete non-pyramid worlds (0=Keep, 1=Delete, default: 0)

Examples:
```bash
# macOS/Linux - Generate 10 medium worlds, keep all
./auto_pyramid_finder.sh 2 1 1 10 0

# Windows - Generate 5 large worlds, delete non-pyramid worlds
.\auto_pyramid_finder.ps1 3 1 1 5 1
```

### 2. Check Single World File

```bash
python3 check_and_rename.py <world_file.wld> [--verbose]
```

Example:
```bash
python3 check_and_rename.py ~/Library/Application\ Support/Terraria/Worlds/MyWorld.wld
```

### 3. Generate Worlds Only (No Detection)

**macOS/Linux:**
```bash
./tWorldGen.sh [SIZE] [DIFFICULTY] [EVIL] [COUNT]
```

**Windows (PowerShell):**
```powershell
.\tWorldGen.ps1 [SIZE] [DIFFICULTY] [EVIL] [COUNT]
```

## Configuration

### Auto-Detection

Scripts automatically detect TerrariaServer and world directory locations:

**macOS:**
- TerrariaServer: `~/Library/Application Support/Steam/steamapps/common/Terraria/Terraria.app/Contents/MacOS/TerrariaServer`
- World directory: `~/Library/Application Support/Terraria/Worlds`

**Linux:**
- TerrariaServer: `~/.local/share/Steam/steamapps/common/Terraria/TerrariaServer.bin.x86_64`
- World directory: `~/.local/share/Terraria/Worlds`

**Windows:**
- TerrariaServer: `C:/Program Files (x86)/Steam/steamapps/common/Terraria/TerrariaServer.exe`
- World directory: `~/Documents/My Games/Terraria/Worlds`

### Custom Paths

If auto-detection fails, use environment variables:

**macOS/Linux:**
```bash
# Set TerrariaServer path
export TERRARIA_SERVER_PATH="/your/custom/path/to/TerrariaServer"

# Set world directory
export TERRARIA_WORLD_DIR="/your/custom/worlds/directory"

# Then run the script
./auto_pyramid_finder.sh 2 1 1 5
```

**Windows (PowerShell):**
```powershell
# Set TerrariaServer path
$env:TERRARIA_SERVER_PATH = "C:\Path\To\TerrariaServer.exe"

# Set world directory
$env:TERRARIA_WORLD_DIR = "C:\Path\To\Worlds"

# Then run the script
.\auto_pyramid_finder.ps1 2 1 1 5
```

Or edit the script files directly to modify `TERRARIA_SERVER` and `WORLD_DIR` variables.

### Windows PowerShell Execution Policy

If you get an execution policy error on Windows, run PowerShell as Administrator and execute:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Or run scripts with bypass (GUI does this automatically):
```powershell
powershell -ExecutionPolicy Bypass -File .\auto_pyramid_finder.ps1
```

## Example Output

```
=========================================
Terraria Pyramid World Finder
=========================================
World Size: Medium
Difficulty: Normal
Evil Type: Random
Count: 5
=========================================

[1/5] Generating world...
✓ Generated: World_20231225_120000_1.wld (2.5MiB)
  Checking for pyramids...
  🎉 PYRAMID FOUND! X=1234, Y=567
  ✓ Renamed to: 1 World_20231225_120000_1.wld

[2/5] Generating world...
✓ Generated: World_20231225_120030_2.wld (2.6MiB)
  Checking for pyramids...
  ○ No pyramid found in this world

...

=========================================
Batch generation complete!
Total worlds generated: 5
Pyramids found: 2
Success rate: 40%
World directory: ~/Library/Application Support/Terraria/Worlds
=========================================
```

## Requirements

### All Platforms
- **Python 3.6+** with Tkinter (usually included)
- **Terraria 1.4.4.9** (including TerrariaServer)
- **lihzahrd** library: `pip install lihzahrd`

### Platform-Specific
- **macOS/Linux**: Bash (pre-installed)
- **Windows**: PowerShell 5.0+ (pre-installed on Windows 7+)

### Optional
- For command-line scripts on Windows without GUI: No additional requirements
- For command-line scripts on macOS/Linux: Bash (pre-installed)

## How It Works

1. **World Generation**: Uses TerrariaServer's auto-create feature to batch generate worlds
2. **File Parsing**: Reads .wld binary files and parses tile data
3. **Pyramid Detection**: Searches for tile ID 151 (Sandstone Brick)
4. **Auto-Rename**: Adds "1 " prefix to filename for easy identification

## Technical Details

- Parser supports Terraria 1.4.4.9 world file format
- Properly handles RLE (Run-Length Encoding) compression
- Reads tiles in column-first order (x then y)
- Handles multi-byte tile IDs and UV coordinates for important tiles

## License

This project is for educational and personal use only.

## Contributing

Issues and Pull Requests are welcome!
