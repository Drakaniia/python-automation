use std::collections::{BTreeMap, BTreeSet};
use std::fmt;

#[cfg(unix)]
mod unix;
#[cfg(windows)]
mod windows;

#[derive(Clone, Copy, Debug, Eq, PartialEq, Ord, PartialOrd, Hash)]
pub enum Protocol {
    Tcp,
    Udp,
}

impl fmt::Display for Protocol {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::Tcp => formatter.write_str("TCP"),
            Self::Udp => formatter.write_str("UDP"),
        }
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct ProcessInfo {
    pub port: u16,
    pub pid: u32,
    pub protocol: Protocol,
    pub command: Option<String>,
}

pub fn scan_ports(
    ports: &[u16],
    include_tcp: bool,
    include_udp: bool,
) -> Result<Vec<ProcessInfo>, String> {
    if ports.is_empty() {
        return Ok(Vec::new());
    }

    #[cfg(windows)]
    {
        return windows::scan_ports(ports, include_tcp, include_udp);
    }

    #[cfg(unix)]
    {
        return unix::scan_ports(ports, include_tcp, include_udp);
    }

    #[allow(unreachable_code)]
    Err("this operating system is not supported".to_string())
}

pub fn parse_windows_netstat(
    output: &str,
    ports: &[u16],
    include_tcp: bool,
    include_udp: bool,
) -> Vec<ProcessInfo> {
    let requested = ports.iter().copied().collect::<BTreeSet<u16>>();
    let mut processes = Vec::new();

    for line in output.lines() {
        let parts = line.split_whitespace().collect::<Vec<&str>>();
        if parts.len() < 4 {
            continue;
        }

        let protocol = match parts[0] {
            "TCP" if include_tcp => Protocol::Tcp,
            "UDP" if include_udp => Protocol::Udp,
            _ => continue,
        };

        if protocol == Protocol::Tcp && !parts.contains(&"LISTENING") {
            continue;
        }

        let Some(port) = port_from_address(parts[1], &requested) else {
            continue;
        };

        if let Some(pid) = parts.last().and_then(|value| value.parse::<u32>().ok()) {
            processes.push(ProcessInfo {
                port,
                pid,
                protocol,
                command: None,
            });
        }
    }

    sort_and_dedup_processes(processes)
}

pub fn parse_ss_output(
    output: &str,
    ports: &[u16],
    include_tcp: bool,
    include_udp: bool,
) -> Vec<ProcessInfo> {
    let requested = ports.iter().copied().collect::<BTreeSet<u16>>();
    let mut processes = Vec::new();

    for line in output.lines() {
        let parts = line.split_whitespace().collect::<Vec<&str>>();
        if parts.len() < 5 {
            continue;
        }

        let protocol = match parts[0] {
            value if value.starts_with("tcp") && include_tcp => Protocol::Tcp,
            value if value.starts_with("udp") && include_udp => Protocol::Udp,
            _ => continue,
        };

        let Some(port) = port_from_address(parts[4], &requested) else {
            continue;
        };

        for pid in extract_pids(line) {
            processes.push(ProcessInfo {
                port,
                pid,
                protocol,
                command: extract_command_name(line, pid),
            });
        }
    }

    sort_and_dedup_processes(processes)
}

pub fn parse_lsof_output(
    output: &str,
    ports: &[u16],
    include_tcp: bool,
    include_udp: bool,
) -> Vec<ProcessInfo> {
    let requested = ports.iter().copied().collect::<BTreeSet<u16>>();
    let mut processes = Vec::new();

    for line in output.lines().skip(1) {
        let parts = line.split_whitespace().collect::<Vec<&str>>();
        if parts.len() < 9 {
            continue;
        }

        let protocol = if line.contains(" TCP ") && include_tcp {
            Protocol::Tcp
        } else if line.contains(" UDP ") && include_udp {
            Protocol::Udp
        } else {
            continue;
        };

        let Some(port) = parts
            .iter()
            .find_map(|part| port_from_address(part, &requested))
        else {
            continue;
        };

        if protocol == Protocol::Tcp && !line.contains("(LISTEN)") {
            continue;
        }

        let Some(pid) = parts.get(1).and_then(|value| value.parse::<u32>().ok()) else {
            continue;
        };

        processes.push(ProcessInfo {
            port,
            pid,
            protocol,
            command: parts.first().map(|value| (*value).to_string()),
        });
    }

    sort_and_dedup_processes(processes)
}

pub fn sort_and_dedup_processes(processes: Vec<ProcessInfo>) -> Vec<ProcessInfo> {
    let mut by_identity = BTreeMap::<(u16, u32, Protocol), Option<String>>::new();

    for process in processes {
        let command = by_identity
            .entry((process.port, process.pid, process.protocol))
            .or_insert(None);
        if command.is_none() && process.command.is_some() {
            *command = process.command;
        }
    }

    by_identity
        .into_iter()
        .map(|((port, pid, protocol), command)| ProcessInfo {
            port,
            pid,
            protocol,
            command,
        })
        .collect()
}

fn port_from_address(address: &str, requested: &BTreeSet<u16>) -> Option<u16> {
    let value =
        address.trim_matches(|character: char| matches!(character, ',' | ')' | '(' | '[' | ']'));
    let (_, tail) = value.rsplit_once(':')?;
    let digits = tail
        .chars()
        .take_while(|character| character.is_ascii_digit())
        .collect::<String>();
    let port = digits.parse::<u16>().ok()?;

    requested.contains(&port).then_some(port)
}

fn extract_pids(line: &str) -> Vec<u32> {
    let mut pids = Vec::new();
    let mut rest = line;

    while let Some(index) = rest.find("pid=") {
        let start = index + 4;
        let pid = rest[start..]
            .chars()
            .take_while(|character| character.is_ascii_digit())
            .collect::<String>();

        if let Ok(pid) = pid.parse::<u32>() {
            pids.push(pid);
        }

        rest = &rest[start..];
    }

    pids
}

fn extract_command_name(line: &str, pid: u32) -> Option<String> {
    let marker = format!("pid={pid}");
    let pid_index = line.find(&marker)?;
    let prefix = &line[..pid_index];
    let end_quote = prefix.rfind('"')?;
    let start_quote = prefix[..end_quote].rfind('"')?;
    Some(prefix[start_quote + 1..end_quote].to_string())
}
