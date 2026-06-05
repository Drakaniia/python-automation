use std::process::Command;
use std::thread;
use std::time::Duration;

use super::{KillMode, collect_process_tree};

pub fn terminate(pid: u32, mode: KillMode, tree: bool) -> Result<(), String> {
    let signal = match mode {
        KillMode::Graceful => "-TERM",
        KillMode::Force => "-KILL",
    };
    let targets = if tree {
        let relationships = current_process_relationships()?;
        collect_process_tree(pid, &relationships)
    } else {
        vec![pid]
    };

    for target_pid in &targets {
        let output = Command::new("kill")
            .args([signal, &target_pid.to_string()])
            .output()
            .map_err(|error| format!("failed to run kill: {error}"))?;

        if !output.status.success() {
            return Err(non_empty_stderr(&output.stderr));
        }
    }

    if mode == KillMode::Graceful {
        thread::sleep(Duration::from_millis(350));
        if targets.iter().any(|target_pid| pid_exists(*target_pid)) {
            return Err("process still running after graceful termination".to_string());
        }
    }

    Ok(())
}

fn pid_exists(pid: u32) -> bool {
    Command::new("kill")
        .args(["-0", &pid.to_string()])
        .status()
        .is_ok_and(|status| status.success())
}

fn non_empty_stderr(stderr: &[u8]) -> String {
    let message = String::from_utf8_lossy(stderr).trim().to_string();
    if message.is_empty() {
        "termination command failed".to_string()
    } else {
        message
    }
}

fn current_process_relationships() -> Result<Vec<(u32, u32)>, String> {
    let output = Command::new("ps")
        .args(["-eo", "pid=,ppid="])
        .output()
        .map_err(|error| format!("failed to inspect process tree with ps: {error}"))?;

    if !output.status.success() {
        return Err(non_empty_stderr(&output.stderr));
    }

    Ok(String::from_utf8_lossy(&output.stdout)
        .lines()
        .filter_map(parse_pid_ppid_line)
        .collect())
}

fn parse_pid_ppid_line(line: &str) -> Option<(u32, u32)> {
    let mut parts = line.split_whitespace();
    let pid = parts.next()?.parse::<u32>().ok()?;
    let parent_pid = parts.next()?.parse::<u32>().ok()?;
    Some((pid, parent_pid))
}
