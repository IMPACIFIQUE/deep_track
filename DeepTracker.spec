# -*- mode: python ; coding: utf-8 -*-
import os
import sys

from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs


datas = collect_data_files("customtkinter")
datas += [("assets", "assets")]
binaries = collect_dynamic_libs("PIL")
python_root = sys.base_prefix
tcl_root = os.path.join(python_root, "tcl")
dll_root = os.path.join(python_root, "DLLs")
datas += [
    (os.path.join(tcl_root, "tcl8.6"), "tcl/tcl8.6"),
    (os.path.join(tcl_root, "tk8.6"), "tcl/tk8.6"),
]
binaries += [
    (os.path.join(dll_root, "tcl86t.dll"), "."),
    (os.path.join(dll_root, "tk86t.dll"), "."),
]

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=["pyi_rth_tk_paths.py"],
    excludes=["pytest", "tkinter.test"],
    noarchive=False,
    optimize=1,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="DeepTracker",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="assets/icons/app.ico",
)
collect = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="DeepTracker",
)
