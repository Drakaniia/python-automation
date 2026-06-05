use magic::scanner::{
    ProcessInfo, Protocol, ScanAttempt, ScanStatus, combine_scan_attempts, parse_lsof_output,
    parse_ss_output, parse_windows_netstat, sort_and_dedup_processes,
};

#[test]
fn parses_windows_netstat_tcp_listeners_for_requested_ports() {
    let output = r#"
  Proto  Local Address          Foreign Address        State           PID
  TCP    127.0.0.1:3000         0.0.0.0:0              LISTENING       1234
  TCP    127.0.0.1:13000        0.0.0.0:0              LISTENING       9999
  TCP    127.0.0.1:3000         127.0.0.1:50000        ESTABLISHED     5678
  UDP    0.0.0.0:5173           *:*                                    4321
"#;

    let processes = parse_windows_netstat(output, &[3000, 5173], true, true);

    assert_eq!(
        processes,
        vec![
            ProcessInfo::new(3000, 1234, Protocol::Tcp),
            ProcessInfo::new(5173, 4321, Protocol::Udp),
        ]
    );
}

#[test]
fn parses_ss_output_with_process_names() {
    let output = r#"
Netid State  Recv-Q Send-Q Local Address:Port Peer Address:Port Process
tcp   LISTEN 0      511    127.0.0.1:5173    0.0.0.0:*     users:(("vite",pid=3210,fd=23))
tcp   LISTEN 0      511    [::1]:8080        [::]:*        users:(("node",pid=6543,fd=20))
"#;

    let processes = parse_ss_output(output, &[5173, 8080], true, false);

    assert_eq!(
        processes,
        vec![
            ProcessInfo::new(5173, 3210, Protocol::Tcp).with_command("vite"),
            ProcessInfo::new(8080, 6543, Protocol::Tcp).with_command("node"),
        ]
    );
}

#[test]
fn parses_lsof_output_for_tcp_and_udp_listeners() {
    let output = r#"
COMMAND   PID USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
node     1111  dev   22u  IPv4  12345      0t0  TCP 127.0.0.1:3000 (LISTEN)
python   2222  dev   23u  IPv4  67890      0t0  UDP *:5173
"#;

    let processes = parse_lsof_output(output, &[3000, 5173], true, true);

    assert_eq!(
        processes,
        vec![
            ProcessInfo::new(3000, 1111, Protocol::Tcp).with_command("node"),
            ProcessInfo::new(5173, 2222, Protocol::Udp).with_command("python"),
        ]
    );
}

#[test]
fn deduplicates_processes_by_port_pid_and_protocol() {
    let processes = vec![
        ProcessInfo::new(3000, 10, Protocol::Tcp)
            .with_command("node")
            .with_command_line("npm run dev"),
        ProcessInfo::new(3000, 10, Protocol::Tcp).with_executable_path("/usr/bin/node"),
    ];

    let deduped = sort_and_dedup_processes(processes);

    assert_eq!(deduped.len(), 1);
    assert_eq!(deduped[0].command.as_deref(), Some("node"));
    assert_eq!(deduped[0].command_line.as_deref(), Some("npm run dev"));
    assert_eq!(deduped[0].executable_path.as_deref(), Some("/usr/bin/node"));
}

#[test]
fn reports_scanner_dependencies_as_unavailable_when_no_tool_can_run() {
    let report = combine_scan_attempts(vec![
        ScanAttempt::unavailable("lsof", "not found"),
        ScanAttempt::unavailable("ss", "not found"),
    ]);

    assert!(matches!(report.status, ScanStatus::Unavailable { .. }));
    assert!(report.processes.is_empty());
    assert!(report.guidance().contains("lsof"));
    assert!(report.guidance().contains("ss"));
}

#[test]
fn reports_permission_limited_scans_before_claiming_no_listeners() {
    let report = combine_scan_attempts(vec![
        ScanAttempt::permission_limited("lsof", "permission denied"),
        ScanAttempt::empty("ss"),
    ]);

    assert!(matches!(
        report.status,
        ScanStatus::PermissionLimited { .. }
    ));
    assert!(report.guidance().contains("permission"));
}
