use ratatui::style::{Color, Modifier, Style};

pub fn title() -> Style {
    Style::default()
        .fg(Color::Cyan)
        .add_modifier(Modifier::BOLD)
}

pub fn status() -> Style {
    Style::default().fg(Color::Yellow)
}

pub fn busy() -> Style {
    Style::default()
        .fg(Color::LightYellow)
        .add_modifier(Modifier::BOLD)
}

pub fn success() -> Style {
    Style::default().fg(Color::Green)
}

pub fn danger() -> Style {
    Style::default().fg(Color::Red).add_modifier(Modifier::BOLD)
}

pub fn muted() -> Style {
    Style::default().fg(Color::DarkGray)
}

pub fn value() -> Style {
    Style::default().fg(Color::White)
}

pub fn focus() -> Style {
    Style::default()
        .fg(Color::Cyan)
        .add_modifier(Modifier::BOLD)
}

pub fn panel() -> Style {
    Style::default().fg(Color::Gray)
}

pub fn table_header() -> Style {
    Style::default()
        .fg(Color::Gray)
        .add_modifier(Modifier::BOLD)
}

pub fn selected() -> Style {
    Style::default()
        .bg(Color::Blue)
        .fg(Color::White)
        .add_modifier(Modifier::BOLD)
}

pub fn marked() -> Style {
    Style::default().fg(Color::LightMagenta)
}
