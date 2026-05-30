param(
    [string]$InstallDir = "$env:LOCALAPPDATA\Programs\magic\bin"
)

$ErrorActionPreference = "Stop"

if (Test-Path $InstallDir) {
    Remove-Item -LiteralPath $InstallDir -Recurse -Force
    Write-Host "Removed $InstallDir"
}

$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($userPath) {
    $normalizedInstallDir = $InstallDir.TrimEnd("\")
    $remainingParts = $userPath -split ";" | Where-Object {
        $_ -and ($_.TrimEnd("\") -ine $normalizedInstallDir)
    }
    [Environment]::SetEnvironmentVariable("Path", ($remainingParts -join ";"), "User")
    Write-Host "Removed Magic from your user PATH."
}

Write-Host "Magic uninstalled."
