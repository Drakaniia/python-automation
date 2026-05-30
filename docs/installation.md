# Installation

Magic is distributed as prebuilt GitHub Release binaries. End users do not need
Rust or Cargo.

## Windows

Install:

```powershell
irm https://raw.githubusercontent.com/Drakaniia/magic/main/scripts/install.ps1 | iex
```

Uninstall:

```powershell
irm https://raw.githubusercontent.com/Drakaniia/magic/main/scripts/uninstall.ps1 | iex
```

After installing, open a new terminal and run:

```powershell
magic
```

## macOS and Linux

Install:

```sh
curl -fsSL https://raw.githubusercontent.com/Drakaniia/magic/main/scripts/install.sh | sh
```

Uninstall:

```sh
curl -fsSL https://raw.githubusercontent.com/Drakaniia/magic/main/scripts/uninstall.sh | sh
```

After installing, open a new terminal and run:

```sh
magic
```

## Manual Install

Download the latest release from:

```text
https://github.com/Drakaniia/magic/releases/latest
```

Choose the asset for your platform:

```text
magic-windows-x64.zip
magic-linux-x64.tar.gz
magic-macos-x64.tar.gz
magic-macos-arm64.tar.gz
```

Extract the archive and place the binaries in a directory on your `PATH`.

## Development Install

For local development with Rust installed:

```sh
cargo install --path .
magic
portkill
```
