# Project Structure

```text
magic/
|-- .github/workflows/
|   |-- ci.yml
|   `-- release.yml
|-- docs/
|   |-- installation.md
|   |-- project-structure.md
|   |-- release.md
|   `-- tui-ux-design.md
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
- `src/cli.rs`: command-line parsing, config commands, JSON output, completions, and routing.
- `src/config.rs`: built-in defaults, saved JSON config, profiles, and env/config resolution.
- `src/scanner/`: OS-specific process discovery, scanner diagnostics, process identity, and parser helpers.
- `src/process/`: graceful, forced, and optional process-tree termination.
- `src/tui/`: terminal setup, state, rendering, and event loop.

## Tests

- `tests/cli.rs`: argument/config resolution, command behavior, and JSON formatting.
- `tests/scanner_parsing.rs`: parser fixtures and scanner diagnostic classification.
- `tests/process.rs`: graceful-to-force fallback and process-tree ordering.
- `tests/tui_state.rs`: deterministic TUI selection, confirmation, result, navigation, and pagination state.

## Design Docs

- `docs/tui-ux-design.md`: keyboard-first ratatui layout, hierarchy, navigation, and feedback strategy.

## Distribution

- `.github/workflows/ci.yml`: formatting, cross-platform tests, and installer smoke checks.
- `.github/workflows/release.yml`: cross-platform release build, archive validation, and upload.
- `scripts/install.ps1`: Windows installer.
- `scripts/uninstall.ps1`: Windows uninstaller.
- `scripts/install.sh`: macOS/Linux installer.
- `scripts/uninstall.sh`: macOS/Linux uninstaller.
