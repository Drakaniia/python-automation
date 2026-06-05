use ratatui::Frame;
use ratatui::layout::{Constraint, Direction, Layout};
use ratatui::style::{Modifier, Style};
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

fn render_header(frame: &mut Frame<'_>, app: &App, area: ratatui::layout::Rect) {
    let ports = app
        .ports()
        .iter()
        .map(u16::to_string)
        .collect::<Vec<String>>()
        .join(", ");
    let title = Line::from(vec![
        Span::styled("magic", theme::title()),
        Span::raw(" port killer "),
        Span::styled(format!("[{ports}]"), theme::muted()),
        Span::raw(" "),
        Span::styled(app.protocol_filter_label(), theme::muted()),
    ]);

    frame.render_widget(
        Paragraph::new(title).block(Block::default().borders(Borders::ALL)),
        area,
    );
}

fn render_status(frame: &mut Frame<'_>, app: &App, area: ratatui::layout::Rect) {
    let spinner = ["-", "\\", "|", "/"][app.tick_index() % 4];
    let mode = match app.mode() {
        AppMode::Scanning => Span::styled(format!("{spinner} scanning"), theme::status()),
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
        .block(Block::default().borders(Borders::ALL)),
        area,
    );
}

fn render_processes(frame: &mut Frame<'_>, app: &App, area: ratatui::layout::Rect) {
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

    let header = Row::new(["Sel", "Port", "PID", "Proto", "Command"])
        .style(Style::default().add_modifier(Modifier::BOLD));
    let visible_capacity = area.height.saturating_sub(3) as usize;
    let range = app.visible_process_range(visible_capacity);
    let rows = app.processes()[range.clone()]
        .iter()
        .enumerate()
        .map(|(offset, process)| {
            let index = range.start + offset;
            let marker = if app.is_marked(process.pid) { "*" } else { " " };
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
            "Processes {}-{} of {}",
            range.start + 1,
            range.end,
            app.processes().len()
        )
    } else {
        "Processes".to_string()
    };

    let table = Table::new(
        rows,
        [
            Constraint::Length(5),
            Constraint::Length(8),
            Constraint::Length(8),
            Constraint::Length(8),
            Constraint::Min(12),
        ],
    )
    .header(header)
    .block(Block::default().title(title).borders(Borders::ALL));

    frame.render_widget(table, area);
}

fn render_confirmation(frame: &mut Frame<'_>, app: &App, area: ratatui::layout::Rect) {
    let header = Row::new(["PID", "Ports", "Proto", "Command"])
        .style(Style::default().add_modifier(Modifier::BOLD));
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
            .title("Confirm Kill Targets")
            .borders(Borders::ALL),
    );

    frame.render_widget(table, area);
}

fn render_footer(frame: &mut Frame<'_>, app: &App, area: ratatui::layout::Rect) {
    let mut lines = vec![Line::from(vec![
        Span::styled("Up/Down", theme::title()),
        Span::raw(" navigate  "),
        Span::styled("Space", theme::title()),
        Span::raw(" mark  "),
        Span::styled("Enter", theme::title()),
        Span::raw(" kill  "),
        Span::styled("a", theme::title()),
        Span::raw(" all  "),
        Span::styled("r", theme::title()),
        Span::raw(" rescan  "),
        Span::styled("q", theme::title()),
        Span::raw(" quit"),
    ])];

    if app.mode() == AppMode::ConfirmKill {
        lines.push(Line::from(vec![
            Span::styled("y", theme::danger()),
            Span::raw(" graceful + force fallback  "),
            Span::styled("f", theme::danger()),
            Span::raw(" force now  "),
            Span::styled("n", theme::title()),
            Span::raw(" cancel"),
        ]));
    } else if !app.last_results().is_empty() {
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
