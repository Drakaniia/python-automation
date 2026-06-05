#!/usr/bin/env sh
set -eu

REPOSITORY="${MAGIC_REPOSITORY:-Drakaniia/magic}"
INSTALL_DIR="${MAGIC_INSTALL_DIR:-$HOME/.local/bin}"
BASE_URL="${MAGIC_BASE_URL:-https://github.com/$REPOSITORY/releases/latest/download}"

OS="$(uname -s)"
ARCH="$(uname -m)"

case "$OS:$ARCH" in
  Linux:x86_64|Linux:amd64)
    ASSET="magic-linux-x64.tar.gz"
    ;;
  Darwin:x86_64)
    ASSET="magic-macos-x64.tar.gz"
    ;;
  Darwin:arm64|Darwin:aarch64)
    ASSET="magic-macos-arm64.tar.gz"
    ;;
  *)
    echo "Unsupported platform: $OS $ARCH" >&2
    exit 1
    ;;
esac

TMP_DIR="$(mktemp -d)"
cleanup() {
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT

fetch_asset() {
  source="$1"
  destination="$2"

  case "$source" in
    http://*|https://*|file://*)
      curl -fsSL "$source" -o "$destination"
      ;;
    *)
      cp "$source" "$destination"
      ;;
  esac
}

echo "Downloading Magic from $REPOSITORY..."
fetch_asset "$BASE_URL/$ASSET" "$TMP_DIR/$ASSET"
fetch_asset "$BASE_URL/SHA256SUMS.txt" "$TMP_DIR/SHA256SUMS.txt"

EXPECTED="$(grep "  $ASSET\$" "$TMP_DIR/SHA256SUMS.txt" | awk '{print $1}')"
if [ -z "$EXPECTED" ]; then
  echo "Could not find $ASSET in SHA256SUMS.txt." >&2
  exit 1
fi

if command -v sha256sum >/dev/null 2>&1; then
  ACTUAL="$(sha256sum "$TMP_DIR/$ASSET" | awk '{print $1}')"
else
  ACTUAL="$(shasum -a 256 "$TMP_DIR/$ASSET" | awk '{print $1}')"
fi

if [ "$ACTUAL" != "$EXPECTED" ]; then
  echo "Checksum mismatch for $ASSET." >&2
  echo "Expected: $EXPECTED" >&2
  echo "Actual:   $ACTUAL" >&2
  exit 1
fi

tar -xzf "$TMP_DIR/$ASSET" -C "$TMP_DIR"

MAGIC_BIN="$(find "$TMP_DIR" -type f -name magic | head -n 1)"
PORTKILL_BIN="$(find "$TMP_DIR" -type f -name portkill | head -n 1)"

if [ -z "$MAGIC_BIN" ] || [ -z "$PORTKILL_BIN" ]; then
  echo "The release archive did not contain magic and portkill." >&2
  exit 1
fi

mkdir -p "$INSTALL_DIR"
install -m 755 "$MAGIC_BIN" "$INSTALL_DIR/magic"
install -m 755 "$PORTKILL_BIN" "$INSTALL_DIR/portkill"

echo "Magic installed to $INSTALL_DIR"
case ":$PATH:" in
  *":$INSTALL_DIR:"*)
    echo "Run: magic"
    ;;
  *)
    echo "Add this to your shell profile if it is not already there:"
    echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo "Then open a new terminal and run: magic"
    ;;
esac
