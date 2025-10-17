# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['src/main.py'],
    pathex=['src/'],
    binaries=[],
    datas=[
        ('src/resources', 'resources'),
        ('src/gen/translation_files', 'gen/translation_files')
    ],
    hiddenimports=['_cffi_backend'],
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
    [],
    exclude_binaries=True,
    name='FamilyRules',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch='universal2',
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='FamilyRules',
)
app = BUNDLE(
    coll,
    name='FamilyRules.app',
    icon='src/resources/icon.icns',
    bundle_identifier=None,
    info_plist={
            'LSUIElement': True,
            'LSBackgroundOnly': False,
            'NSUIElement': True
        }
)
