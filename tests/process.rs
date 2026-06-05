use magic::process::{
    KillMode, KillOutcome, KillRequest, KillResult, TerminationError, Terminator,
    collect_process_tree, terminate_tree_with_fallback, terminate_with_fallback,
};

#[derive(Default)]
struct ScriptedTerminator {
    calls: Vec<KillRequest>,
}

impl Terminator for ScriptedTerminator {
    fn terminate(&mut self, request: KillRequest) -> Result<(), TerminationError> {
        self.calls.push(request);
        match request.mode {
            KillMode::Graceful => Err(TerminationError::new("still running")),
            KillMode::Force => Ok(()),
        }
    }
}

#[test]
fn graceful_failure_falls_back_to_force_kill() {
    let mut terminator = ScriptedTerminator::default();

    let result = terminate_with_fallback(&mut terminator, 42, true);

    assert_eq!(
        result,
        KillResult {
            pid: 42,
            outcome: KillOutcome::Killed { used_force: true },
        }
    );
    assert_eq!(
        terminator.calls,
        vec![
            KillRequest {
                pid: 42,
                mode: KillMode::Graceful,
                tree: false,
            },
            KillRequest {
                pid: 42,
                mode: KillMode::Force,
                tree: false,
            },
        ]
    );
}

#[test]
fn tree_termination_passes_tree_flag_to_graceful_and_force_fallback() {
    let mut terminator = ScriptedTerminator::default();

    let result = terminate_tree_with_fallback(&mut terminator, 42, true);

    assert_eq!(
        result,
        KillResult {
            pid: 42,
            outcome: KillOutcome::Killed { used_force: true },
        }
    );
    assert_eq!(
        terminator.calls,
        vec![
            KillRequest {
                pid: 42,
                mode: KillMode::Graceful,
                tree: true,
            },
            KillRequest {
                pid: 42,
                mode: KillMode::Force,
                tree: true,
            },
        ]
    );
}

#[test]
fn process_tree_signal_order_is_children_before_parent() {
    let relationships = vec![(10, 1), (11, 10), (12, 10), (13, 11), (20, 1)];

    assert_eq!(
        collect_process_tree(10, &relationships),
        vec![13, 11, 12, 10]
    );
}
