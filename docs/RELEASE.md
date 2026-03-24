# Forge Chamber — Release Process

## Pre-release Checklist

1. All tests pass locally:
   ```bash
   cd backend && source .venv/bin/activate && pytest tests/ -v
   cd frontend && npx vitest run && npx tsc --noEmit
   ```

2. Update version in `desktop/package.json`:
   ```json
   "version": "1.1.0"
   ```

3. Update `docs/current-version.txt`:
   ```
   v1.1.0
   ```

4. Commit version bump:
   ```bash
   git add desktop/package.json docs/current-version.txt
   git commit -m "chore: release v1.1.0"
   ```

## Creating a Release

5. Tag the release:
   ```bash
   git tag -a v1.1.0 -m "Forge Chamber v1.1.0 — brief description"
   ```

6. Push the tag (triggers GitHub Actions build):
   ```bash
   git push origin v1.1.0
   ```

7. Monitor the build:
   - Go to https://github.com/jeril-ascendion/forge-chamber/actions
   - The "Release Build" workflow runs on Windows (~20 min)
   - Steps: Python sidecar (PyInstaller) -> React build -> Electron installer

8. Verify the release:
   - Check https://github.com/jeril-ascendion/forge-chamber/releases
   - Download the .exe installer
   - Test on a clean Windows machine (no dev tools installed)
   - Verify: app launches, splash screen, sidecar starts, /health responds

## Release Types

| Tag Pattern | Type | Auto-publish |
|-------------|------|-------------|
| `v1.0.0` | Stable | Yes |
| `v1.1.0-beta.1` | Beta | Yes (marked prerelease) |
| `v1.1.0-rc.1` | Release Candidate | Yes (marked prerelease) |

## Post-release

9. Announce to pilot engineers via Ascendion Slack
10. Monitor for crash reports in the first 24 hours
11. The download page at `docs/download/index.html` auto-updates
    the version badge via GitHub Actions

## Hotfix Process

If a critical bug is found in a released version:

1. Create a hotfix branch from the release tag:
   ```bash
   git checkout -b hotfix/v1.0.1 v1.0.0
   ```
2. Fix the bug, commit, push
3. Tag: `git tag -a v1.0.1 -m "Hotfix: description"`
4. Push tag: `git push origin v1.0.1`
5. Merge hotfix back to develop:
   ```bash
   git checkout develop && git merge hotfix/v1.0.1
   ```

## Build Artifacts

| Artifact | Location | Size |
|----------|----------|------|
| Python sidecar | `backend/dist/forge_chamber.exe` | ~180 MB |
| React frontend | `frontend/dist/` | ~2 MB |
| Windows installer | `desktop/dist/Forge-Chamber-Setup-*.exe` | ~200 MB |
