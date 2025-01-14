# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from PyInstaller.utils.hooks import collect_all

block_cipher = None

# 收集所有相关的包
datas = []
binaries = []
hiddenimports = []
tmp_ret = collect_all('tkinter')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('moviepy')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

a = Analysis(
    [r'D:\2048\caj\pythonProject\VIP.py'],
    pathex=[r'D:\2048\caj\pythonProject'],
    binaries=[('D:\\\\RJ\\\\Anaconda3\\\\envs\\\\py311\\\\Library\\\\bin\\\\libcrypto-1_1-x64.dll', '.'), ('D:\\\\RJ\\\\Anaconda3\\\\envs\\\\py311\\\\Library\\\\bin\\\\libssl-1_1-x64.dll', '.'), ('D:\\\\RJ\\\\Anaconda3\\\\envs\\\\py311\\\\Library\\\\bin\\\\liblzma.dll', '.'), ('D:\\\\RJ\\\\Anaconda3\\\\envs\\\\py311\\\\Library\\\\bin\\\\ffi.dll', '.'), ('D:\\\\RJ\\\\Anaconda3\\\\envs\\\\py311\\\\DLLs\\\\_tkinter.pyd', '.'), ('D:\\\\RJ\\\\Anaconda3\\\\envs\\\\py311\\\\DLLs\\\\_ctypes.pyd', '.')],
    datas=[('C:\\\\Users\\\\18558\\\\Downloads\\\\视频.ico', '.'), ('D:\\\\RJ\\\\Anaconda3\\\\envs\\\\py311\\\\python3.dll', '.'), ('D:\\\\RJ\\\\Anaconda3\\\\envs\\\\py311\\\\python311.dll', '.')],
    hiddenimports=['tkinter.filedialog', 'numpy', 'moviepy.video.fx.all', 'ctypes', 'proglog', '_ctypes', 'tkinter', 'tkinter.messagebox', 'PIL.ImageTk', 'PIL.Image', 'tkinter.ttk', 'PIL', 'cv2', 'moviepy.audio.fx.all', 'numpy.core._multiarray_umath'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# 添加额外的DLL搜索路径
a.datas += Tree(r'D:\RJ\Anaconda3\envs\py311\Library\bin', prefix='.')

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='VIP视频解析工具',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=r'C:\Users\18558\Downloads\视频.ico',
)
