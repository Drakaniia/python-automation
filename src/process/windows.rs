use std::process::Command;
use std::thread;
use std::time::Duration;

use super::KillMode;

pub fn terminate(pid: u32, mode: KillMode, tree: bool) -> Result<(), String> {
    let pid_arg = pid.to_string();
    let mut command = Command::new("taskkill");
    command.args(["/PID", &pid_arg]);

    if mode == KillMode::Force {
        command.arg("/F");
    }

    if tree {
        command.arg("/T");
    }

    let output = command
        .output()
        .map_err(|error| format!("failed to run taskkill: {error}"))?;

    if !output.status.success() {
        return Err(non_empty_stderr(&output.stderr));
    }

    if mode == KillMode::Graceful {
        thread::sleep(Duration::from_millis(350));
        if pid_exists(pid) {
            return Err("process still running after graceful termination".to_string());
        }
    }

    Ok(())
}

fn pid_exists(pid: u32) -> bool {
    let filter = format!("PID eq {pid}");
    let Ok(output) = Command::new("tasklist")
        .args(["/FI", &filter, "/NH"])
        .output()
    else {
        return false;
    };

    if !output.status.success() {
        return false;
    }

    let stdout = String::from_utf8_lossy(&output.stdout);
    let pid_text = pid.to_string();
    stdout
        .lines()
        .any(|line| line.split_whitespace().any(|part| part == pid_text))
}

fn non_empty_stderr(stderr: &[u8]) -> String {
    let message = String::from_utf8_lossy(stderr).trim().to_string();
    if message.is_empty() {
        "termination command failed".to_string()
    } else {
        message
    }
}
