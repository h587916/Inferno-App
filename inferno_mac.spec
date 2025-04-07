# inferno_mac.spec
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

from PyInstaller.utils.hooks import collect_submodules
hiddenimports = collect_submodules('file_manager')

from PyInstaller.utils.hooks import collect_data_files
r_datas = collect_data_files('R', includes=['*'], subdir='Inferno.app/Contents/Resources/R')

datas=[
        ('resources/home.svg', 'resources'),
        ('resources/check.svg', 'resources'),
        ('resources/metadata.svg', 'resources'),
        ('resources/learn.svg', 'resources'),
        ('resources/plotting.svg', 'resources'),
        ('resources/mutualinfo.svg', 'resources'),
        ('resources/literature.svg', 'resources'),
        ('resources/inferno_image.png', 'resources'),
        ('resources/inferno_symbol.png', 'resources'),
        ('pages/shared/styles.qss', 'pages/shared'),
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
    ]

datas += r_datas

a = Analysis(
    [
        'main.py', 
        'pages/shared/custom_combobox.py',
        'pages/home/page.py',
        'pages/metadata/page.py',
        'pages/learn/page.py',
        'pages/plotting/page.py',
        'pages/plotting/config.py',
        'pages/plotting/prob_functions.py',
        'pages/plotting/plotting.py',
        'pages/plotting/variables.py',
        'pages/mutualinfo/page.py',
        'pages/literature/page.py',
        'r_integration/inferno_functions.py',
    ],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

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
    icon='resources/inferno_symbol.icns'
)

app = BUNDLE(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    name="Inferno.app", 
    icon='resources/inferno_symbol.icns'
)
