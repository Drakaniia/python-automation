use clap::Parser;
use magic::cli::{Cli, Command, format_processes_json};
use magic::config::{ConfigContext, DEFAULT_PORTS};
use magic::scanner::{ProcessInfo, Protocol};
use std::fs;
use std::time::{SystemTime, UNIX_EPOCH};

#[test]
fn starts_interactive_tui_on_common_dev_ports_by_default() {
    let cli = Cli::parse_from(["magic"]);
    let resolved = cli.resolve().expect("default cli should resolve");

    assert_eq!(resolved.ports, DEFAULT_PORTS.to_vec());
    assert_eq!(resolved.command, Command::Interactive);
}

#[test]
fn default_ports_include_common_language_and_framework_dev_servers() {
    let cli = Cli::parse_from(["magic"]);
    let resolved = cli.resolve().expect("default cli should resolve");

    for port in [
        1420, 3000, 3001, 4200, 5000, 5173, 8000, 8080, 8081, 8888, 9000,
    ] {
        assert!(
            resolved.ports.contains(&port),
            "default ports should include {port}"
        );
    }
}

#[test]
fn default_ports_are_unique() {
    let mut ports = DEFAULT_PORTS.to_vec();
    ports.sort_unstable();
    ports.dedup();

    assert_eq!(ports.len(), DEFAULT_PORTS.len());
}

#[test]
fn parses_list_command_with_comma_separated_ports() {
    let cli = Cli::parse_from(["magic", "list", "3000,5173", "--tcp"]);
    let resolved = cli.resolve().expect("list cli should resolve");

    assert_eq!(resolved.ports, vec![3000, 5173]);
    assert_eq!(resolved.command, Command::List);
    assert!(resolved.tcp);
}

#[test]
fn resolves_ports_from_cli_then_env_then_profile_then_config_defaults() {
    let config_path = unique_config_path("port-resolution");
    fs::create_dir_all(config_path.parent().unwrap()).expect("config dir should be writable");
    fs::write(
        &config_path,
        r#"{"default_ports":[6100],"profiles":{"api":[6200,6201]}}"#,
    )
    .expect("config fixture should be writable");

    let context = ConfigContext {
        magic_ports: Some("7000,7001".to_string()),
        config_path: Some(config_path.clone()),
    };
    let cli = Cli::parse_from(["magic", "--profile", "api"]);
    let resolved = cli
        .resolve_with_context(&context)
        .expect("env ports should resolve before profile ports");
    assert_eq!(resolved.ports, vec![7000, 7001]);

    let context = ConfigContext {
        magic_ports: None,
        config_path: Some(config_path.clone()),
    };
    let cli = Cli::parse_from(["magic", "--profile", "api"]);
    let resolved = cli
        .resolve_with_context(&context)
        .expect("profile ports should resolve from config file");
    assert_eq!(resolved.ports, vec![6200, 6201]);

    let cli = Cli::parse_from(["magic"]);
    let resolved = cli
        .resolve_with_context(&context)
        .expect("config defaults should resolve when no profile is selected");
    assert_eq!(resolved.ports, vec![6100]);

    let cli = Cli::parse_from(["magic", "3000"]);
    let resolved = cli
        .resolve_with_context(&context)
        .expect("CLI ports should win over every saved source");
    assert_eq!(resolved.ports, vec![3000]);
}

#[test]
fn parses_config_json_tree_quiet_and_completion_commands() {
    let list = Cli::parse_from(["magic", "list", "3000", "--json"])
        .resolve()
        .expect("json list should resolve");
    assert_eq!(list.command, Command::List);
    assert!(list.json);

    let kill = Cli::parse_from(["magic", "kill", "3000", "--yes", "--quiet", "--tree"])
        .resolve()
        .expect("quiet tree kill should resolve");
    assert_eq!(kill.command, Command::Kill);
    assert!(kill.quiet);
    assert!(kill.tree);

    let config = Cli::parse_from(["magic", "config", "set-profile", "api", "7000,7001"])
        .resolve()
        .expect("config set-profile should resolve");
    assert_eq!(config.command, Command::ConfigSetProfile);
    assert_eq!(config.profile_name.as_deref(), Some("api"));
    assert_eq!(config.ports, vec![7000, 7001]);

    let completions = Cli::parse_from(["magic", "completions", "bash"])
        .resolve()
        .expect("completion generation should resolve");
    assert_eq!(completions.command, Command::Completions);
}

#[test]
fn formats_listeners_as_json_for_scripts() {
    let output = format_processes_json(&[ProcessInfo::new(3000, 1234, Protocol::Tcp)
        .with_command("node")
        .with_command_line("npm run dev")
        .with_executable_path("/usr/bin/node")
        .with_cwd("/workspace/app")
        .with_parent_pid(42)])
    .expect("json output should serialize");

    let parsed: serde_json::Value =
        serde_json::from_str(&output).expect("output should be valid json");
    assert_eq!(parsed[0]["port"], 3000);
    assert_eq!(parsed[0]["pid"], 1234);
    assert_eq!(parsed[0]["protocol"], "TCP");
    assert_eq!(parsed[0]["command"], "node");
    assert_eq!(parsed[0]["command_line"], "npm run dev");
    assert_eq!(parsed[0]["executable_path"], "/usr/bin/node");
    assert_eq!(parsed[0]["cwd"], "/workspace/app");
    assert_eq!(parsed[0]["parent_pid"], 42);
}

fn unique_config_path(name: &str) -> std::path::PathBuf {
    let nanos = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .expect("clock should be after epoch")
        .as_nanos();
    std::env::temp_dir()
        .join(format!("magic-{name}-{nanos}"))
        .join("config.json")
}
