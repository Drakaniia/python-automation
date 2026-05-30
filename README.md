# Magic Port Killer

`magic` is a globally installable terminal port killer for local development.
It scans common dev ports, shows the running processes in an interactive TUI,
and makes it easy to kill stuck port processes by typing `magic` in your terminal.

Default ports: `5173`, `3000`, and `8080`.

## Install

Windows:

```powershell
irm https://raw.githubusercontent.com/Drakaniia/magic/main/scripts/install.ps1 | iex
```

macOS/Linux:

```sh
curl -fsSL https://raw.githubusercontent.com/Drakaniia/magic/main/scripts/install.sh | sh
```

Open a new terminal after installing, then run:

```sh
magic
```

## Usage

```sh
magic
magic 3000,5173
portkill
magic list 3000,5173 --tcp
magic kill 3000
magic kill 3000 --yes
```

Inside the TUI:

```text
Up/Down  navigate
Space    mark process
a        toggle all
Enter    confirm kill
y        graceful termination, then force fallback if needed
f        force kill immediately
r        rescan
q/Esc    quit
```

## Docs

- [Installation](docs/installation.md)
- [GitHub release setup](docs/release.md)
- [Project structure](docs/project-structure.md)

## Development

```sh
cargo fmt -- --check
cargo test
cargo run
```

## License

MIT
