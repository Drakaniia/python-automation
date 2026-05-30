use std::process::Command;

use super::{ProcessInfo, parse_lsof_output, parse_ss_output, sort_and_dedup_processes};

pub fn scan_ports(
    ports: &[u16],
    include_tcp: bool,
    include_udp: bool,
) -> Result<Vec<ProcessInfo>, String> {
    let mut processes = scan_with_lsof(ports, include_tcp, include_udp)?;

    if processes.is_empty() {
        processes.extend(scan_with_ss(ports, include_tcp, include_udp)?);
    }

    Ok(sort_and_dedup_processes(processes))
}

fn scan_with_lsof(
    ports: &[u16],
    include_tcp: bool,
    include_udp: bool,
) -> Result<Vec<ProcessInfo>, String> {
    let mut args = vec!["-nP".to_string()];

    for port in ports {
        if include_tcp {
            args.push(format!("-iTCP:{port}"));
            args.push("-sTCP:LISTEN".to_string());
        }
        if include_udp {
            args.push(format!("-iUDP:{port}"));
        }
    }

    let output = match Command::new("lsof").args(args).output() {
        Ok(output) => output,
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => return Ok(Vec::new()),
        Err(error) => return Err(format!("failed to run lsof: {error}")),
    };

    if !output.status.success() {
        return Ok(Vec::new());
    }

    Ok(parse_lsof_output(
        &String::from_utf8_lossy(&output.stdout),
        ports,
        include_tcp,
        include_udp,
    ))
}

fn scan_with_ss(
    ports: &[u16],
    include_tcp: bool,
    include_udp: bool,
) -> Result<Vec<ProcessInfo>, String> {
    let mut args = vec!["-l", "-n", "-p"];
    if include_tcp {
        args.push("-t");
    }
    if include_udp {
        args.push("-u");
    }

    let output = match Command::new("ss").args(args).output() {
        Ok(output) => output,
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => return Ok(Vec::new()),
        Err(error) => return Err(format!("failed to run ss: {error}")),
    };

    if !output.status.success() {
        return Ok(Vec::new());
    }

    Ok(parse_ss_output(
        &String::from_utf8_lossy(&output.stdout),
        ports,
        include_tcp,
        include_udp,
    ))
}
