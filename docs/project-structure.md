# Project Structure

```text
magic/
|-- .github/workflows/
|   |-- ci.yml
|   `-- release.yml
|-- docs/
|   |-- installation.md
|   |-- project-structure.md
|   `-- release.md
|-- scripts/
|   |-- install.ps1
|   |-- uninstall.ps1
|   |-- install.sh
|   `-- uninstall.sh
|-- src/
|   |-- main.rs
|   |-- lib.rs
|   |-- bin/
|   |  `-- portkill.rs
|   |-- cli.rs
|   |-- config.rs
|   |-- scanner/
|   |-- process/
|   `-- tui/
|-- tests/
|-- Cargo.toml
|-- Cargo.lock
|-- LICENSE
`-- README.md
```

## Root Files

- `Cargo.toml`: package metadata, dependencies, binary names, and release profile.
- `Cargo.lock`: locked dependency graph for reproducible builds.
- `README.md`: short user-facing install and usage guide.
- `LICENSE`: MIT license.

## Source

- `src/main.rs`: entry point for the `magic` binary.
- `src/bin/portkill.rs`: alternate binary name for the same tool.
- `src/lib.rs`: public module exports used by binaries and tests.
- `src/cli.rs`: command-line parsing, subcommands, and routing.
- `src/config.rs`: default ports and protocol defaults.
- `src/scanner/`: OS-specific process discovery and parser helpers.
- `src/process/`: graceful and forced process termination.
- `src/tui/`: terminal setup, state, rendering, and event loop.

## Tests

- `tests/cli.rs`: argument resolution and command behavior.
- `tests/scanner_parsing.rs`: parser fixtures for platform command output.
- `tests/process.rs`: graceful-to-force termination fallback.
- `tests/tui_state.rs`: deterministic TUI state transitions.

## Distribution

- `.github/workflows/ci.yml`: formatting and test checks.
- `.github/workflows/release.yml`: cross-platform release build and upload.
- `scripts/install.ps1`: Windows installer.
- `scripts/uninstall.ps1`: Windows uninstaller.
- `scripts/install.sh`: macOS/Linux installer.
- `scripts/uninstall.sh`: macOS/Linux uninstaller.
