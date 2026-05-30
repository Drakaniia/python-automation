use std::process::Command;
use std::thread;
use std::time::Duration;

use super::KillMode;

pub fn terminate(pid: u32, mode: KillMode) -> Result<(), String> {
    let signal = match mode {
        KillMode::Graceful => "-TERM",
        KillMode::Force => "-KILL",
    };

    let output = Command::new("kill")
        .args([signal, &pid.to_string()])
        .output()
        .map_err(|error| format!("failed to run kill: {error}"))?;

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
