# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Terraria Pyramid Detector GUI

This file configures how PyInstaller packages the application.
"""

import sys
import os
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

# Determine platform-specific settings
if sys.platform == 'darwin':  # macOS
    icon_file = None  # Add your .icns file path here if you have one
    console = False
elif sys.platform == 'win32':  # Windows
    icon_file = None  # Add your .ico file path here if you have one
    console = False
else:  # Linux
    icon_file = None
    console = False

a = Analysis(
    ['run_gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('pyramid_detector', 'pyramid_detector'),
        ('requirements.txt', '.'),
        ('LICENSE', '.'),
        ('README.md', '.'),
    ],
    hiddenimports=[
        'pyramid_detector',
        'pyramid_detector.core',
        'pyramid_detector.core.config',
        'pyramid_detector.core.models',
        'pyramid_detector.core.strategies',
        'pyramid_detector.core.pyramid_detector',
        'pyramid_detector.core.orchestrator',
        'pyramid_detector.platform',
        'pyramid_detector.platform.base',
        'pyramid_detector.platform.unix',
        'pyramid_detector.platform.windows',
        'pyramid_detector.platform.factory',
        'pyramid_detector.gui',
        'pyramid_detector.gui.app',
        'lihzahrd',
        'tkinter',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'pyramid_detector.cli',  # Exclude CLI if you only want GUI
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='PyramidDetector',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=console,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_file,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='PyramidDetector',
)

# macOS app bundle
if sys.platform == 'darwin':
    app = BUNDLE(
        coll,
        name='PyramidDetector.app',
        icon=icon_file,
        bundle_identifier='com.pyramiddetector.app',
        info_plist={
            'NSPrincipalClass': 'NSApplication',
            'NSHighResolutionCapable': 'True',
            'CFBundleName': 'Pyramid Detector',
            'CFBundleDisplayName': 'Terraria Pyramid Detector',
            'CFBundleVersion': '2.0.0',
            'CFBundleShortVersionString': '2.0.0',
        },
    )
