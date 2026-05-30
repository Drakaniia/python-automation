use std::collections::BTreeSet;

use crate::process::KillResult;
use crate::scanner::ProcessInfo;

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum AppMode {
    Scanning,
    Browsing,
    ConfirmKill,
    Killing,
    Done,
    Error,
}

#[derive(Clone, Debug)]
pub struct App {
    ports: Vec<u16>,
    processes: Vec<ProcessInfo>,
    selected_index: usize,
    selected_pids: BTreeSet<u32>,
    mode: AppMode,
    status: String,
    tick: usize,
    should_quit: bool,
    last_results: Vec<KillResult>,
}

impl App {
    pub fn new(ports: Vec<u16>) -> Self {
        Self {
            ports,
            processes: Vec::new(),
            selected_index: 0,
            selected_pids: BTreeSet::new(),
            mode: AppMode::Scanning,
            status: "Scanning ports...".to_string(),
            tick: 0,
            should_quit: false,
            last_results: Vec::new(),
        }
    }

    pub fn with_processes(ports: Vec<u16>, processes: Vec<ProcessInfo>) -> Self {
        let mut app = Self::new(ports);
        app.set_processes(processes);
        app
    }

    pub fn ports(&self) -> &[u16] {
        &self.ports
    }

    pub fn processes(&self) -> &[ProcessInfo] {
        &self.processes
    }

    pub fn mode(&self) -> AppMode {
        self.mode
    }

    pub fn status(&self) -> &str {
        &self.status
    }

    pub fn tick_index(&self) -> usize {
        self.tick
    }

    pub fn last_results(&self) -> &[KillResult] {
        &self.last_results
    }

    pub fn selected_index(&self) -> usize {
        self.selected_index
    }

    pub fn selected_pid(&self) -> Option<u32> {
        self.processes
            .get(self.selected_index)
            .map(|process| process.pid)
    }

    pub fn selected_pids(&self) -> Vec<u32> {
        let mut pids = if self.selected_pids.is_empty() {
            self.selected_pid().into_iter().collect::<Vec<u32>>()
        } else {
            self.selected_pids.iter().copied().collect::<Vec<u32>>()
        };
        pids.sort_unstable();
        pids
    }

    pub fn is_marked(&self, pid: u32) -> bool {
        self.selected_pids.contains(&pid)
    }

    pub fn start_scanning(&mut self) {
        self.mode = AppMode::Scanning;
        self.status = format!("Scanning {}...", join_ports(&self.ports));
    }

    pub fn set_processes(&mut self, processes: Vec<ProcessInfo>) {
        self.processes = processes;
        self.selected_pids
            .retain(|pid| self.processes.iter().any(|process| process.pid == *pid));
        if self.processes.is_empty() {
            self.selected_index = 0;
            self.mode = AppMode::Done;
            self.status = format!("No listeners found on {}", join_ports(&self.ports));
        } else {
            self.selected_index = self.selected_index.min(self.processes.len() - 1);
            self.mode = AppMode::Browsing;
            self.status = format!(
                "Found {} listener(s) on {}",
                self.processes.len(),
                join_ports(&self.ports)
            );
        }
    }

    pub fn set_error(&mut self, message: String) {
        self.mode = AppMode::Error;
        self.status = message;
    }

    pub fn move_down(&mut self) {
        if self.processes.is_empty() {
            return;
        }

        self.selected_index = (self.selected_index + 1) % self.processes.len();
    }

    pub fn move_up(&mut self) {
        if self.processes.is_empty() {
            return;
        }

        self.selected_index = if self.selected_index == 0 {
            self.processes.len() - 1
        } else {
            self.selected_index - 1
        };
    }

    pub fn toggle_selected(&mut self) {
        let Some(pid) = self.selected_pid() else {
            return;
        };

        if !self.selected_pids.insert(pid) {
            self.selected_pids.remove(&pid);
        }
    }

    pub fn toggle_all(&mut self) {
        let all_pids = self
            .processes
            .iter()
            .map(|process| process.pid)
            .collect::<BTreeSet<u32>>();

        if self.selected_pids.len() == all_pids.len() {
            self.selected_pids.clear();
        } else {
            self.selected_pids = all_pids;
        }
    }

    pub fn request_confirmation(&mut self) {
        if self.selected_pids().is_empty() {
            return;
        }

        self.mode = AppMode::ConfirmKill;
        self.status = format!(
            "Kill {} selected process(es)? y=graceful+fallback, f=force, n=cancel",
            self.selected_pids().len()
        );
    }

    pub fn cancel_confirmation(&mut self) {
        self.mode = if self.processes.is_empty() {
            AppMode::Done
        } else {
            AppMode::Browsing
        };
        self.status = "Kill cancelled".to_string();
    }

    pub fn start_killing(&mut self) {
        self.mode = AppMode::Killing;
        self.status = "Terminating selected process(es)...".to_string();
    }

    pub fn set_kill_results(&mut self, results: Vec<KillResult>) {
        let failures = results.iter().filter(|result| result.is_failed()).count();
        self.last_results = results;
        self.selected_pids.clear();
        self.mode = if failures == 0 {
            AppMode::Done
        } else {
            AppMode::Error
        };
        self.status = if failures == 0 {
            "Termination complete".to_string()
        } else {
            format!("{failures} termination(s) failed")
        };
    }

    pub fn tick(&mut self) {
        self.tick = self.tick.wrapping_add(1);
    }

    pub fn quit(&mut self) {
        self.should_quit = true;
    }

    pub fn should_quit(&self) -> bool {
        self.should_quit
    }
}

fn join_ports(ports: &[u16]) -> String {
    ports
        .iter()
        .map(u16::to_string)
        .collect::<Vec<String>>()
        .join(", ")
}
