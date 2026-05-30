# GitHub Release Setup

Magic publishes installable binaries from GitHub Actions in
`Drakaniia/magic`.

## Workflows

```text
.github/workflows/ci.yml
.github/workflows/release.yml
```

`ci.yml` runs formatting and tests on pushes and pull requests.

`release.yml` runs when a tag matching `v*.*.*` is pushed. It verifies the repo,
builds release binaries on Windows, Linux, and macOS, creates checksums, and
publishes a GitHub Release.

## Release Assets

```text
magic-windows-x64.zip
magic-linux-x64.tar.gz
magic-macos-x64.tar.gz
magic-macos-arm64.tar.gz
SHA256SUMS.txt
```

The asset names stay stable so the install scripts can always download from the
latest release.

## Publish A Release

Update `Cargo.toml` if the version is changing, then tag and push:

```sh
git checkout main
git pull
git tag -a v0.1.0 -m "Release v0.1.0"
git push origin v0.1.0
```

GitHub Actions will build and publish the release.

You can also run the `Release` workflow manually from GitHub Actions and provide
a tag such as `v0.1.0`.

## Repository Settings

The release workflow needs permission to create releases and upload assets.
Enable:

```text
Repository Settings -> Actions -> General -> Workflow permissions -> Read and write permissions
```

## Local Verification

Before tagging:

```sh
cargo fmt -- --check
cargo test --locked
cargo build --release --locked
```

On Windows, the release executable is:

```text
target/release/magic.exe
```
