# -*- mode: python ; coding: utf-8 -*-
# Forge Chamber — PyInstaller build spec
# Produces a single-file exe with all dependencies bundled.
# Usage: cd backend && pyinstaller forge_chamber.spec --clean

from PyInstaller.utils.hooks import collect_all, collect_data_files

datas, binaries, hiddenimports = [], [], []

for pkg in [
    'fastapi', 'uvicorn', 'livekit', 'livekit_agents',
    'langchain', 'langgraph', 'chromadb', 'sentence_transformers',
    'llama_index', 'sqlalchemy', 'anthropic', 'pydantic',
    'pydantic_settings', 'openai',
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

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    name='forge_chamber',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    console=False,
    onefile=True,
    icon='../desktop/assets/icon.ico',
)
