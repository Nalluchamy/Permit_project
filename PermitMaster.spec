# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_data_files

ctk_datas = collect_data_files('customtkinter')

bundled_files = ['permit_icon.ico', 'ad_dd_signature.png', 'permits.db']
existing_datas = [(f, '.') for f in bundled_files if os.path.exists(f)]

a = Analysis(
    ['permit_master_source.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('pdf_generator/template.html', 'pdf_generator'),
    ] + existing_datas + ctk_datas,
    hiddenimports=['qrcode.image.svg'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='PermitMaster',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='permit_icon.ico' if os.path.exists('permit_icon.ico') else None,
)
