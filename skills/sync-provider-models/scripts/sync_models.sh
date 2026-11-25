#!/usr/bin/env bash
# sync_models.sh — wrapper fino para sync_models.py
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$here/sync_models.py" "$@"
