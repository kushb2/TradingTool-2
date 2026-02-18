#!/usr/bin/env bash
set -euo pipefail

if command -v poetry >/dev/null 2>&1; then
  exec poetry "$@"
fi

if [ -x "$HOME/.local/bin/poetry" ]; then
  exec "$HOME/.local/bin/poetry" "$@"
fi

echo "poetry command not found. Install Poetry or add it to PATH." >&2
exit 127
