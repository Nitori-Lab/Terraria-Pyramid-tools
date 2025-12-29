@echo off
REM Build script for Terraria Pyramid Detector GUI (Windows)

echo ===================================
echo Pyramid Detector GUI Builder
echo ===================================
echo.

REM Check if PyInstaller is installed
where pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: PyInstaller is not installed
    echo Installing PyInstaller...
    pip install pyinstaller
)

REM Clean previous builds
echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Build the application
echo.
echo Building GUI application...
pyinstaller pyramid_detector.spec --clean

if %errorlevel% equ 0 (
    echo.
    echo ===================================
    echo Build successful!
    echo ===================================
    echo.
    echo Executable created at: dist\PyramidDetector\PyramidDetector.exe
    echo.
    echo To run the app:
    echo   dist\PyramidDetector\PyramidDetector.exe
    echo.
    echo To create a desktop shortcut:
    echo   Right-click PyramidDetector.exe and select "Create shortcut"
    echo   Move the shortcut to your Desktop
) else (
    echo.
    echo ===================================
    echo Build failed!
    echo ===================================
    exit /b 1
)

pause
