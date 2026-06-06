# Magic Port Killer

`magic` is a globally installable terminal port killer for local development.
It scans common dev ports, shows the running processes in an interactive TUI,
and makes it easy to kill stuck port processes by typing `magic` in your terminal.

Default ports cover common local development servers, including Tauri/Svelte,
Vite, Next.js, Rails, Angular, Astro, Django, Flask, ASP.NET, Spring, Expo,
Storybook, Jupyter, Cloudflare Workers, and live-reload ports.

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
magic --profile api
portkill
magic list 3000,5173 --tcp
magic list --json
magic kill 3000
magic kill 3000 --yes --quiet
magic kill 3000 --yes --tree
magic config show
magic config set-ports 3000,5173,8080
magic config set-profile api 7000,7001
magic completions bash
```

Port resolution order is:

```text
CLI ports > MAGIC_PORTS > saved profile/default config > built-in defaults
```

Set `MAGIC_CONFIG_DIR` or `MAGIC_CONFIG_PATH` to place the config somewhere
specific, such as a project-local test fixture.

Inside the TUI:

```text
Up/Down or j/k  move selection
g/Home          jump to first process
G/End           jump to last process
Space           mark or unmark process
a               mark all or clear all
Enter           review selected process(es)
y               graceful termination, then force fallback if needed
f               force kill immediately
n/Esc           cancel confirmation
r               rescan
q               quit
```

Wide terminals show the process table beside a selected-process inspector with
PID, port/protocol, mark state, command, working directory, executable path, and
parent PID. The confirmation view lists exact selected PIDs, ports, protocols,
and available process identity before termination. Post-kill results stay
visible until the next explicit scan or action.

## Docs

- [Installation](docs/installation.md)
- [GitHub release setup](docs/release.md)
- [Project structure](docs/project-structure.md)
- [TUI UX design](docs/tui-ux-design.md)

## Development

```sh
cargo fmt -- --check
cargo test
cargo run
```

## License

MIT
