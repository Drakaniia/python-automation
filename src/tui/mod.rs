pub mod app;
mod theme;
mod view;

use std::io;
use std::time::Duration;

use crossterm::event::{self, Event, KeyCode, KeyEventKind};
use crossterm::execute;
use crossterm::terminal::{
    EnterAlternateScreen, LeaveAlternateScreen, disable_raw_mode, enable_raw_mode,
};
use ratatui::Terminal;
use ratatui::backend::CrosstermBackend;

use crate::cli::ResolvedConfig;
use crate::process::{NativeTerminator, terminate_force, terminate_many_with_fallback};
use crate::scanner::scan_ports;

use self::app::{App, AppMode};

pub fn run(config: ResolvedConfig) -> Result<(), String> {
    enable_raw_mode().map_err(|error| format!("failed to enable raw mode: {error}"))?;
    let mut stdout = io::stdout();
    execute!(stdout, EnterAlternateScreen)
        .map_err(|error| format!("failed to enter alternate screen: {error}"))?;

    let backend = CrosstermBackend::new(stdout);
    let mut terminal =
        Terminal::new(backend).map_err(|error| format!("failed to open terminal: {error}"))?;

    let result = run_loop(&mut terminal, config);

    disable_raw_mode().map_err(|error| format!("failed to disable raw mode: {error}"))?;
    execute!(terminal.backend_mut(), LeaveAlternateScreen)
        .map_err(|error| format!("failed to leave alternate screen: {error}"))?;
    terminal
        .show_cursor()
        .map_err(|error| format!("failed to restore cursor: {error}"))?;

    result
}

fn run_loop(
    terminal: &mut Terminal<CrosstermBackend<io::Stdout>>,
    config: ResolvedConfig,
) -> Result<(), String> {
    let mut app = App::new(config.ports.clone());
    rescan(terminal, &mut app, &config)?;

    loop {
        draw(terminal, &app)?;

        if app.should_quit() {
            return Ok(());
        }

        if !event::poll(Duration::from_millis(80))
            .map_err(|error| format!("failed to poll terminal input: {error}"))?
        {
            app.tick();
            continue;
        }

        let Event::Key(key) =
            event::read().map_err(|error| format!("failed to read terminal input: {error}"))?
        else {
            continue;
        };

        if key.kind == KeyEventKind::Release {
            continue;
        }

        match (app.mode(), key.code) {
            (_, KeyCode::Char('q') | KeyCode::Esc) => app.quit(),
            (_, KeyCode::Char('r')) => rescan(terminal, &mut app, &config)?,
            (AppMode::Browsing | AppMode::Done, KeyCode::Down) => app.move_down(),
            (AppMode::Browsing | AppMode::Done, KeyCode::Up) => app.move_up(),
            (AppMode::Browsing | AppMode::Done, KeyCode::Char(' ')) => app.toggle_selected(),
            (AppMode::Browsing | AppMode::Done, KeyCode::Char('a')) => app.toggle_all(),
            (AppMode::Browsing | AppMode::Done, KeyCode::Enter) => app.request_confirmation(),
            (AppMode::ConfirmKill, KeyCode::Char('n')) => app.cancel_confirmation(),
            (AppMode::ConfirmKill, KeyCode::Char('y')) => {
                kill_selected(terminal, &mut app, &config, false)?
            }
            (AppMode::ConfirmKill, KeyCode::Char('f')) => {
                kill_selected(terminal, &mut app, &config, true)?
            }
            _ => {}
        }
    }
}

fn draw(terminal: &mut Terminal<CrosstermBackend<io::Stdout>>, app: &App) -> Result<(), String> {
    terminal
        .draw(|frame| view::render(frame, app))
        .map(|_| ())
        .map_err(|error| format!("failed to draw TUI: {error}"))
}

fn rescan(
    terminal: &mut Terminal<CrosstermBackend<io::Stdout>>,
    app: &mut App,
    config: &ResolvedConfig,
) -> Result<(), String> {
    app.start_scanning();
    draw(terminal, app)?;
    match scan_ports(&config.ports, config.tcp, config.udp) {
        Ok(processes) => app.set_processes(processes),
        Err(error) => app.set_error(error),
    }
    Ok(())
}

fn kill_selected(
    terminal: &mut Terminal<CrosstermBackend<io::Stdout>>,
    app: &mut App,
    config: &ResolvedConfig,
    force_now: bool,
) -> Result<(), String> {
    let pids = app.selected_pids();
    if pids.is_empty() {
        app.cancel_confirmation();
        return Ok(());
    }

    app.start_killing();
    draw(terminal, app)?;
    let mut terminator = NativeTerminator;
    let force = force_now || config.force;
    let results = if force {
        pids.into_iter()
            .map(|pid| terminate_force(&mut terminator, pid))
            .collect()
    } else {
        terminate_many_with_fallback(&mut terminator, &pids, true)
    };

    app.set_kill_results(results);
    rescan(terminal, app, config)
}
