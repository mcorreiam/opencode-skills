#!/usr/bin/env bash
# list_sessions.sh — wrapper fino para list_sessions.py
# Uso: scripts/list_sessions.sh --limit 5 --scope current
#      scripts/list_sessions.sh --limit 20 --scope all --offset 20
# Bundle da skill list-past-sessions: 1 comando substitui 3 queries + conversão Python manual.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$SCRIPT_DIR/list_sessions.py" "$@"
