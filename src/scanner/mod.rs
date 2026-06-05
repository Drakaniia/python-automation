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
    pub command_line: Option<String>,
    pub executable_path: Option<String>,
    pub cwd: Option<String>,
    pub parent_pid: Option<u32>,
}

impl ProcessInfo {
    pub fn new(port: u16, pid: u32, protocol: Protocol) -> Self {
        Self {
            port,
            pid,
            protocol,
            command: None,
            command_line: None,
            executable_path: None,
            cwd: None,
            parent_pid: None,
        }
    }

    pub fn with_command(mut self, command: impl Into<String>) -> Self {
        self.command = Some(command.into());
        self
    }

    pub fn with_command_line(mut self, command_line: impl Into<String>) -> Self {
        self.command_line = Some(command_line.into());
        self
    }

    pub fn with_executable_path(mut self, executable_path: impl Into<String>) -> Self {
        self.executable_path = Some(executable_path.into());
        self
    }

    pub fn with_cwd(mut self, cwd: impl Into<String>) -> Self {
        self.cwd = Some(cwd.into());
        self
    }

    pub fn with_parent_pid(mut self, parent_pid: u32) -> Self {
        self.parent_pid = Some(parent_pid);
        self
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub enum ScanStatus {
    Found,
    NoListeners,
    Unavailable { message: String },
    PermissionLimited { message: String },
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct ScanReport {
    pub processes: Vec<ProcessInfo>,
    pub status: ScanStatus,
}

impl ScanReport {
    pub fn from_processes(processes: Vec<ProcessInfo>) -> Self {
        let status = if processes.is_empty() {
            ScanStatus::NoListeners
        } else {
            ScanStatus::Found
        };

        Self { processes, status }
    }

    pub fn guidance(&self) -> String {
        match &self.status {
            ScanStatus::Found => "listeners found".to_string(),
            ScanStatus::NoListeners => "no listeners found".to_string(),
            ScanStatus::Unavailable { message } => {
                format!("{message}. Install lsof or ss, or verify they are available on PATH.")
            }
            ScanStatus::PermissionLimited { message } => {
                format!(
                    "{message}. Scanner output may be incomplete; try elevated permissions or inspect the port with system tools."
                )
            }
        }
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub enum ScanAttempt {
    Found {
        tool: String,
        processes: Vec<ProcessInfo>,
    },
    Empty {
        tool: String,
    },
    Unavailable {
        tool: String,
        message: String,
    },
    PermissionLimited {
        tool: String,
        message: String,
    },
}

impl ScanAttempt {
    pub fn found(tool: impl Into<String>, processes: Vec<ProcessInfo>) -> Self {
        Self::Found {
            tool: tool.into(),
            processes,
        }
    }

    pub fn empty(tool: impl Into<String>) -> Self {
        Self::Empty { tool: tool.into() }
    }

    pub fn unavailable(tool: impl Into<String>, message: impl Into<String>) -> Self {
        Self::Unavailable {
            tool: tool.into(),
            message: message.into(),
        }
    }

    pub fn permission_limited(tool: impl Into<String>, message: impl Into<String>) -> Self {
        Self::PermissionLimited {
            tool: tool.into(),
            message: message.into(),
        }
    }
}

pub fn scan_ports(
    ports: &[u16],
    include_tcp: bool,
    include_udp: bool,
) -> Result<Vec<ProcessInfo>, String> {
    let report = scan_ports_report(ports, include_tcp, include_udp)?;
    match report.status {
        ScanStatus::Found | ScanStatus::NoListeners => Ok(report.processes),
        ScanStatus::Unavailable { .. } | ScanStatus::PermissionLimited { .. } => {
            Err(report.guidance())
        }
    }
}

pub fn scan_ports_report(
    ports: &[u16],
    include_tcp: bool,
    include_udp: bool,
) -> Result<ScanReport, String> {
    if ports.is_empty() {
        return Ok(ScanReport::from_processes(Vec::new()));
    }

    #[cfg(windows)]
    {
        return windows::scan_ports_report(ports, include_tcp, include_udp);
    }

    #[cfg(unix)]
    {
        return unix::scan_ports_report(ports, include_tcp, include_udp);
    }

    #[allow(unreachable_code)]
    Err("this operating system is not supported".to_string())
}

pub fn combine_scan_attempts(attempts: Vec<ScanAttempt>) -> ScanReport {
    let mut processes = Vec::new();
    let mut unavailable = Vec::new();
    let mut permission_limited = Vec::new();
    let mut saw_empty = false;

    for attempt in attempts {
        match attempt {
            ScanAttempt::Found {
                processes: found, ..
            } => processes.extend(found),
            ScanAttempt::Empty { .. } => saw_empty = true,
            ScanAttempt::Unavailable { tool, message } => {
                unavailable.push(format!("{tool}: {message}"));
            }
            ScanAttempt::PermissionLimited { tool, message } => {
                permission_limited.push(format!("{tool}: {message}"));
            }
        }
    }

    let processes = sort_and_dedup_processes(processes);
    if !processes.is_empty() {
        return ScanReport {
            processes,
            status: ScanStatus::Found,
        };
    }

    if !permission_limited.is_empty() {
        return ScanReport {
            processes,
            status: ScanStatus::PermissionLimited {
                message: format!(
                    "scanner permission limited ({})",
                    permission_limited.join("; ")
                ),
            },
        };
    }

    if !unavailable.is_empty() && !saw_empty {
        return ScanReport {
            processes,
            status: ScanStatus::Unavailable {
                message: format!("scanner unavailable ({})", unavailable.join("; ")),
            },
        };
    }

    ScanReport {
        processes,
        status: ScanStatus::NoListeners,
    }
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
            processes.push(ProcessInfo::new(port, pid, protocol));
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
            let mut process = ProcessInfo::new(port, pid, protocol);
            process.command = extract_command_name(line, pid);
            processes.push(process);
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

        let mut process = ProcessInfo::new(port, pid, protocol);
        process.command = parts.first().map(|value| (*value).to_string());
        processes.push(process);
    }

    sort_and_dedup_processes(processes)
}

pub fn sort_and_dedup_processes(processes: Vec<ProcessInfo>) -> Vec<ProcessInfo> {
    let mut by_identity = BTreeMap::<(u16, u32, Protocol), ProcessInfo>::new();

    for process in processes {
        let entry = by_identity
            .entry((process.port, process.pid, process.protocol))
            .or_insert_with(|| ProcessInfo::new(process.port, process.pid, process.protocol));
        merge_identity(entry, process);
    }

    by_identity.into_values().collect()
}

fn merge_identity(target: &mut ProcessInfo, source: ProcessInfo) {
    if target.command.is_none() {
        target.command = source.command;
    }
    if target.command_line.is_none() {
        target.command_line = source.command_line;
    }
    if target.executable_path.is_none() {
        target.executable_path = source.executable_path;
    }
    if target.cwd.is_none() {
        target.cwd = source.cwd;
    }
    if target.parent_pid.is_none() {
        target.parent_pid = source.parent_pid;
    }
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
