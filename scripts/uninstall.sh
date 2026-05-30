#!/usr/bin/env sh
set -eu

INSTALL_DIR="${MAGIC_INSTALL_DIR:-$HOME/.local/bin}"

rm -f "$INSTALL_DIR/magic" "$INSTALL_DIR/portkill"

echo "Magic uninstalled from $INSTALL_DIR"
