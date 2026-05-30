use clap::Parser;
use magic::cli::{Cli, Command};
use magic::config::DEFAULT_PORTS;

#[test]
fn starts_interactive_tui_on_common_dev_ports_by_default() {
    let cli = Cli::parse_from(["magic"]);
    let resolved = cli.resolve().expect("default cli should resolve");

    assert_eq!(resolved.ports, DEFAULT_PORTS.to_vec());
    assert_eq!(resolved.command, Command::Interactive);
}

#[test]
fn parses_list_command_with_comma_separated_ports() {
    let cli = Cli::parse_from(["magic", "list", "3000,5173", "--tcp"]);
    let resolved = cli.resolve().expect("list cli should resolve");

    assert_eq!(resolved.ports, vec![3000, 5173]);
    assert_eq!(resolved.command, Command::List);
    assert!(resolved.tcp);
}
