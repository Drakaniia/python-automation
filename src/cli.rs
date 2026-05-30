use std::io::{self, Write};
use std::process::ExitCode;

use clap::{Args, Parser, Subcommand};

use crate::config::{DEFAULT_PORTS, ProtocolFilter};
use crate::process::{NativeTerminator, terminate_force, terminate_many_with_fallback};
use crate::scanner::{ProcessInfo, scan_ports};
use crate::tui;

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum Command {
    Interactive,
    List,
    Kill,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct ResolvedConfig {
    pub command: Command,
    pub ports: Vec<u16>,
    pub tcp: bool,
    pub udp: bool,
    pub yes: bool,
    pub force: bool,
}

#[derive(Clone, Debug, Parser)]
#[command(
    name = "magic",
    bin_name = "magic",
    version,
    about = "Interactive development port killer",
    long_about = "Scan common development ports, inspect listeners, and terminate stuck processes from a polished terminal UI."
)]
pub struct Cli {
    #[command(subcommand)]
    command: Option<RawCommand>,

    #[arg(
        value_name = "PORTS",
        value_delimiter = ',',
        help = "Ports to scan in interactive mode, for example 3000,5173"
    )]
    ports: Vec<u16>,

    #[arg(long, global = true, help = "Only scan TCP listeners")]
    pub tcp: bool,

    #[arg(long, global = true, help = "Only scan UDP sockets")]
    pub udp: bool,

    #[arg(
        short = 'y',
        long,
        global = true,
        help = "Skip non-interactive kill prompt"
    )]
    pub yes: bool,

    #[arg(
        short,
        long,
        global = true,
        help = "Force kill immediately instead of trying graceful termination first"
    )]
    pub force: bool,
}

#[derive(Clone, Debug, Subcommand)]
enum RawCommand {
    #[command(about = "Print listeners on the selected ports")]
    List(PortArgs),
    #[command(about = "Terminate listeners without launching the TUI")]
    Kill(PortArgs),
}

#[derive(Clone, Debug, Args)]
struct PortArgs {
    #[arg(value_name = "PORTS", value_delimiter = ',')]
    ports: Vec<u16>,
}

impl Cli {
    pub fn resolve(&self) -> Result<ResolvedConfig, String> {
        let (command, ports) = match &self.command {
            Some(RawCommand::List(args)) => (Command::List, resolve_ports(&args.ports)?),
            Some(RawCommand::Kill(args)) => (Command::Kill, resolve_ports(&args.ports)?),
            None => (Command::Interactive, resolve_ports(&self.ports)?),
        };

        if self.tcp && self.udp {
            return Err("--tcp and --udp are mutually exclusive".to_string());
        }

        let filter = ProtocolFilter::from_flags(self.tcp, self.udp);

        Ok(ResolvedConfig {
            command,
            ports,
            tcp: filter.tcp,
            udp: filter.udp,
            yes: self.yes,
            force: self.force,
        })
    }
}

pub fn run_from_env() -> ExitCode {
    match Cli::parse().resolve() {
        Ok(config) => run(config),
        Err(message) => {
            eprintln!("error: {message}");
            ExitCode::from(2)
        }
    }
}

pub fn run(config: ResolvedConfig) -> ExitCode {
    match config.command {
        Command::Interactive => match tui::run(config) {
            Ok(()) => ExitCode::SUCCESS,
            Err(message) => {
                eprintln!("error: {message}");
                ExitCode::from(1)
            }
        },
        Command::List => match scan_ports(&config.ports, config.tcp, config.udp) {
            Ok(processes) => {
                print_processes(&config.ports, &processes);
                ExitCode::SUCCESS
            }
            Err(message) => {
                eprintln!("error: {message}");
                ExitCode::from(1)
            }
        },
        Command::Kill => run_non_interactive_kill(config),
    }
}

fn run_non_interactive_kill(config: ResolvedConfig) -> ExitCode {
    let processes = match scan_ports(&config.ports, config.tcp, config.udp) {
        Ok(processes) => processes,
        Err(message) => {
            eprintln!("error: {message}");
            return ExitCode::from(1);
        }
    };

    if processes.is_empty() {
        println!("No listeners found on {}", join_ports(&config.ports));
        return ExitCode::SUCCESS;
    }

    print_processes(&config.ports, &processes);
    let pids = unique_pids(&processes);

    if !config.yes && !confirm(&format!("Kill {} process(es)?", pids.len())) {
        println!("Aborted");
        return ExitCode::SUCCESS;
    }

    let mut terminator = NativeTerminator;
    let results = if config.force {
        pids.into_iter()
            .map(|pid| terminate_force(&mut terminator, pid))
            .collect()
    } else {
        terminate_many_with_fallback(&mut terminator, &pids, true)
    };

    let failed = results
        .iter()
        .inspect(|result| println!("{result}"))
        .any(|result| result.is_failed());

    if failed {
        ExitCode::from(1)
    } else {
        ExitCode::SUCCESS
    }
}

fn resolve_ports(ports: &[u16]) -> Result<Vec<u16>, String> {
    let ports = if ports.is_empty() {
        DEFAULT_PORTS.to_vec()
    } else {
        ports.to_vec()
    };

    if ports.contains(&0) {
        return Err("ports must be between 1 and 65535".to_string());
    }

    let mut deduped = Vec::new();
    for port in ports {
        if !deduped.contains(&port) {
            deduped.push(port);
        }
    }

    Ok(deduped)
}

fn print_processes(ports: &[u16], processes: &[ProcessInfo]) {
    if processes.is_empty() {
        println!("No listeners found on {}", join_ports(ports));
        return;
    }

    println!("{:<7} {:<6} {:<8} Command", "Port", "PID", "Protocol");
    for process in processes {
        println!(
            "{:<7} {:<6} {:<8} {}",
            process.port,
            process.pid,
            process.protocol,
            process.command.as_deref().unwrap_or("-")
        );
    }
}

fn confirm(prompt: &str) -> bool {
    print!("{prompt} [y/N] ");
    let _ = io::stdout().flush();

    let mut answer = String::new();
    if io::stdin().read_line(&mut answer).is_err() {
        return false;
    }

    matches!(answer.trim(), "y" | "Y" | "yes" | "YES")
}

fn unique_pids(processes: &[ProcessInfo]) -> Vec<u32> {
    let mut pids = processes
        .iter()
        .map(|process| process.pid)
        .collect::<Vec<u32>>();
    pids.sort_unstable();
    pids.dedup();
    pids
}

fn join_ports(ports: &[u16]) -> String {
    ports
        .iter()
        .map(u16::to_string)
        .collect::<Vec<String>>()
        .join(", ")
}
