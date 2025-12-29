# Building Pyramid Detector GUI

This guide explains how to build standalone executables for Terraria Pyramid Detector GUI.

## Prerequisites

1. **Python 3.6+** installed
2. **PyInstaller** installed:
   ```bash
   pip install pyinstaller
   ```
3. **All dependencies** installed:
   ```bash
   pip install -r requirements.txt
   ```

## Building on macOS

```bash
# Make build script executable
chmod +x build.sh

# Run build
./build.sh
```

**Output:** `dist/PyramidDetector.app`

**To run:**
```bash
open dist/PyramidDetector.app
```

**To install:**
```bash
cp -r dist/PyramidDetector.app /Applications/
```

## Building on Windows

```batch
# Run build script
build.bat
```

**Output:** `dist\PyramidDetector\PyramidDetector.exe`

**To run:**
- Double-click `dist\PyramidDetector\PyramidDetector.exe`
- Or run from command line: `dist\PyramidDetector\PyramidDetector.exe`

**To create desktop shortcut:**
1. Navigate to `dist\PyramidDetector\`
2. Right-click `PyramidDetector.exe`
3. Select "Create shortcut"
4. Move shortcut to Desktop

## Building on Linux

```bash
# Make build scripts executable
chmod +x build.sh build_desktop_entry.sh

# Run build
./build.sh

# Create desktop entry (optional)
./build_desktop_entry.sh
```

**Output:** `dist/PyramidDetector/PyramidDetector`

**To run:**
```bash
./dist/PyramidDetector/PyramidDetector
```

**Desktop integration:**
The `build_desktop_entry.sh` script creates a `.desktop` file so the app appears in your applications menu.

## Manual Build

If the build scripts don't work, you can build manually:

```bash
# Clean previous builds
rm -rf build dist

# Build with PyInstaller
pyinstaller pyramid_detector.spec --clean
```

## Build Options

### One-File Build

To create a single executable file instead of a folder:

Edit `pyramid_detector.spec` and change:
```python
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,      # Add this
    a.zipfiles,      # Add this
    a.datas,         # Add this
    [],
    name='PyramidDetector',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
)

# Remove COLLECT section
```

Then rebuild:
```bash
./build.sh  # or build.bat on Windows
```

### Including CLI

To include the CLI tools in the build, edit `pyramid_detector.spec` and remove this line:
```python
excludes=['pyramid_detector.cli'],
```

### Custom Icon

To add a custom icon:

1. Create an icon file:
   - **macOS:** `.icns` file
   - **Windows:** `.ico` file
   - **Linux:** `.png` file (512x512 recommended)

2. Edit `pyramid_detector.spec`:
   ```python
   if sys.platform == 'darwin':
       icon_file = 'icon.icns'
   elif sys.platform == 'win32':
       icon_file = 'icon.ico'
   else:
       icon_file = 'icon.png'
   ```

3. Rebuild

## Distribution

### macOS

**Create DMG (recommended):**
```bash
# Install create-dmg
brew install create-dmg

# Create DMG
create-dmg \
  --volname "Pyramid Detector" \
  --window-pos 200 120 \
  --window-size 600 400 \
  --icon-size 100 \
  --icon "PyramidDetector.app" 175 120 \
  --app-drop-link 425 120 \
  "PyramidDetector-2.0.0-macOS.dmg" \
  "dist/PyramidDetector.app"
```

**Or create ZIP:**
```bash
cd dist
zip -r PyramidDetector-2.0.0-macOS.zip PyramidDetector.app
```

### Windows

**Create installer with Inno Setup (recommended):**
1. Install [Inno Setup](https://jrsoftware.org/isinfo.php)
2. Create `installer.iss` file (see example below)
3. Compile with Inno Setup

**Or create ZIP:**
```batch
cd dist
powershell Compress-Archive -Path PyramidDetector -DestinationPath PyramidDetector-2.0.0-Windows.zip
```

### Linux

**Create tarball:**
```bash
cd dist
tar -czf PyramidDetector-2.0.0-Linux.tar.gz PyramidDetector/
```

**Create AppImage (advanced):**
Use [appimage-builder](https://appimage-builder.readthedocs.io/)

## Troubleshooting

### "Module not found" errors

Add missing modules to `hiddenimports` in `pyramid_detector.spec`:
```python
hiddenimports=[
    'pyramid_detector',
    'your_missing_module',
],
```

### Large executable size

The executable includes Python and all dependencies. To reduce size:
- Use `upx=True` (already enabled)
- Exclude unused modules in `excludes`
- Use virtual environment with only required packages

### macOS security warning

On macOS, if you get "App can't be opened because it is from an unidentified developer":
1. Right-click the app
2. Select "Open"
3. Click "Open" in the dialog

Or disable Gatekeeper temporarily:
```bash
sudo spctl --master-disable
```

### Windows antivirus warning

PyInstaller executables may trigger antivirus warnings. This is a false positive. You can:
- Add exclusion to your antivirus
- Code-sign the executable (requires certificate)

## Platform-Specific Notes

### macOS

- Builds on Apple Silicon (M1/M2) create ARM64 executables
- Builds on Intel Macs create x86_64 executables
- For universal binary, build on both and use `lipo` to combine

### Windows

- Build on Windows for best compatibility
- Builds are typically larger due to DLLs
- Consider using UPX compression

### Linux

- Build on the oldest supported Linux version
- Use PyInstaller from pip, not system packages
- Desktop integration via `.desktop` files

## Automated Builds

For CI/CD, see `.github/workflows/build.yml` (if you create one).

Example GitHub Actions workflow:
```yaml
name: Build Executables

on: [push, pull_request]

jobs:
  build:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]

    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    - run: pip install -r requirements.txt pyinstaller
    - run: ./build.sh  # or build.bat on Windows
    - uses: actions/upload-artifact@v3
      with:
        name: PyramidDetector-${{ matrix.os }}
        path: dist/
```

## Support

If you encounter issues building, check:
1. PyInstaller version: `pyinstaller --version`
2. Python version: `python --version`
3. All dependencies installed: `pip list`
4. Check PyInstaller logs in `build/` folder

For more help, see [PyInstaller documentation](https://pyinstaller.readthedocs.io/).
