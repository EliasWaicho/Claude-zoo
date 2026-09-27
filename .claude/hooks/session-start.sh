#!/bin/bash
# Install the CAD toolchain in Claude Code on the web sessions.
set -euo pipefail
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi
cd "$CLAUDE_PROJECT_DIR"
pip install --quiet -r requirements.txt
