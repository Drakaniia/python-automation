use magic::process::{
    KillMode, KillOutcome, KillRequest, KillResult, TerminationError, Terminator,
    terminate_with_fallback,
};

#[derive(Default)]
struct ScriptedTerminator {
    calls: Vec<KillMode>,
}

impl Terminator for ScriptedTerminator {
    fn terminate(&mut self, request: KillRequest) -> Result<(), TerminationError> {
        self.calls.push(request.mode);
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
    assert_eq!(terminator.calls, vec![KillMode::Graceful, KillMode::Force]);
}
