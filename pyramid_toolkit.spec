# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Terraria Pyramid Toolkit GUI

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
        ('pyramid_toolkit', 'pyramid_toolkit'),
        ('requirements.txt', '.'),
        ('LICENSE', '.'),
        ('README.md', '.'),
    ],
    hiddenimports=[
        'pyramid_toolkit',
        'pyramid_toolkit.core',
        'pyramid_toolkit.core.config',
        'pyramid_toolkit.core.models',
        'pyramid_toolkit.core.strategies',
        'pyramid_toolkit.core.pyramid_toolkit',
        'pyramid_toolkit.core.orchestrator',
        'pyramid_toolkit.platform',
        'pyramid_toolkit.platform.base',
        'pyramid_toolkit.platform.unix',
        'pyramid_toolkit.platform.windows',
        'pyramid_toolkit.platform.factory',
        'pyramid_toolkit.gui',
        'pyramid_toolkit.gui.app',
        'lihzahrd',
        'tkinter',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'pyramid_toolkit.cli',  # Exclude CLI if you only want GUI
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
            'CFBundleName': 'Pyramid Toolkit',
            'CFBundleDisplayName': 'Terraria Pyramid Toolkit',
            'CFBundleVersion': '2.0.0',
            'CFBundleShortVersionString': '2.0.0',
        },
    )
