# inferno_app.spec
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

from PyInstaller.utils.hooks import collect_submodules
hiddenimports = collect_submodules('file_manager')

a = Analysis(
    [
        'main.py', 
        'pages/home/page.py', 
        'pages/metadata/page.py', 
        'pages/learn/page.py', 
        'pages/plotting/page.py',
        'pages/plotting/config.py',
        'pages/plotting/custom_combobox.py',
        'pages/plotting/prob_functions.py',
        'pages/plotting/plotting.py',
        'pages/plotting/variables.py', 
        'pages/mutualinfo/page.py',
        'pages/literature/page.py', 
        'r_integration/inferno_functions.py',
    ],
    pathex=['.'],
    binaries=[],
    datas=[
        ('icons/home.svg', 'icons'),
        ('icons/metadata.svg', 'icons'),
        ('icons/learn.svg', 'icons'),
        ('icons/plotting.svg', 'icons'),
        ('icons/mutualinfo.svg', 'icons'),
        ('icons/literature.svg', 'icons'),
        ('icons/inferno_image.png', 'icons'),
        ('icons/inferno_symbol.png', 'icons'),
        ('pages/metadata/styles.qss', 'pages/metadata'),
        ('pages/home/styles.qss', 'pages/home'),
        ('pages/learn/styles.qss', 'pages/learn'),
        ('pages/literature/styles.qss', 'pages/literature'),
        ('pages/plotting/styles.qss', 'pages/plotting'),
        ('pages/plotting/default_config.json', 'pages/plotting'),
        ('pages/mutualinfo/styles.qss', 'pages/mutualinfo'),
        ('pages/metadata/tooltips.json', 'pages/metadata'),
        ('pages/home/content/about.txt', 'pages/home/content'),
        ('pages/home/content/features.txt', 'pages/home/content')
    ],
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Inferno',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    icon='icons/inferno_symbol.ico'
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    name='inferno_app'
)