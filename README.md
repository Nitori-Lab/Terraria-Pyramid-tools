# Terraria Pyramid Detector

Automatically detect pyramids (Sandstone Brick) in Terraria worlds and rename world files containing pyramids.

## Features

- **Automatic World Generation**: Batch generate Terraria worlds
- **Pyramid Detection**: Scan world files for Sandstone Brick (tile ID: 151)
- **Auto-Rename**: Add "1 " prefix to world files containing pyramids
- **Cross-Platform**: Supports macOS, Linux, and Windows

## Files

### Main Scripts

1. **auto_pyramid_finder.sh** - Automated pyramid finder
   - Generate worlds → Detect pyramids → Auto-rename
   - Display statistics (success rate, etc.)

2. **tWorldGen.sh** - Batch world generator
   - Only generates worlds, no detection

3. **check_and_rename.py** - Python check and rename tool
   - Check a single world file
   - Rename if pyramid found

### Parsers

- **correct_parser.py** - Most complete Terraria 1.4.4.9 world file parser
- **main_fixed.py** - Simplified binary parser
- **main.py** / **lihzahrd_parser.py** - Parser using lihzahrd library
- **sandstone_finder.py** - Simple byte pattern scanner

## Usage

### 1. Auto-find Pyramid Worlds (Recommended)

```bash
./auto_pyramid_finder.sh [SIZE] [DIFFICULTY] [EVIL] [COUNT]
```

Parameters:
- `SIZE`: World size (1=Small, 2=Medium, 3=Large, default: 2)
- `DIFFICULTY`: Difficulty (1=Normal, 2=Expert, 3=Master, default: 1)
- `EVIL`: Evil type (1=Random, 2=Corruption, 3=Crimson, default: 1)
- `COUNT`: Number of worlds to generate, max 200 (default: 1)

Examples:
```bash
# Generate 10 medium-sized normal difficulty worlds with random evil
./auto_pyramid_finder.sh 2 1 1 10

# Generate 5 large worlds
./auto_pyramid_finder.sh 3 1 1 5
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

```bash
./tWorldGen.sh [SIZE] [DIFFICULTY] [EVIL] [COUNT]
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

```bash
# Set TerrariaServer path
export TERRARIA_SERVER_PATH="/your/custom/path/to/TerrariaServer"

# Set world directory
export TERRARIA_WORLD_DIR="/your/custom/worlds/directory"

# Then run the script
./auto_pyramid_finder.sh 2 1 1 5
```

Or edit the script files directly to modify `TERRARIA_SERVER` and `WORLD_DIR` variables.

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

- **Bash** (built-in on macOS/Linux, requires Git Bash or WSL on Windows)
- **Python 3.6+**
- **Terraria 1.4.4.9** (including TerrariaServer)

No additional Python libraries needed (`correct_parser.py` uses only standard library).

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
