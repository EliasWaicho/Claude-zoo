#!/bin/bash
# One-time setup of the 3D-printing toolchain on a Mac.
# Run from the repo root:  bash setup/install-mac.sh
set -euo pipefail

if ! command -v brew >/dev/null; then
  echo "Installing Homebrew (you'll be asked for your Mac password)..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  eval "$(/opt/homebrew/bin/brew shellenv 2>/dev/null || /usr/local/bin/brew shellenv)"
fi

echo "== Command-line tools: uv (runs Python MCP servers), Node (runs the Bambu MCP), Python"
brew install uv node python@3.12

echo "== Desktop apps"
brew install --cask bambu-studio orcaslicer openscad blender || true

echo "== This repo's Python CAD libraries"
python3.12 -m venv .venv
.venv/bin/pip install --quiet -r requirements.txt
.venv/bin/python tools/build.py models/wall_hook.py

echo
echo "Done. Next: add the connectors to Claude Desktop (see setup/MAC.md, step 3)."
echo "uvx lives at: $(command -v uvx)"
echo "npx lives at: $(command -v npx)"
