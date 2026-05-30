use magic::scanner::{ProcessInfo, Protocol};
use magic::tui::app::{App, AppMode};

fn process(port: u16, pid: u32) -> ProcessInfo {
    ProcessInfo {
        port,
        pid,
        protocol: Protocol::Tcp,
        command: Some("node".to_string()),
    }
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
