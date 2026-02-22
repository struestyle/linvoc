#!/bin/bash
# Launcher script for linvoc - use this for KDE shortcuts
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "${SCRIPT_DIR}/.venv/bin/linvoc" "$@"
