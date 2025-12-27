# Terraria Pyramid Detector

Automatically detect pyramids in Terraria worlds with GUI and CLI support.

## Features

- **GUI Interface** - Simple graphical interface for world generation
- **CLI Interface** - Command-line tool for automation
- **Cross-Platform** - Works on Windows, macOS, and Linux
- **Multiple Modes** - Generate fixed count, find pyramids, or generate without detection

## Quick Start

### Installation

```bash
git clone https://github.com/yourusername/pyramidDetector.git
cd pyramidDetector
pip install -r requirements.txt
```

### GUI (Recommended)

```bash
python -m pyramid_detector.gui
```

### CLI Examples

```bash
# Generate 10 worlds and detect pyramids
python -m pyramid_detector.cli auto-find --count 10

# Find 5 pyramid worlds
python -m pyramid_detector.cli find-pyramids --target 5

# See all options
python -m pyramid_detector.cli --help
```

## CLI Usage

### Auto-find Mode
Generate a fixed number of worlds:
```bash
python -m pyramid_detector.cli auto-find [OPTIONS]

Options:
  --size, -s INTEGER       World size (1=Small, 2=Medium, 3=Large) [default: 2]
  --difficulty, -d INTEGER Difficulty (1=Normal, 2=Expert, 3=Master) [default: 1]
  --evil, -e INTEGER       Evil type (1=Random, 2=Corruption, 3=Crimson) [default: 1]
  --count, -c INTEGER      Number of worlds to generate [default: 1]
  --delete/--no-delete     Delete non-pyramid worlds [default: no-delete]
```

### Find-pyramids Mode
Generate until finding pyramid worlds:
```bash
python -m pyramid_detector.cli find-pyramids [OPTIONS]

Options:
  --target, -t INTEGER        Number of pyramid worlds to find [default: 1]
  --max-attempts, -m INTEGER  Maximum worlds to generate [default: 100]
```

### Generate Mode
Generate worlds without detection:
```bash
python -m pyramid_detector.cli generate --count 5
```

## Configuration

### TerrariaServer Path

Set custom TerrariaServer path:
```bash
# macOS/Linux
export TERRARIA_SERVER_PATH="/path/to/TerrariaServer"

# Windows
set TERRARIA_SERVER_PATH=C:\Path\To\TerrariaServer.exe
```

### Auto-detected Paths

**macOS:**
- TerrariaServer: `~/Library/Application Support/Steam/steamapps/common/Terraria/Terraria.app/Contents/MacOS/TerrariaServer`
- Worlds: `~/Library/Application Support/Terraria/Worlds`

**Linux:**
- TerrariaServer: `~/.local/share/Steam/steamapps/common/Terraria/TerrariaServer.bin.x86_64`
- Worlds: `~/.local/share/Terraria/Worlds`

**Windows:**
- TerrariaServer: `C:\Program Files (x86)\Steam\steamapps\common\Terraria\TerrariaServer.exe`
- Worlds: `%USERPROFILE%\Documents\My Games\Terraria\Worlds`

## Requirements

- Python 3.6+
- Terraria 1.4.4.9 with TerrariaServer
- Dependencies: `pip install -r requirements.txt`

## Project Structure

```
pyramid_detector/
├── core/          # Business logic
├── platform/      # OS-specific implementations
├── cli/           # Command-line interface
└── gui/           # Graphical interface
```

## Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) - Architecture details
- [CHANGELOG.md](CHANGELOG.md) - Version history

## License

MIT License - see [LICENSE](LICENSE) for details.
