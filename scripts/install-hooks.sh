#!/bin/bash
# Install git hooks for the Forge Chamber repository
set -e

cp scripts/pre-commit-hook .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
echo "Git hooks installed."
