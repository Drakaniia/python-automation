use std::process::ExitCode;

fn main() -> ExitCode {
    magic::cli::run_from_env()
}
