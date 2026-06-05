use std::collections::BTreeMap;
use std::env;
use std::fs;
use std::path::{Path, PathBuf};

use serde::{Deserialize, Serialize};

// Curated common local web/app dev, preview, inspector, and live-reload ports.
// Custom CLI ports still support any valid port from 1 to 65535.
pub const DEFAULT_PORTS: &[u16] = &[
    1234, 1313, 1420, 2368, 3000, 3001, 3002, 3003, 3333, 4000, 4173, 4200, 4321, 4567, 5000, 5001,
    5050, 5173, 5174, 5500, 5601, 5800, 5858, 6006, 6007, 7000, 7001, 7007, 7071, 8000, 8001, 8008,
    8080, 8081, 8082, 8088, 8787, 8800, 8888, 8889, 9000, 9001, 9090, 9229, 9292, 9293, 9443,
    10000, 19000, 19001, 19002, 19006, 24678, 35729,
];

pub const MAGIC_PORTS_ENV: &str = "MAGIC_PORTS";
pub const MAGIC_CONFIG_DIR_ENV: &str = "MAGIC_CONFIG_DIR";
pub const MAGIC_CONFIG_PATH_ENV: &str = "MAGIC_CONFIG_PATH";

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct ConfigContext {
    pub magic_ports: Option<String>,
    pub config_path: Option<PathBuf>,
}

impl ConfigContext {
    pub fn from_env() -> Self {
        Self {
            magic_ports: env::var(MAGIC_PORTS_ENV).ok(),
            config_path: default_config_path(),
        }
    }
}

#[derive(Clone, Debug, Default, Deserialize, Eq, PartialEq, Serialize)]
pub struct MagicConfig {
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub default_ports: Option<Vec<u16>>,
    #[serde(default)]
    pub profiles: BTreeMap<String, Vec<u16>>,
}

pub fn resolve_ports_with_context(
    cli_ports: &[u16],
    profile: Option<&str>,
    context: &ConfigContext,
) -> Result<Vec<u16>, String> {
    if !cli_ports.is_empty() {
        return normalize_ports(cli_ports.to_vec());
    }

    if let Some(env_ports) = context.magic_ports.as_deref() {
        return parse_ports(env_ports).map_err(|error| format!("{MAGIC_PORTS_ENV}: {error}"));
    }

    let config = load_config(context)?;
    if let Some(profile_name) = profile {
        let Some(ports) = config.profiles.get(profile_name) else {
            return Err(format!(
                "profile '{profile_name}' was not found in Magic config"
            ));
        };
        return normalize_ports(ports.clone());
    }

    if let Some(ports) = config.default_ports
        && !ports.is_empty()
    {
        return normalize_ports(ports);
    }

    Ok(DEFAULT_PORTS.to_vec())
}

pub fn parse_ports(value: &str) -> Result<Vec<u16>, String> {
    let ports = value
        .split(',')
        .map(str::trim)
        .filter(|part| !part.is_empty())
        .map(|part| {
            part.parse::<u16>()
                .map_err(|_| format!("'{part}' is not a valid port"))
        })
        .collect::<Result<Vec<_>, _>>()?;

    normalize_ports(ports)
}

pub fn load_config(context: &ConfigContext) -> Result<MagicConfig, String> {
    let Some(path) = &context.config_path else {
        return Ok(MagicConfig::default());
    };

    if !path.exists() {
        return Ok(MagicConfig::default());
    }

    let content = fs::read_to_string(path)
        .map_err(|error| format!("failed to read {}: {error}", path.display()))?;
    serde_json::from_str(&content)
        .map_err(|error| format!("failed to parse {}: {error}", path.display()))
}

pub fn save_config(context: &ConfigContext, config: &MagicConfig) -> Result<PathBuf, String> {
    let path = context
        .config_path
        .clone()
        .ok_or_else(|| "Magic config path could not be resolved".to_string())?;
    write_config(&path, config)?;
    Ok(path)
}

pub fn set_default_ports(
    context: &ConfigContext,
    ports: Vec<u16>,
) -> Result<(PathBuf, MagicConfig), String> {
    let mut config = load_config(context)?;
    config.default_ports = Some(normalize_ports(ports)?);
    let path = save_config(context, &config)?;
    Ok((path, config))
}

pub fn set_profile_ports(
    context: &ConfigContext,
    name: &str,
    ports: Vec<u16>,
) -> Result<(PathBuf, MagicConfig), String> {
    if name.trim().is_empty() {
        return Err("profile name must not be empty".to_string());
    }

    let mut config = load_config(context)?;
    config
        .profiles
        .insert(name.to_string(), normalize_ports(ports)?);
    let path = save_config(context, &config)?;
    Ok((path, config))
}

pub fn config_path(context: &ConfigContext) -> Result<PathBuf, String> {
    context
        .config_path
        .clone()
        .ok_or_else(|| "Magic config path could not be resolved".to_string())
}

pub fn normalize_ports(ports: Vec<u16>) -> Result<Vec<u16>, String> {
    if ports.is_empty() {
        return Err("at least one port is required".to_string());
    }

    if ports.contains(&0) {
        return Err("ports must be between 1 and 65535".to_string());
    }

    let mut deduped = Vec::new();
    for port in ports {
        if !deduped.contains(&port) {
            deduped.push(port);
        }
    }

    Ok(deduped)
}

fn write_config(path: &Path, config: &MagicConfig) -> Result<(), String> {
    if let Some(parent) = path.parent() {
        fs::create_dir_all(parent)
            .map_err(|error| format!("failed to create {}: {error}", parent.display()))?;
    }

    let content = serde_json::to_string_pretty(config)
        .map_err(|error| format!("failed to serialize config: {error}"))?;
    fs::write(path, format!("{content}\n"))
        .map_err(|error| format!("failed to write {}: {error}", path.display()))
}

fn default_config_path() -> Option<PathBuf> {
    if let Ok(path) = env::var(MAGIC_CONFIG_PATH_ENV) {
        return Some(PathBuf::from(path));
    }

    if let Ok(dir) = env::var(MAGIC_CONFIG_DIR_ENV) {
        return Some(PathBuf::from(dir).join("config.json"));
    }

    #[cfg(windows)]
    {
        if let Ok(dir) = env::var("LOCALAPPDATA") {
            return Some(PathBuf::from(dir).join("magic").join("config.json"));
        }
        if let Ok(dir) = env::var("APPDATA") {
            return Some(PathBuf::from(dir).join("magic").join("config.json"));
        }
    }

    #[cfg(not(windows))]
    {
        if let Ok(dir) = env::var("XDG_CONFIG_HOME") {
            return Some(PathBuf::from(dir).join("magic").join("config.json"));
        }
    }

    env::var("HOME").ok().map(|home| {
        PathBuf::from(home)
            .join(".config")
            .join("magic")
            .join("config.json")
    })
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub struct ProtocolFilter {
    pub tcp: bool,
    pub udp: bool,
}

impl ProtocolFilter {
    pub fn from_flags(tcp: bool, udp: bool) -> Self {
        if tcp || udp {
            Self { tcp, udp }
        } else {
            Self {
                tcp: true,
                udp: true,
            }
        }
    }
}
