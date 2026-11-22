# PyInstaller config for the desktop app backend.
# Run from desktop/ with "npm run build:backend", or by hand from backend/:
#     .venv/bin/python -m PyInstaller supermarket-backend.spec --noconfirm
# Output: dist/supermarket-backend/ (a folder with the executable, Python is not needed)

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    # data files read with Path(__file__), they keep the same folder inside the package
    datas=[
        ('app/postal_code/postal_code.json', 'app/postal_code'),
        ('app/postal_code/super_fresh_stores.json', 'app/postal_code'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    # not used by the app, keeps the package smaller
    excludes=['tkinter', 'unittest', 'pydoc'],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='supermarket-backend',
    debug=False,
    strip=False,
    upx=False,
    # console app so Electron can read its output; Electron starts it hidden
    console=True,
)

# one folder (not --onefile): starts faster because nothing is extracted on every run
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name='supermarket-backend',
)
