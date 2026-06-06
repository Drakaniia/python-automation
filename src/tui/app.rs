use std::collections::{BTreeMap, BTreeSet};
use std::ops::Range;

use crate::process::KillResult;
use crate::scanner::{ProcessInfo, Protocol, ScanReport, ScanStatus};

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum AppMode {
    Scanning,
    Browsing,
    ConfirmKill,
    Killing,
    Done,
    Error,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct ConfirmationTarget {
    pub pid: u32,
    pub ports: Vec<u16>,
    pub protocols: Vec<Protocol>,
    pub command: Option<String>,
    pub command_line: Option<String>,
    pub executable_path: Option<String>,
    pub cwd: Option<String>,
    pub parent_pid: Option<u32>,
}

#[derive(Clone, Debug)]
pub struct App {
    ports: Vec<u16>,
    tcp: bool,
    udp: bool,
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
            tcp: true,
            udp: true,
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

    pub fn with_filter(ports: Vec<u16>, tcp: bool, udp: bool) -> Self {
        let mut app = Self::new(ports);
        app.tcp = tcp;
        app.udp = udp;
        app
    }

    pub fn with_processes(ports: Vec<u16>, processes: Vec<ProcessInfo>) -> Self {
        let mut app = Self::new(ports);
        app.set_processes(processes);
        app
    }

    pub fn ports(&self) -> &[u16] {
        &self.ports
    }

    pub fn protocol_filter_label(&self) -> &'static str {
        match (self.tcp, self.udp) {
            (true, true) => "TCP+UDP",
            (true, false) => "TCP only",
            (false, true) => "UDP only",
            (false, false) => "no protocols",
        }
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
        self.last_results.clear();
    }

    pub fn set_processes(&mut self, processes: Vec<ProcessInfo>) {
        self.replace_processes(processes);
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

    pub fn set_scan_report(&mut self, report: ScanReport) {
        let guidance = report.guidance();
        match report.status {
            ScanStatus::Found | ScanStatus::NoListeners => self.set_processes(report.processes),
            ScanStatus::Unavailable { .. } | ScanStatus::PermissionLimited { .. } => {
                self.replace_processes(report.processes);
                self.mode = AppMode::Error;
                self.status = guidance;
            }
        }
    }

    pub fn refresh_processes_after_kill(&mut self, processes: Vec<ProcessInfo>) {
        self.replace_processes(processes);
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

    pub fn move_first(&mut self) {
        if self.processes.is_empty() {
            return;
        }

        self.selected_index = 0;
    }

    pub fn move_last(&mut self) {
        if self.processes.is_empty() {
            return;
        }

        self.selected_index = self.processes.len() - 1;
    }

    pub fn toggle_selected(&mut self) {
        let Some(pid) = self.selected_pid() else {
            return;
        };

        let marked = self.selected_pids.insert(pid);
        if !marked {
            self.selected_pids.remove(&pid);
        }
        let action = if marked { "Marked" } else { "Unmarked" };
        self.status = format!("{action} PID {pid} ({} selected)", self.selected_pids.len());
    }

    pub fn toggle_all(&mut self) {
        let all_pids = self
            .processes
            .iter()
            .map(|process| process.pid)
            .collect::<BTreeSet<u32>>();

        if all_pids.is_empty() {
            self.status = "No processes to mark".to_string();
        } else if self.selected_pids.len() == all_pids.len() {
            self.selected_pids.clear();
            self.status = "Cleared all selections".to_string();
        } else {
            let count = all_pids.len();
            self.selected_pids = all_pids;
            self.status = format!("Marked all {count} process(es)");
        }
    }

    pub fn request_confirmation(&mut self) {
        if self.selected_pids().is_empty() {
            return;
        }

        self.mode = AppMode::ConfirmKill;
        self.status = format!(
            "Review {} selected process(es), then choose y=graceful+fallback, f=force, n=cancel",
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

    pub fn confirmation_targets(&self) -> Vec<ConfirmationTarget> {
        let selected_pids = self.selected_pids().into_iter().collect::<BTreeSet<_>>();
        let mut targets = BTreeMap::<u32, ConfirmationTarget>::new();

        for process in self
            .processes
            .iter()
            .filter(|process| selected_pids.contains(&process.pid))
        {
            let target = targets
                .entry(process.pid)
                .or_insert_with(|| ConfirmationTarget {
                    pid: process.pid,
                    ports: Vec::new(),
                    protocols: Vec::new(),
                    command: None,
                    command_line: None,
                    executable_path: None,
                    cwd: None,
                    parent_pid: None,
                });

            if !target.ports.contains(&process.port) {
                target.ports.push(process.port);
                target.ports.sort_unstable();
            }
            if !target.protocols.contains(&process.protocol) {
                target.protocols.push(process.protocol);
                target.protocols.sort_unstable();
            }
            if target.command.is_none() {
                target.command = process.command.clone();
            }
            if target.command_line.is_none() {
                target.command_line = process.command_line.clone();
            }
            if target.executable_path.is_none() {
                target.executable_path = process.executable_path.clone();
            }
            if target.cwd.is_none() {
                target.cwd = process.cwd.clone();
            }
            if target.parent_pid.is_none() {
                target.parent_pid = process.parent_pid;
            }
        }

        targets.into_values().collect()
    }

    pub fn visible_process_range(&self, capacity: usize) -> Range<usize> {
        if self.processes.is_empty() || capacity == 0 {
            return 0..0;
        }

        let capacity = capacity.min(self.processes.len());
        let end = (self.selected_index + 1)
            .max(capacity)
            .min(self.processes.len());
        end - capacity..end
    }

    pub fn quit(&mut self) {
        self.should_quit = true;
    }

    pub fn should_quit(&self) -> bool {
        self.should_quit
    }

    fn replace_processes(&mut self, processes: Vec<ProcessInfo>) {
        self.processes = processes;
        self.selected_pids
            .retain(|pid| self.processes.iter().any(|process| process.pid == *pid));
        if self.processes.is_empty() {
            self.selected_index = 0;
        } else {
            self.selected_index = self.selected_index.min(self.processes.len() - 1);
        }
    }
}

fn join_ports(ports: &[u16]) -> String {
    ports
        .iter()
        .map(u16::to_string)
        .collect::<Vec<String>>()
        .join(", ")
}
