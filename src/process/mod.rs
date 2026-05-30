use std::fmt;

#[cfg(unix)]
mod unix;
#[cfg(windows)]
mod windows;

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum KillMode {
    Graceful,
    Force,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub struct KillRequest {
    pub pid: u32,
    pub mode: KillMode,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct TerminationError {
    message: String,
}

impl TerminationError {
    pub fn new(message: impl Into<String>) -> Self {
        Self {
            message: message.into(),
        }
    }
}

impl fmt::Display for TerminationError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        formatter.write_str(&self.message)
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub enum KillOutcome {
    Killed { used_force: bool },
    Skipped { reason: String },
    Failed { message: String },
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct KillResult {
    pub pid: u32,
    pub outcome: KillOutcome,
}

impl KillResult {
    pub fn is_failed(&self) -> bool {
        matches!(self.outcome, KillOutcome::Failed { .. })
    }
}

impl fmt::Display for KillResult {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        match &self.outcome {
            KillOutcome::Killed { used_force } if *used_force => {
                write!(formatter, "pid {} killed with force fallback", self.pid)
            }
            KillOutcome::Killed { .. } => write!(formatter, "pid {} killed gracefully", self.pid),
            KillOutcome::Skipped { reason } => {
                write!(formatter, "pid {} skipped: {reason}", self.pid)
            }
            KillOutcome::Failed { message } => {
                write!(formatter, "pid {} failed: {message}", self.pid)
            }
        }
    }
}

pub trait Terminator {
    fn terminate(&mut self, request: KillRequest) -> Result<(), TerminationError>;
}

pub struct NativeTerminator;

impl Terminator for NativeTerminator {
    fn terminate(&mut self, request: KillRequest) -> Result<(), TerminationError> {
        if is_protected_pid(request.pid) {
            return Err(TerminationError::new(
                "refusing to terminate a protected system pid",
            ));
        }

        native_terminate(request.pid, request.mode).map_err(TerminationError::new)
    }
}

pub fn terminate_with_fallback(
    terminator: &mut impl Terminator,
    pid: u32,
    allow_force_fallback: bool,
) -> KillResult {
    if is_protected_pid(pid) {
        return KillResult {
            pid,
            outcome: KillOutcome::Skipped {
                reason: "protected system pid".to_string(),
            },
        };
    }

    match terminator.terminate(KillRequest {
        pid,
        mode: KillMode::Graceful,
    }) {
        Ok(()) => KillResult {
            pid,
            outcome: KillOutcome::Killed { used_force: false },
        },
        Err(error) if allow_force_fallback => match terminator.terminate(KillRequest {
            pid,
            mode: KillMode::Force,
        }) {
            Ok(()) => KillResult {
                pid,
                outcome: KillOutcome::Killed { used_force: true },
            },
            Err(force_error) => KillResult {
                pid,
                outcome: KillOutcome::Failed {
                    message: format!("{error}; force fallback failed: {force_error}"),
                },
            },
        },
        Err(error) => KillResult {
            pid,
            outcome: KillOutcome::Failed {
                message: error.to_string(),
            },
        },
    }
}

pub fn terminate_force(terminator: &mut impl Terminator, pid: u32) -> KillResult {
    if is_protected_pid(pid) {
        return KillResult {
            pid,
            outcome: KillOutcome::Skipped {
                reason: "protected system pid".to_string(),
            },
        };
    }

    match terminator.terminate(KillRequest {
        pid,
        mode: KillMode::Force,
    }) {
        Ok(()) => KillResult {
            pid,
            outcome: KillOutcome::Killed { used_force: true },
        },
        Err(error) => KillResult {
            pid,
            outcome: KillOutcome::Failed {
                message: error.to_string(),
            },
        },
    }
}

pub fn terminate_many_with_fallback(
    terminator: &mut impl Terminator,
    pids: &[u32],
    allow_force_fallback: bool,
) -> Vec<KillResult> {
    pids.iter()
        .map(|pid| terminate_with_fallback(terminator, *pid, allow_force_fallback))
        .collect()
}

fn is_protected_pid(pid: u32) -> bool {
    pid == 0 || pid == 1 || pid == std::process::id() || cfg!(windows) && pid == 4
}

#[cfg(windows)]
fn native_terminate(pid: u32, mode: KillMode) -> Result<(), String> {
    windows::terminate(pid, mode)
}

#[cfg(unix)]
fn native_terminate(pid: u32, mode: KillMode) -> Result<(), String> {
    unix::terminate(pid, mode)
}
