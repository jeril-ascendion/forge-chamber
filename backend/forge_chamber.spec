# -*- mode: python ; coding: utf-8 -*-
# Forge Chamber — PyInstaller build spec
# Produces a directory build (faster than onefile on CI).
# electron-builder bundles the entire dist/forge_chamber/ folder.
# Usage: cd backend && pyinstaller forge_chamber.spec --clean

from PyInstaller.utils.hooks import collect_all

datas, binaries, hiddenimports = [], [], []

# Only collect packages that need special handling.
# Skip heavy ML packages — they work fine with just hiddenimports.
for pkg in [
    'fastapi', 'uvicorn', 'pydantic', 'pydantic_settings',
    'sqlalchemy', 'chromadb', 'openai',
]:
    try:
        d, b, h = collect_all(pkg)
        datas += d
        binaries += b
        hiddenimports += h
    except Exception:
        pass

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=binaries,
    datas=datas + [
        ('agents/', 'agents/'),
        ('api/', 'api/'),
        ('core/', 'core/'),
        ('db/', 'db/'),
        ('rag/', 'rag/'),
        ('voice/', 'voice/'),
        ('mentoring/', 'mentoring/'),
    ],
    hiddenimports=hiddenimports + [
        'aiosqlite',
        'greenlet',
        'sqlalchemy.dialects.sqlite',
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        'fastembed',
        'onnxruntime',
        'langchain',
        'langgraph',
        'llama_index',
        'anthropic',
        'livekit',
        'livekit.agents',
        'backend.api.routes.health',
        'backend.api.routes.engineer',
        'backend.api.routes.session',
        'backend.api.routes.rag',
        'backend.api.routes.progress',
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

# Directory build (not onefile) — much faster on CI
exe = EXE(
    pyz,
    a.scripts,
    name='forge_chamber',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    icon='../desktop/assets/icon.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name='forge_chamber',
)
