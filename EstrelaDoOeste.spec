# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['EstrelaDoOeste.py'],
    pathex=[r'C:\saloonEstrelaDoOeste\SALOONSOFTWARE\EstrelaDoOeste.py'],
    binaries=[],
    datas=[
        ('C:\\Users\\Fernando\\Desktop\\SALOONSOFTWARE\\saloon_recipes.db', '.'),  # Inclua o banco de dados
        ('C:\\Users\Fernando\\Desktop\\SALOONSOFTWARE\\imagens\\saloon.jpg', '.'),        # Inclua a imagem
    ],
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
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='EstrelaDoOeste',
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
      icon='C:\\Users\\Fernando\\Desktop\\SALOONSOFTWARE\\imagens\\saloon.ico'  # Adicione o ícone
)
