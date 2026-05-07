# -*- mode: python ; coding: utf-8 -*-

import sys
import os

block_cipher = None

# Paths
ROOT_DIR = os.path.abspath(os.path.dirname(SPEC))
MAIN_SCRIPT = os.path.join(ROOT_DIR, 'starter', 'main.py')

# Dynamically find PySide6 path from sysconfig
import sysconfig
site_packages = sysconfig.get_paths()['purelib']
PYSIDE6_PATH = os.path.join(site_packages, 'PySide6')

a = Analysis(
    [MAIN_SCRIPT],
    pathex=[os.path.join(ROOT_DIR, 'starter')],
    binaries=[],
    datas=[
        # PySide6 plugins (needed for Qt PDF and Qt GUI)
        (os.path.join(PYSIDE6_PATH, 'plugins', 'platforms'), 'PySide6/plugins/platforms'),
        (os.path.join(PYSIDE6_PATH, 'plugins', 'styles'), 'PySide6/plugins/styles'),
        (os.path.join(PYSIDE6_PATH, 'plugins', 'imageformats'), 'PySide6/plugins/imageformats'),
        (os.path.join(PYSIDE6_PATH, 'plugins', 'iconengines'), 'PySide6/plugins/iconengines'),
        (os.path.join(PYSIDE6_PATH, 'translations'), 'PySide6/translations'),
        # App icon
        (os.path.join(ROOT_DIR, 'icon.ico'), 'icon.ico'),
    ],
    hiddenimports=[
        'PySide6',
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'PySide6.QtPdf',
        'PySide6.QtPdfWidgets',
        'fitz',
        'PyMuPDF',
    ],
    hookspath=[],
    hooksconfig={},
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
    name='PDF_Compare_Viewer_V2',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Windowed mode
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(ROOT_DIR, 'icon.ico'),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='PDF_Compare_Viewer_V2',
)
