use magic::scanner::{
    ProcessInfo, Protocol, parse_ss_output, parse_windows_netstat, sort_and_dedup_processes,
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
            ProcessInfo {
                port: 3000,
                pid: 1234,
                protocol: Protocol::Tcp,
                command: None,
            },
            ProcessInfo {
                port: 5173,
                pid: 4321,
                protocol: Protocol::Udp,
                command: None,
            },
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
            ProcessInfo {
                port: 5173,
                pid: 3210,
                protocol: Protocol::Tcp,
                command: Some("vite".to_string()),
            },
            ProcessInfo {
                port: 8080,
                pid: 6543,
                protocol: Protocol::Tcp,
                command: Some("node".to_string()),
            },
        ]
    );
}

#[test]
fn deduplicates_processes_by_port_pid_and_protocol() {
    let processes = vec![
        ProcessInfo {
            port: 3000,
            pid: 10,
            protocol: Protocol::Tcp,
            command: Some("node".to_string()),
        },
        ProcessInfo {
            port: 3000,
            pid: 10,
            protocol: Protocol::Tcp,
            command: None,
        },
    ];

    assert_eq!(sort_and_dedup_processes(processes).len(), 1);
}
