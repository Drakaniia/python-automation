use std::collections::BTreeMap;
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
    pub tree: bool,
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

        native_terminate(request.pid, request.mode, request.tree).map_err(TerminationError::new)
    }
}

pub fn terminate_with_fallback(
    terminator: &mut impl Terminator,
    pid: u32,
    allow_force_fallback: bool,
) -> KillResult {
    terminate_with_fallback_internal(terminator, pid, allow_force_fallback, false)
}

pub fn terminate_tree_with_fallback(
    terminator: &mut impl Terminator,
    pid: u32,
    allow_force_fallback: bool,
) -> KillResult {
    terminate_with_fallback_internal(terminator, pid, allow_force_fallback, true)
}

fn terminate_with_fallback_internal(
    terminator: &mut impl Terminator,
    pid: u32,
    allow_force_fallback: bool,
    tree: bool,
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
        tree,
    }) {
        Ok(()) => KillResult {
            pid,
            outcome: KillOutcome::Killed { used_force: false },
        },
        Err(error) if allow_force_fallback => match terminator.terminate(KillRequest {
            pid,
            mode: KillMode::Force,
            tree,
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
    terminate_force_internal(terminator, pid, false)
}

pub fn terminate_force_tree(terminator: &mut impl Terminator, pid: u32) -> KillResult {
    terminate_force_internal(terminator, pid, true)
}

fn terminate_force_internal(terminator: &mut impl Terminator, pid: u32, tree: bool) -> KillResult {
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
        tree,
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
    terminate_many_with_fallback_internal(terminator, pids, allow_force_fallback, false)
}

pub fn terminate_many_with_fallback_tree(
    terminator: &mut impl Terminator,
    pids: &[u32],
    allow_force_fallback: bool,
) -> Vec<KillResult> {
    terminate_many_with_fallback_internal(terminator, pids, allow_force_fallback, true)
}

fn terminate_many_with_fallback_internal(
    terminator: &mut impl Terminator,
    pids: &[u32],
    allow_force_fallback: bool,
    tree: bool,
) -> Vec<KillResult> {
    pids.iter()
        .map(|pid| terminate_with_fallback_internal(terminator, *pid, allow_force_fallback, tree))
        .collect()
}

fn is_protected_pid(pid: u32) -> bool {
    pid == 0 || pid == 1 || pid == std::process::id() || cfg!(windows) && pid == 4
}

pub fn collect_process_tree(root_pid: u32, relationships: &[(u32, u32)]) -> Vec<u32> {
    let mut children = BTreeMap::<u32, Vec<u32>>::new();
    for (pid, parent_pid) in relationships {
        children.entry(*parent_pid).or_default().push(*pid);
    }
    for child_pids in children.values_mut() {
        child_pids.sort_unstable();
    }

    let mut ordered = Vec::new();
    collect_tree_postorder(root_pid, &children, &mut ordered);
    ordered
}

fn collect_tree_postorder(pid: u32, children: &BTreeMap<u32, Vec<u32>>, ordered: &mut Vec<u32>) {
    if let Some(child_pids) = children.get(&pid) {
        for child_pid in child_pids {
            collect_tree_postorder(*child_pid, children, ordered);
        }
    }
    ordered.push(pid);
}

#[cfg(windows)]
fn native_terminate(pid: u32, mode: KillMode, tree: bool) -> Result<(), String> {
    windows::terminate(pid, mode, tree)
}

#[cfg(unix)]
fn native_terminate(pid: u32, mode: KillMode, tree: bool) -> Result<(), String> {
    unix::terminate(pid, mode, tree)
}
