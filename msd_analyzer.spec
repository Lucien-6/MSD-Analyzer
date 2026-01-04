# -*- mode: python ; coding: utf-8 -*-
# MSD Analyzer V1.6 - PyInstaller Configuration
# Author: Lucien
# Date: 2026-01-04

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['F:\\Codes\\MSD Analyzer'],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# 排除测试数据文件夹（减小打包体积）
a.datas = [x for x in a.datas if not x[0].startswith('test_data')]
a.binaries = [x for x in a.binaries if not x[0].startswith('test_data')]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,       # 添加二进制文件
    a.zipfiles,       # 添加压缩文件
    a.datas,          # 添加数据文件
    [],
    name='MSD Analyzer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,         # 启用UPX压缩
    upx_exclude=[],   # UPX排除列表
    upx_dir='F:\\Codes\\UPX',  # UPX可执行文件路径
    runtime_tmpdir=None,
    console=False,    # 禁用控制台窗口，仅显示GUI界面
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',  # 应用图标（V1.5）
)