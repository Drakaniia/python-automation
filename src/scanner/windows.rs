use std::collections::BTreeMap;
use std::process::Command;

use serde_json::Value;

use super::{ScanReport, ScanStatus, parse_windows_netstat, sort_and_dedup_processes};

#[derive(Clone, Debug, Default)]
struct ProcessDetails {
    command: Option<String>,
    command_line: Option<String>,
    executable_path: Option<String>,
    parent_pid: Option<u32>,
}

pub fn scan_ports_report(
    ports: &[u16],
    include_tcp: bool,
    include_udp: bool,
) -> Result<ScanReport, String> {
    let output = match Command::new("netstat").args(["-ano"]).output() {
        Ok(output) => output,
        Err(error) => {
            return Ok(ScanReport {
                processes: Vec::new(),
                status: ScanStatus::Unavailable {
                    message: format!("netstat failed to run: {error}"),
                },
            });
        }
    };

    if !output.status.success() {
        return Ok(ScanReport {
            processes: Vec::new(),
            status: ScanStatus::Unavailable {
                message: "netstat exited with a non-zero status".to_string(),
            },
        });
    }

    let stdout = String::from_utf8_lossy(&output.stdout);
    let mut processes = parse_windows_netstat(&stdout, ports, include_tcp, include_udp);
    let details = load_process_details();

    for process in &mut processes {
        if let Some(details) = details.get(&process.pid) {
            process.command = details.command.clone();
            process.command_line = details.command_line.clone();
            process.executable_path = details.executable_path.clone();
            process.parent_pid = details.parent_pid;
        }
    }

    Ok(ScanReport::from_processes(sort_and_dedup_processes(
        processes,
    )))
}

fn load_process_details() -> BTreeMap<u32, ProcessDetails> {
    let mut details = load_tasklist_names()
        .into_iter()
        .map(|(pid, command)| {
            (
                pid,
                ProcessDetails {
                    command: Some(command),
                    ..ProcessDetails::default()
                },
            )
        })
        .collect::<BTreeMap<_, _>>();

    for (pid, cim_details) in load_cim_process_details() {
        let entry = details.entry(pid).or_default();
        if entry.command_line.is_none() {
            entry.command_line = cim_details.command_line;
        }
        if entry.executable_path.is_none() {
            entry.executable_path = cim_details.executable_path;
        }
        if entry.parent_pid.is_none() {
            entry.parent_pid = cim_details.parent_pid;
        }
    }

    details
}

fn load_tasklist_names() -> BTreeMap<u32, String> {
    let Ok(output) = Command::new("tasklist")
        .args(["/FO", "CSV", "/NH"])
        .output()
    else {
        return BTreeMap::new();
    };

    if !output.status.success() {
        return BTreeMap::new();
    }

    String::from_utf8_lossy(&output.stdout)
        .lines()
        .filter_map(parse_tasklist_csv_line)
        .collect()
}

fn load_cim_process_details() -> BTreeMap<u32, ProcessDetails> {
    let Ok(output) = Command::new("powershell")
        .args([
            "-NoProfile",
            "-Command",
            "Get-CimInstance Win32_Process | Select-Object ProcessId,ParentProcessId,ExecutablePath,CommandLine | ConvertTo-Json -Compress",
        ])
        .output()
    else {
        return BTreeMap::new();
    };

    if !output.status.success() {
        return BTreeMap::new();
    }

    let Ok(value) = serde_json::from_slice::<Value>(&output.stdout) else {
        return BTreeMap::new();
    };

    let values = match value {
        Value::Array(values) => values,
        value => vec![value],
    };

    values
        .into_iter()
        .filter_map(|value| {
            let pid = value.get("ProcessId")?.as_u64()? as u32;
            let parent_pid = value
                .get("ParentProcessId")
                .and_then(Value::as_u64)
                .map(|pid| pid as u32);
            let executable_path = value
                .get("ExecutablePath")
                .and_then(Value::as_str)
                .filter(|value| !value.is_empty())
                .map(str::to_string);
            let command_line = value
                .get("CommandLine")
                .and_then(Value::as_str)
                .filter(|value| !value.is_empty())
                .map(str::to_string);

            Some((
                pid,
                ProcessDetails {
                    command: None,
                    command_line,
                    executable_path,
                    parent_pid,
                },
            ))
        })
        .collect()
}

fn parse_tasklist_csv_line(line: &str) -> Option<(u32, String)> {
    let fields = parse_csv_line(line);
    let name = fields.first()?.trim().to_string();
    let pid = fields.get(1)?.trim().parse::<u32>().ok()?;
    Some((pid, name))
}

fn parse_csv_line(line: &str) -> Vec<String> {
    let mut fields = Vec::new();
    let mut field = String::new();
    let mut in_quotes = false;

    for character in line.chars() {
        match character {
            '"' => in_quotes = !in_quotes,
            ',' if !in_quotes => {
                fields.push(field.clone());
                field.clear();
            }
            _ => field.push(character),
        }
    }

    fields.push(field);
    fields
}
