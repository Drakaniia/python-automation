use std::fs;
use std::path::PathBuf;
use std::process::Command;

use super::{
    ProcessInfo, ScanAttempt, ScanReport, combine_scan_attempts, parse_lsof_output,
    parse_ss_output, sort_and_dedup_processes,
};

pub fn scan_ports_report(
    ports: &[u16],
    include_tcp: bool,
    include_udp: bool,
) -> Result<ScanReport, String> {
    let lsof = scan_with_lsof(ports, include_tcp, include_udp);
    let ss = match &lsof {
        ScanAttempt::Found { .. } => None,
        _ => Some(scan_with_ss(ports, include_tcp, include_udp)),
    };

    let mut attempts = vec![lsof];
    if let Some(ss) = ss {
        attempts.push(ss);
    }

    let mut report = combine_scan_attempts(attempts);
    enrich_processes(&mut report.processes);
    report.processes = sort_and_dedup_processes(report.processes);
    Ok(report)
}

fn scan_with_lsof(ports: &[u16], include_tcp: bool, include_udp: bool) -> ScanAttempt {
    let mut args = vec!["-nP".to_string()];

    for port in ports {
        if include_tcp {
            args.push(format!("-iTCP:{port}"));
            args.push("-sTCP:LISTEN".to_string());
        }
        if include_udp {
            args.push(format!("-iUDP:{port}"));
        }
    }

    let output = match Command::new("lsof").args(args).output() {
        Ok(output) => output,
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => {
            return ScanAttempt::unavailable("lsof", "not found");
        }
        Err(error) => return ScanAttempt::unavailable("lsof", format!("failed to run: {error}")),
    };

    let stdout = String::from_utf8_lossy(&output.stdout);
    let processes = parse_lsof_output(&stdout, ports, include_tcp, include_udp);
    if !processes.is_empty() {
        return ScanAttempt::found("lsof", processes);
    }

    if output.status.success() {
        return ScanAttempt::empty("lsof");
    }

    let stderr = non_empty_stderr(&output.stderr);
    if stderr.is_empty() {
        ScanAttempt::empty("lsof")
    } else if is_permission_message(&stderr) {
        ScanAttempt::permission_limited("lsof", stderr)
    } else {
        ScanAttempt::unavailable("lsof", stderr)
    }
}

fn scan_with_ss(ports: &[u16], include_tcp: bool, include_udp: bool) -> ScanAttempt {
    let mut args = vec!["-l", "-n", "-p"];
    if include_tcp {
        args.push("-t");
    }
    if include_udp {
        args.push("-u");
    }

    let output = match Command::new("ss").args(args).output() {
        Ok(output) => output,
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => {
            return ScanAttempt::unavailable("ss", "not found");
        }
        Err(error) => return ScanAttempt::unavailable("ss", format!("failed to run: {error}")),
    };

    let stdout = String::from_utf8_lossy(&output.stdout);
    let processes = parse_ss_output(&stdout, ports, include_tcp, include_udp);
    if !processes.is_empty() {
        return ScanAttempt::found("ss", processes);
    }

    if output.status.success() {
        return ScanAttempt::empty("ss");
    }

    let stderr = non_empty_stderr(&output.stderr);
    if stderr.is_empty() {
        ScanAttempt::empty("ss")
    } else if is_permission_message(&stderr) {
        ScanAttempt::permission_limited("ss", stderr)
    } else {
        ScanAttempt::unavailable("ss", stderr)
    }
}

fn enrich_processes(processes: &mut [ProcessInfo]) {
    for process in processes {
        enrich_process(process);
    }
}

#[cfg(target_os = "linux")]
fn enrich_process(process: &mut ProcessInfo) {
    let root = PathBuf::from("/proc").join(process.pid.to_string());
    if process.command_line.is_none() {
        if let Ok(bytes) = fs::read(root.join("cmdline")) {
            let parts = bytes
                .split(|byte| *byte == 0)
                .filter(|part| !part.is_empty())
                .map(|part| String::from_utf8_lossy(part).to_string())
                .collect::<Vec<_>>();
            if !parts.is_empty() {
                process.command_line = Some(parts.join(" "));
            }
        }
    }

    if process.executable_path.is_none() {
        if let Ok(path) = fs::read_link(root.join("exe")) {
            process.executable_path = Some(path.display().to_string());
        }
    }

    if process.cwd.is_none() {
        if let Ok(path) = fs::read_link(root.join("cwd")) {
            process.cwd = Some(path.display().to_string());
        }
    }

    if process.parent_pid.is_none() {
        if let Ok(stat) = fs::read_to_string(root.join("stat")) {
            process.parent_pid = parse_linux_ppid(&stat);
        }
    }
}

#[cfg(not(target_os = "linux"))]
fn enrich_process(process: &mut ProcessInfo) {
    let Ok(output) = Command::new("ps")
        .args([
            "-p",
            &process.pid.to_string(),
            "-o",
            "ppid=",
            "-o",
            "command=",
        ])
        .output()
    else {
        return;
    };

    if !output.status.success() {
        return;
    }

    let text = String::from_utf8_lossy(&output.stdout);
    let Some(line) = text.lines().find(|line| !line.trim().is_empty()) else {
        return;
    };

    let mut parts = line.trim().splitn(2, char::is_whitespace);
    if process.parent_pid.is_none() {
        process.parent_pid = parts
            .next()
            .and_then(|part| part.trim().parse::<u32>().ok());
    }
    if process.command_line.is_none() {
        process.command_line = parts
            .next()
            .map(str::trim)
            .filter(|value| !value.is_empty())
            .map(str::to_string);
    }
}

#[cfg(target_os = "linux")]
fn parse_linux_ppid(stat: &str) -> Option<u32> {
    let close = stat.rfind(") ")?;
    let after_command = &stat[close + 2..];
    let mut parts = after_command.split_whitespace();
    let _state = parts.next()?;
    parts.next()?.parse::<u32>().ok()
}

fn is_permission_message(message: &str) -> bool {
    let lower = message.to_ascii_lowercase();
    lower.contains("permission")
        || lower.contains("not permitted")
        || lower.contains("access denied")
}

fn non_empty_stderr(stderr: &[u8]) -> String {
    String::from_utf8_lossy(stderr).trim().to_string()
}
