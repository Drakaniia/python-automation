use magic::process::{KillOutcome, KillResult};
use magic::scanner::{ProcessInfo, Protocol};
use magic::tui::app::{App, AppMode};

fn process(port: u16, pid: u32) -> ProcessInfo {
    ProcessInfo::new(port, pid, Protocol::Tcp).with_command("node")
}

#[test]
fn arrow_navigation_wraps_through_detected_processes() {
    let mut app = App::with_processes(
        vec![5173, 3000, 8080],
        vec![process(3000, 1), process(5173, 2)],
    );

    assert_eq!(app.selected_pid(), Some(1));

    app.move_down();
    assert_eq!(app.selected_pid(), Some(2));

    app.move_down();
    assert_eq!(app.selected_pid(), Some(1));

    app.move_up();
    assert_eq!(app.selected_pid(), Some(2));
}

#[test]
fn first_and_last_navigation_jump_to_process_boundaries() {
    let mut app = App::with_processes(
        vec![5173, 3000, 8080],
        vec![process(3000, 1), process(5173, 2), process(8080, 3)],
    );

    app.move_last();
    assert_eq!(app.selected_pid(), Some(3));

    app.move_first();
    assert_eq!(app.selected_pid(), Some(1));
}

#[test]
fn selected_processes_are_marked_for_confirmation() {
    let mut app = App::with_processes(
        vec![5173, 3000, 8080],
        vec![process(3000, 1), process(5173, 2)],
    );

    app.toggle_selected();
    app.move_down();
    app.toggle_selected();
    app.request_confirmation();

    assert_eq!(app.selected_pids(), vec![1, 2]);
    assert_eq!(app.mode(), AppMode::ConfirmKill);
}

#[test]
fn marking_a_process_reports_the_changed_selection_count() {
    let mut app = App::with_processes(
        vec![5173, 3000, 8080],
        vec![process(3000, 1), process(5173, 2)],
    );

    app.toggle_selected();
    assert_eq!(app.status(), "Marked PID 1 (1 selected)");

    app.toggle_selected();
    assert_eq!(app.status(), "Unmarked PID 1 (0 selected)");
}

#[test]
fn toggling_all_processes_reports_whether_all_or_none_are_selected() {
    let mut app = App::with_processes(
        vec![5173, 3000, 8080],
        vec![process(3000, 1), process(5173, 2)],
    );

    app.toggle_all();
    assert_eq!(app.status(), "Marked all 2 process(es)");

    app.toggle_all();
    assert_eq!(app.status(), "Cleared all selections");
}

#[test]
fn confirmation_targets_list_exact_pid_ports_protocols_and_identity() {
    let mut app = App::with_processes(
        vec![3000, 5173],
        vec![
            ProcessInfo::new(3000, 10, Protocol::Tcp)
                .with_command("node")
                .with_command_line("npm run dev")
                .with_executable_path("/usr/bin/node")
                .with_cwd("/workspace/app")
                .with_parent_pid(9),
            ProcessInfo::new(5173, 10, Protocol::Tcp).with_command("node"),
            ProcessInfo::new(8080, 20, Protocol::Tcp).with_command("python"),
        ],
    );

    app.toggle_selected();
    app.request_confirmation();

    let targets = app.confirmation_targets();
    assert_eq!(targets.len(), 1);
    assert_eq!(targets[0].pid, 10);
    assert_eq!(targets[0].ports, vec![3000, 5173]);
    assert_eq!(targets[0].protocols, vec![Protocol::Tcp]);
    assert_eq!(targets[0].command.as_deref(), Some("node"));
    assert_eq!(targets[0].command_line.as_deref(), Some("npm run dev"));
    assert_eq!(targets[0].executable_path.as_deref(), Some("/usr/bin/node"));
    assert_eq!(targets[0].cwd.as_deref(), Some("/workspace/app"));
    assert_eq!(targets[0].parent_pid, Some(9));
}

#[test]
fn post_kill_results_survive_automatic_process_refresh() {
    let mut app = App::with_processes(vec![3000], vec![process(3000, 10)]);

    app.set_kill_results(vec![KillResult {
        pid: 10,
        outcome: KillOutcome::Failed {
            message: "access denied".to_string(),
        },
    }]);
    app.refresh_processes_after_kill(Vec::new());

    assert_eq!(app.mode(), AppMode::Error);
    assert_eq!(app.status(), "1 termination(s) failed");
    assert_eq!(app.last_results().len(), 1);
}

#[test]
fn selected_process_stays_inside_visible_range_for_small_terminals() {
    let processes = (0u16..10)
        .map(|index| process(3000 + index, u32::from(index) + 10))
        .collect::<Vec<_>>();
    let mut app = App::with_processes(vec![3000], processes);

    for _ in 0..5 {
        app.move_down();
    }

    assert_eq!(app.selected_index(), 5);
    assert_eq!(app.visible_process_range(3), 3..6);
}
