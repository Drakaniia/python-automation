use std::collections::BTreeMap;
use std::process::Command;

use super::{ProcessInfo, parse_windows_netstat, sort_and_dedup_processes};

pub fn scan_ports(
    ports: &[u16],
    include_tcp: bool,
    include_udp: bool,
) -> Result<Vec<ProcessInfo>, String> {
    let output = Command::new("netstat")
        .args(["-ano"])
        .output()
        .map_err(|error| format!("failed to run netstat: {error}"))?;

    if !output.status.success() {
        return Err("netstat exited with a non-zero status".to_string());
    }

    let stdout = String::from_utf8_lossy(&output.stdout);
    let mut processes = parse_windows_netstat(&stdout, ports, include_tcp, include_udp);
    let names = load_process_names();

    for process in &mut processes {
        if let Some(name) = names.get(&process.pid) {
            process.command = Some(name.clone());
        }
    }

    Ok(sort_and_dedup_processes(processes))
}

fn load_process_names() -> BTreeMap<u32, String> {
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
