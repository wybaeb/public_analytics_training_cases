#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"
NOTEBOOK_PATH="$SCRIPT_DIR/client_clustering_walkthrough.ipynb"

if command -v jupyter >/dev/null 2>&1; then
  jupyter lab "$NOTEBOOK_PATH"
else
  open "$NOTEBOOK_PATH"
fi
