use ratatui::Frame;
use ratatui::layout::{Constraint, Direction, Layout, Rect};
use ratatui::style::Style;
use ratatui::text::{Line, Span};
use ratatui::widgets::{Block, Borders, Cell, Paragraph, Row, Table, Wrap};

use crate::tui::app::{App, AppMode};

use super::theme;

pub fn render(frame: &mut Frame<'_>, app: &App) {
    let area = frame.area();
    let chunks = Layout::default()
        .direction(Direction::Vertical)
        .constraints([
            Constraint::Length(3),
            Constraint::Length(3),
            Constraint::Min(8),
            Constraint::Length(5),
        ])
        .split(area);

    render_header(frame, app, chunks[0]);
    render_status(frame, app, chunks[1]);
    render_processes(frame, app, chunks[2]);
    render_footer(frame, app, chunks[3]);
}

fn render_header(frame: &mut Frame<'_>, app: &App, area: Rect) {
    let ports = app
        .ports()
        .iter()
        .map(u16::to_string)
        .collect::<Vec<String>>()
        .join(", ");
    let marked = marked_count(app);
    let total = app.processes().len();
    let title = Line::from(vec![
        Span::styled("magic", theme::title()),
        Span::raw(" port killer"),
        Span::styled("  ports ", theme::muted()),
        Span::styled(ports, theme::value()),
        Span::styled("  filter ", theme::muted()),
        Span::styled(app.protocol_filter_label(), theme::muted()),
        Span::styled("  listeners ", theme::muted()),
        Span::styled(total.to_string(), theme::value()),
        Span::styled("  marked ", theme::muted()),
        Span::styled(format!("{marked}/{total}"), selection_summary_style(marked)),
    ]);

    frame.render_widget(
        Paragraph::new(title).block(Block::default().borders(Borders::ALL)),
        area,
    );
}

fn render_status(frame: &mut Frame<'_>, app: &App, area: Rect) {
    let spinner = ["-", "\\", "|", "/"][app.tick_index() % 4];
    let mode = match app.mode() {
        AppMode::Scanning => Span::styled(format!("{spinner} scanning"), theme::busy()),
        AppMode::Browsing => Span::styled("ready", theme::success()),
        AppMode::ConfirmKill => Span::styled("confirm", theme::danger()),
        AppMode::Killing => Span::styled(format!("{spinner} killing"), theme::danger()),
        AppMode::Done => Span::styled("done", theme::success()),
        AppMode::Error => Span::styled("error", theme::danger()),
    };

    frame.render_widget(
        Paragraph::new(Line::from(vec![
            mode,
            Span::raw("  "),
            Span::styled(app.status().to_string(), theme::status()),
        ]))
        .block(
            Block::default()
                .title("Status")
                .borders(Borders::ALL)
                .border_style(status_border_style(app.mode())),
        ),
        area,
    );
}

fn render_processes(frame: &mut Frame<'_>, app: &App, area: Rect) {
    if app.mode() == AppMode::ConfirmKill {
        render_confirmation(frame, app, area);
        return;
    }

    if app.processes().is_empty() {
        frame.render_widget(
            Paragraph::new(format!(
                "{}. Press r to scan again or q to quit.",
                app.status()
            ))
            .style(theme::muted())
            .wrap(Wrap { trim: true })
            .block(Block::default().title("Processes").borders(Borders::ALL)),
            area,
        );
        return;
    }

    if area.width >= 96 {
        let chunks = Layout::default()
            .direction(Direction::Horizontal)
            .constraints([Constraint::Percentage(68), Constraint::Percentage(32)])
            .split(area);
        render_process_table(frame, app, chunks[0]);
        render_process_inspector(frame, app, chunks[1]);
    } else {
        render_process_table(frame, app, area);
    }
}

fn render_process_table(frame: &mut Frame<'_>, app: &App, area: Rect) {
    let header =
        Row::new(["State", "Port", "PID", "Proto", "Command"]).style(theme::table_header());
    let visible_capacity = area.height.saturating_sub(3) as usize;
    let range = app.visible_process_range(visible_capacity);
    let rows = app.processes()[range.clone()]
        .iter()
        .enumerate()
        .map(|(offset, process)| {
            let index = range.start + offset;
            let cursor = if index == app.selected_index() {
                ">"
            } else {
                " "
            };
            let checkbox = if app.is_marked(process.pid) {
                "[x]"
            } else {
                "[ ]"
            };
            let marker = format!("{cursor} {checkbox}");
            let style = if index == app.selected_index() {
                theme::selected()
            } else if app.is_marked(process.pid) {
                theme::marked()
            } else {
                Style::default()
            };

            Row::new(vec![
                Cell::from(marker),
                Cell::from(process.port.to_string()),
                Cell::from(process.pid.to_string()),
                Cell::from(process.protocol.to_string()),
                Cell::from(display_command(process)),
            ])
            .style(style)
        });
    let title = if app.processes().len() > range.len() {
        format!(
            "Listeners {}-{} of {}",
            range.start + 1,
            range.end,
            app.processes().len()
        )
    } else {
        "Listeners".to_string()
    };

    let table = Table::new(
        rows,
        [
            Constraint::Length(7),
            Constraint::Length(8),
            Constraint::Length(8),
            Constraint::Length(8),
            Constraint::Min(12),
        ],
    )
    .header(header)
    .block(
        Block::default()
            .title(title)
            .borders(Borders::ALL)
            .border_style(theme::focus()),
    );

    frame.render_widget(table, area);
}

fn render_process_inspector(frame: &mut Frame<'_>, app: &App, area: Rect) {
    let lines = match app.processes().get(app.selected_index()) {
        Some(process) => vec![
            Line::from(vec![
                Span::styled("PID ", theme::muted()),
                Span::styled(process.pid.to_string(), theme::value()),
            ]),
            Line::from(vec![
                Span::styled("Port ", theme::muted()),
                Span::styled(
                    format!("{}/{}", process.port, process.protocol),
                    theme::value(),
                ),
            ]),
            Line::from(vec![
                Span::styled("Marked ", theme::muted()),
                Span::styled(
                    marked_label(app, process.pid),
                    marked_style(app, process.pid),
                ),
            ]),
            Line::from(""),
            Line::from(vec![
                Span::styled("Command ", theme::muted()),
                Span::styled(display_command(process), theme::value()),
            ]),
            Line::from(vec![
                Span::styled("CWD ", theme::muted()),
                Span::raw(optional_value(process.cwd.as_deref())),
            ]),
            Line::from(vec![
                Span::styled("Exec ", theme::muted()),
                Span::raw(optional_value(process.executable_path.as_deref())),
            ]),
            Line::from(vec![
                Span::styled("Parent ", theme::muted()),
                Span::raw(
                    process
                        .parent_pid
                        .map(|pid| pid.to_string())
                        .unwrap_or_else(|| "-".to_string()),
                ),
            ]),
        ],
        None => vec![Line::from("No process selected")],
    };

    frame.render_widget(
        Paragraph::new(lines).wrap(Wrap { trim: true }).block(
            Block::default()
                .title("Selected Process")
                .borders(Borders::ALL)
                .border_style(theme::panel()),
        ),
        area,
    );
}

fn render_confirmation(frame: &mut Frame<'_>, app: &App, area: Rect) {
    let chunks = Layout::default()
        .direction(Direction::Vertical)
        .constraints([Constraint::Length(4), Constraint::Min(5)])
        .split(area);
    let target_count = app.confirmation_targets().len();

    frame.render_widget(
        Paragraph::new(vec![
            Line::from(vec![
                Span::styled("Kill Review", theme::danger()),
                Span::raw("  "),
                Span::styled(format!("selected {target_count}"), theme::danger()),
            ]),
            Line::from(vec![Span::styled(
                "Review exact PIDs, ports, and commands before terminating.",
                theme::muted(),
            )]),
        ])
        .wrap(Wrap { trim: true })
        .block(
            Block::default()
                .borders(Borders::ALL)
                .border_style(theme::danger()),
        ),
        chunks[0],
    );

    let header = Row::new(["PID", "Ports", "Proto", "Command"]).style(theme::table_header());
    let rows = app.confirmation_targets().into_iter().map(|target| {
        Row::new(vec![
            Cell::from(target.pid.to_string()),
            Cell::from(join_values(&target.ports)),
            Cell::from(
                target
                    .protocols
                    .iter()
                    .map(ToString::to_string)
                    .collect::<Vec<_>>()
                    .join(","),
            ),
            Cell::from(
                target
                    .command_line
                    .or(target.command)
                    .or(target.executable_path)
                    .unwrap_or_else(|| "-".to_string()),
            ),
        ])
    });

    let table = Table::new(
        rows,
        [
            Constraint::Length(8),
            Constraint::Length(14),
            Constraint::Length(10),
            Constraint::Min(20),
        ],
    )
    .header(header)
    .block(
        Block::default()
            .title("Targets")
            .borders(Borders::ALL)
            .border_style(theme::danger()),
    );

    frame.render_widget(table, chunks[1]);
}

fn render_footer(frame: &mut Frame<'_>, app: &App, area: Rect) {
    let mut lines = if app.mode() == AppMode::ConfirmKill {
        vec![Line::from(vec![
            Span::styled("y", theme::danger()),
            Span::raw(" graceful  "),
            Span::styled("f", theme::danger()),
            Span::raw(" force  "),
            Span::styled("n/Esc", theme::title()),
            Span::raw(" cancel  "),
            Span::styled("q", theme::title()),
            Span::raw(" quit"),
        ])]
    } else {
        vec![Line::from(vec![
            Span::styled("Up/Down/j/k", theme::title()),
            Span::raw(" move  "),
            Span::styled("g/G", theme::title()),
            Span::raw(" first/last  "),
            Span::styled("Space", theme::title()),
            Span::raw(" mark  "),
            Span::styled("Enter", theme::title()),
            Span::raw(" review  "),
            Span::styled("a", theme::title()),
            Span::raw(" all  "),
            Span::styled("r", theme::title()),
            Span::raw(" rescan  "),
            Span::styled("q", theme::title()),
            Span::raw(" quit"),
        ])]
    };

    if app.mode() != AppMode::ConfirmKill && !app.last_results().is_empty() {
        lines.extend(
            app.last_results()
                .iter()
                .take(2)
                .map(|result| Line::from(result.to_string())),
        );
    }

    frame.render_widget(
        Paragraph::new(lines)
            .wrap(Wrap { trim: true })
            .block(Block::default().borders(Borders::ALL)),
        area,
    );
}

fn display_command(process: &crate::scanner::ProcessInfo) -> String {
    process
        .command_line
        .as_deref()
        .or(process.command.as_deref())
        .unwrap_or("-")
        .to_string()
}

fn join_values(values: &[u16]) -> String {
    values
        .iter()
        .map(u16::to_string)
        .collect::<Vec<_>>()
        .join(",")
}

fn status_border_style(mode: AppMode) -> Style {
    match mode {
        AppMode::Scanning | AppMode::Killing => theme::busy(),
        AppMode::ConfirmKill | AppMode::Error => theme::danger(),
        AppMode::Browsing | AppMode::Done => theme::focus(),
    }
}

fn marked_count(app: &App) -> usize {
    app.processes()
        .iter()
        .filter(|process| app.is_marked(process.pid))
        .count()
}

fn selection_summary_style(marked: usize) -> Style {
    if marked == 0 {
        theme::muted()
    } else {
        theme::marked()
    }
}

fn marked_label(app: &App, pid: u32) -> &'static str {
    if app.is_marked(pid) { "yes" } else { "no" }
}

fn marked_style(app: &App, pid: u32) -> Style {
    if app.is_marked(pid) {
        theme::marked()
    } else {
        theme::muted()
    }
}

fn optional_value(value: Option<&str>) -> String {
    value.unwrap_or("-").to_string()
}

#[cfg(test)]
mod tests {
    use ratatui::Terminal;
    use ratatui::backend::TestBackend;

    use super::*;
    use crate::scanner::{ProcessInfo, Protocol};

    fn process(port: u16, pid: u32) -> ProcessInfo {
        ProcessInfo::new(port, pid, Protocol::Tcp).with_command("node")
    }

    fn render_to_text(app: &App, width: u16, height: u16) -> String {
        let backend = TestBackend::new(width, height);
        let mut terminal = Terminal::new(backend).expect("test backend should open");
        terminal
            .draw(|frame| render(frame, app))
            .expect("test render should succeed");

        let buffer = terminal.backend().buffer();
        let mut output = String::new();
        for y in 0..buffer.area.height {
            for x in 0..buffer.area.width {
                output.push_str(buffer[(x, y)].symbol());
            }
            output.push('\n');
        }
        output
    }

    #[test]
    fn footer_exposes_arrow_and_vim_navigation() {
        let app = App::with_processes(vec![3000], vec![process(3000, 10)]);

        let output = render_to_text(&app, 100, 18);

        assert!(output.contains("Up/Down/j/k"));
        assert!(output.contains("g/G"));
    }

    #[test]
    fn selected_rows_render_a_cursor_and_checkbox_marker() {
        let mut app =
            App::with_processes(vec![3000, 5173], vec![process(3000, 10), process(5173, 20)]);

        app.toggle_selected();
        let output = render_to_text(&app, 100, 18);

        assert!(output.contains("> [x]"));
        assert!(output.contains("  [ ]"));
    }

    #[test]
    fn browsing_layout_shows_selection_summary_and_selected_process_inspector() {
        let mut app = App::with_processes(
            vec![3000, 5173],
            vec![
                process(3000, 10),
                ProcessInfo::new(5173, 20, Protocol::Tcp)
                    .with_command("node")
                    .with_command_line("npm run dev")
                    .with_executable_path("C:\\nodejs\\node.exe")
                    .with_cwd("C:\\workspace\\app")
                    .with_parent_pid(15),
            ],
        );

        app.move_down();
        app.toggle_selected();
        let output = render_to_text(&app, 120, 22);

        assert!(output.contains("marked 1/2"));
        assert!(output.contains("Selected Process"));
        assert!(output.contains("PID 20"));
        assert!(output.contains("Port 5173/TCP"));
        assert!(output.contains("Marked yes"));
        assert!(output.contains("Command npm run dev"));
        assert!(output.contains("Parent 15"));
    }

    #[test]
    fn confirmation_layout_surfaces_destructive_decision_and_target_count() {
        let mut app =
            App::with_processes(vec![3000, 5173], vec![process(3000, 10), process(5173, 20)]);

        app.toggle_selected();
        app.request_confirmation();
        let output = render_to_text(&app, 120, 22);

        assert!(output.contains("Kill Review"));
        assert!(output.contains("selected 1"));
        assert!(output.contains("Targets"));
        assert!(output.contains("y graceful"));
        assert!(output.contains("f force"));
        assert!(output.contains("n/Esc cancel"));
    }
}
