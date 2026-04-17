#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

PYTHON=${PYTHON:-python3}

if ! command -v "$PYTHON" >/dev/null 2>&1; then
  echo "Python not found. Install Python 3.10+ or set PYTHON=python3."
  exit 1
fi

if ! "$PYTHON" -m PyInstaller --version >/dev/null 2>&1; then
  echo "PyInstaller is not installed. Installing it locally..."
  "$PYTHON" -m pip install --user pyinstaller
fi

DIST_DIR="$ROOT_DIR/dist"
BUILD_DIR="$ROOT_DIR/build"
WORK_DIR="$BUILD_DIR/pyinstaller"

rm -rf "$DIST_DIR" "$BUILD_DIR"

"$PYTHON" -m PyInstaller \
  --noconfirm \
  --clean \
  --windowed \
  --onedir \
  --name "24-Hour-Digital-Clock" \
  --distpath "$DIST_DIR" \
  --workpath "$WORK_DIR" \
  --specpath "$BUILD_DIR" \
  "24-Hour-Digital-Clock.py"

printf "\nBuild complete. App folder: %s/24-Hour-Digital-Clock\n" "$DIST_DIR"
