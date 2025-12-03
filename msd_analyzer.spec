# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['E:\\Codes\\MSD Analyzer'],
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

# 排除测试数据生成脚本和测试数据文件夹
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
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,  # 添加临时目录设置
    console=False,  # 禁用控制台窗口，仅显示GUI界面
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',  # 添加应用图标
)