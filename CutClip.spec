# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files

datas = [('assets', 'assets')]
binaries = []
ffmpeg_binary = 'tools/ffmpeg/ffmpeg.exe'
if Path(ffmpeg_binary).is_file():
    binaries.append((ffmpeg_binary, 'ffmpeg'))
datas += collect_data_files('customtkinter')

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=['pystray._win32', 'winotify'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=1,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='CutClip',
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
    icon=['assets/cutclip.ico'],
    version='version_info.txt',
)
