use std::io::{self, Write};
use std::process::ExitCode;

use clap::{Args, CommandFactory, Parser, Subcommand};
use clap_complete::{Shell, generate};
use serde_json::json;

use crate::config::{
    ConfigContext, ProtocolFilter, config_path, load_config, normalize_ports,
    resolve_ports_with_context, set_default_ports, set_profile_ports,
};
use crate::process::{
    NativeTerminator, terminate_force, terminate_force_tree, terminate_many_with_fallback,
    terminate_many_with_fallback_tree,
};
use crate::scanner::{ProcessInfo, ScanStatus, scan_ports_report};
use crate::tui;

#[derive(Clone, Debug, Eq, PartialEq)]
pub enum Command {
    Interactive,
    List,
    Kill,
    ConfigShow,
    ConfigSetPorts,
    ConfigSetProfile,
    Completions,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct ResolvedConfig {
    pub command: Command,
    pub ports: Vec<u16>,
    pub profile_name: Option<String>,
    pub tcp: bool,
    pub udp: bool,
    pub yes: bool,
    pub force: bool,
    pub tree: bool,
    pub json: bool,
    pub quiet: bool,
    pub completion_shell: Option<Shell>,
    pub config_context: ConfigContext,
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

    #[arg(
        long,
        global = true,
        value_name = "NAME",
        help = "Use a saved port profile from the Magic config file"
    )]
    profile: Option<String>,

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

    #[arg(
        long,
        global = true,
        help = "Terminate selected process trees instead of only listener PIDs"
    )]
    pub tree: bool,
}

#[derive(Clone, Debug, Subcommand)]
enum RawCommand {
    #[command(about = "Print listeners on the selected ports")]
    List(ListArgs),
    #[command(about = "Terminate listeners without launching the TUI")]
    Kill(KillArgs),
    #[command(about = "Read or write saved Magic port configuration", subcommand)]
    Config(ConfigCommand),
    #[command(about = "Generate shell completions")]
    Completions(CompletionArgs),
}

#[derive(Clone, Debug, Args)]
struct PortArgs {
    #[arg(value_name = "PORTS", value_delimiter = ',')]
    ports: Vec<u16>,
}

#[derive(Clone, Debug, Args)]
struct ListArgs {
    #[arg(value_name = "PORTS", value_delimiter = ',')]
    ports: Vec<u16>,

    #[arg(long, help = "Print listeners as JSON")]
    json: bool,
}

#[derive(Clone, Debug, Args)]
struct KillArgs {
    #[arg(value_name = "PORTS", value_delimiter = ',')]
    ports: Vec<u16>,

    #[arg(long, help = "Suppress successful non-interactive kill output")]
    quiet: bool,
}

#[derive(Clone, Debug, Subcommand)]
enum ConfigCommand {
    #[command(about = "Show the Magic config path and saved ports")]
    Show,
    #[command(about = "Save default ports used when no CLI ports are provided")]
    SetPorts(PortArgs),
    #[command(about = "Save a named port profile")]
    SetProfile {
        name: String,
        #[arg(value_name = "PORTS", value_delimiter = ',')]
        ports: Vec<u16>,
    },
}

#[derive(Clone, Debug, Args)]
struct CompletionArgs {
    #[arg(value_enum)]
    shell: Shell,
}

impl Cli {
    pub fn resolve(&self) -> Result<ResolvedConfig, String> {
        self.resolve_with_context(&ConfigContext::from_env())
    }

    pub fn resolve_with_context(&self, context: &ConfigContext) -> Result<ResolvedConfig, String> {
        if self.tcp && self.udp {
            return Err("--tcp and --udp are mutually exclusive".to_string());
        }

        let filter = ProtocolFilter::from_flags(self.tcp, self.udp);
        let (command, ports) = match &self.command {
            Some(RawCommand::List(args)) => (
                Command::List,
                resolve_ports_with_context(&args.ports, self.profile.as_deref(), context)?,
            ),
            Some(RawCommand::Kill(args)) => (
                Command::Kill,
                resolve_ports_with_context(&args.ports, self.profile.as_deref(), context)?,
            ),
            Some(RawCommand::Config(ConfigCommand::Show)) => (Command::ConfigShow, Vec::new()),
            Some(RawCommand::Config(ConfigCommand::SetPorts(args))) => (
                Command::ConfigSetPorts,
                normalize_ports(args.ports.clone())?,
            ),
            Some(RawCommand::Config(ConfigCommand::SetProfile { ports, .. })) => {
                (Command::ConfigSetProfile, normalize_ports(ports.clone())?)
            }
            Some(RawCommand::Completions(_)) => (Command::Completions, Vec::new()),
            None => (
                Command::Interactive,
                resolve_ports_with_context(&self.ports, self.profile.as_deref(), context)?,
            ),
        };

        let (json, quiet, profile_name, completion_shell) = match &self.command {
            Some(RawCommand::List(args)) => (args.json, false, None, None),
            Some(RawCommand::Kill(args)) => (false, args.quiet, None, None),
            Some(RawCommand::Config(ConfigCommand::SetProfile { name, .. })) => {
                (false, false, Some(name.clone()), None)
            }
            Some(RawCommand::Completions(args)) => (false, false, None, Some(args.shell)),
            _ => (false, false, None, None),
        };

        Ok(ResolvedConfig {
            command,
            ports,
            profile_name,
            tcp: filter.tcp,
            udp: filter.udp,
            yes: self.yes,
            force: self.force,
            tree: self.tree,
            json,
            quiet,
            completion_shell,
            config_context: context.clone(),
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
        Command::List => run_list(config),
        Command::Kill => run_non_interactive_kill(config),
        Command::ConfigShow => run_config_show(&config.config_context),
        Command::ConfigSetPorts => run_config_set_ports(&config.config_context, config.ports),
        Command::ConfigSetProfile => run_config_set_profile(
            &config.config_context,
            config.profile_name.as_deref().unwrap_or_default(),
            config.ports,
        ),
        Command::Completions => run_completions(config.completion_shell),
    }
}

fn run_list(config: ResolvedConfig) -> ExitCode {
    let report = match scan_ports_report(&config.ports, config.tcp, config.udp) {
        Ok(report) => report,
        Err(message) => {
            eprintln!("error: {message}");
            return ExitCode::from(1);
        }
    };

    match report.status {
        ScanStatus::Found | ScanStatus::NoListeners => {
            if config.json {
                match format_processes_json(&report.processes) {
                    Ok(output) => println!("{output}"),
                    Err(message) => {
                        eprintln!("error: {message}");
                        return ExitCode::from(1);
                    }
                }
            } else {
                print_processes(&config.ports, &report.processes);
            }
            ExitCode::SUCCESS
        }
        ScanStatus::Unavailable { .. } | ScanStatus::PermissionLimited { .. } => {
            eprintln!("error: {}", report.guidance());
            ExitCode::from(1)
        }
    }
}

fn run_non_interactive_kill(config: ResolvedConfig) -> ExitCode {
    let report = match scan_ports_report(&config.ports, config.tcp, config.udp) {
        Ok(report) => report,
        Err(message) => {
            eprintln!("error: {message}");
            return ExitCode::from(1);
        }
    };

    if matches!(
        report.status,
        ScanStatus::Unavailable { .. } | ScanStatus::PermissionLimited { .. }
    ) {
        eprintln!("error: {}", report.guidance());
        return ExitCode::from(1);
    }

    let processes = report.processes;
    if processes.is_empty() {
        if !config.quiet {
            println!("No listeners found on {}", join_ports(&config.ports));
        }
        return ExitCode::SUCCESS;
    }

    if !config.quiet {
        print_processes(&config.ports, &processes);
    }
    let pids = unique_pids(&processes);

    if !config.yes && !confirm(&format!("Kill {} process(es)?", pids.len())) {
        println!("Aborted");
        return ExitCode::SUCCESS;
    }

    let mut terminator = NativeTerminator;
    let results = if config.force {
        pids.into_iter()
            .map(|pid| {
                if config.tree {
                    terminate_force_tree(&mut terminator, pid)
                } else {
                    terminate_force(&mut terminator, pid)
                }
            })
            .collect()
    } else if config.tree {
        terminate_many_with_fallback_tree(&mut terminator, &pids, true)
    } else {
        terminate_many_with_fallback(&mut terminator, &pids, true)
    };

    let failed = results
        .iter()
        .inspect(|result| {
            if !config.quiet || result.is_failed() {
                println!("{result}");
            }
        })
        .any(|result| result.is_failed());

    if failed {
        ExitCode::from(1)
    } else {
        ExitCode::SUCCESS
    }
}

fn run_config_show(context: &ConfigContext) -> ExitCode {
    let path = match config_path(context) {
        Ok(path) => path,
        Err(message) => {
            eprintln!("error: {message}");
            return ExitCode::from(1);
        }
    };
    let config = match load_config(context) {
        Ok(config) => config,
        Err(message) => {
            eprintln!("error: {message}");
            return ExitCode::from(1);
        }
    };

    println!("Config: {}", path.display());
    match &config.default_ports {
        Some(ports) if !ports.is_empty() => println!("Default ports: {}", join_ports(ports)),
        _ => println!("Default ports: built-in"),
    }
    if config.profiles.is_empty() {
        println!("Profiles: none");
    } else {
        println!("Profiles:");
        for (name, ports) in config.profiles {
            println!("  {name}: {}", join_ports(&ports));
        }
    }

    ExitCode::SUCCESS
}

fn run_config_set_ports(context: &ConfigContext, ports: Vec<u16>) -> ExitCode {
    match set_default_ports(context, ports) {
        Ok((path, config)) => {
            let ports = config.default_ports.unwrap_or_default();
            println!(
                "Saved default ports {} to {}",
                join_ports(&ports),
                path.display()
            );
            ExitCode::SUCCESS
        }
        Err(message) => {
            eprintln!("error: {message}");
            ExitCode::from(1)
        }
    }
}

fn run_config_set_profile(context: &ConfigContext, name: &str, ports: Vec<u16>) -> ExitCode {
    match set_profile_ports(context, name, ports) {
        Ok((path, config)) => {
            let ports = config.profiles.get(name).cloned().unwrap_or_default();
            println!(
                "Saved profile {name} ports {} to {}",
                join_ports(&ports),
                path.display()
            );
            ExitCode::SUCCESS
        }
        Err(message) => {
            eprintln!("error: {message}");
            ExitCode::from(1)
        }
    }
}

fn run_completions(shell: Option<Shell>) -> ExitCode {
    let Some(shell) = shell else {
        eprintln!("error: completion shell is required");
        return ExitCode::from(2);
    };

    let mut command = Cli::command();
    generate(shell, &mut command, "magic", &mut io::stdout());
    ExitCode::SUCCESS
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
            display_command(process)
        );
    }
}

pub fn format_processes_json(processes: &[ProcessInfo]) -> Result<String, String> {
    let rows = processes
        .iter()
        .map(|process| {
            json!({
                "port": process.port,
                "pid": process.pid,
                "protocol": process.protocol.to_string(),
                "command": process.command.as_deref(),
                "command_line": process.command_line.as_deref(),
                "executable_path": process.executable_path.as_deref(),
                "cwd": process.cwd.as_deref(),
                "parent_pid": process.parent_pid,
            })
        })
        .collect::<Vec<_>>();

    serde_json::to_string_pretty(&rows).map_err(|error| format!("failed to format JSON: {error}"))
}

fn display_command(process: &ProcessInfo) -> String {
    process
        .command_line
        .as_deref()
        .or(process.command.as_deref())
        .unwrap_or("-")
        .to_string()
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
