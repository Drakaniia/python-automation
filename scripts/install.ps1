param(
    [string]$Repository = "Drakaniia/magic",
    [string]$InstallDir = "$env:LOCALAPPDATA\Programs\magic\bin",
    [string]$BaseUrl,
    [switch]$SkipChecksum
)

$ErrorActionPreference = "Stop"

if (-not [Environment]::Is64BitOperatingSystem) {
    throw "Magic currently publishes a Windows x64 binary. This system is not x64."
}

$assetName = "magic-windows-x64.zip"
if (-not $BaseUrl) {
    $BaseUrl = "https://github.com/$Repository/releases/latest/download"
}
$archivePath = Join-Path ([System.IO.Path]::GetTempPath()) $assetName
$checksumPath = Join-Path ([System.IO.Path]::GetTempPath()) "magic-SHA256SUMS.txt"
$extractRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("magic-install-" + [System.Guid]::NewGuid().ToString("N"))

function Join-AssetSource {
    param(
        [string]$Base,
        [string]$Name
    )

    if ($Base -match "^[a-zA-Z][a-zA-Z0-9+.-]*://") {
        return "$($Base.TrimEnd("/"))/$Name"
    }

    return Join-Path $Base $Name
}

function Receive-Asset {
    param(
        [string]$Source,
        [string]$Destination
    )

    if ($Source -match "^(https?|file)://") {
        Invoke-WebRequest -Uri $Source -OutFile $Destination
        return
    }

    Copy-Item -LiteralPath $Source -Destination $Destination -Force
}

Write-Host "Downloading Magic from $Repository..."
Receive-Asset -Source (Join-AssetSource -Base $BaseUrl -Name $assetName) -Destination $archivePath

if (-not $SkipChecksum) {
    Receive-Asset -Source (Join-AssetSource -Base $BaseUrl -Name "SHA256SUMS.txt") -Destination $checksumPath
    $checksumLine = Get-Content $checksumPath | Where-Object { $_ -match "\s+$([regex]::Escape($assetName))$" } | Select-Object -First 1

    if (-not $checksumLine) {
        throw "Could not find $assetName in SHA256SUMS.txt."
    }

    $expectedHash = ($checksumLine -split "\s+")[0].ToLowerInvariant()
    $actualHash = (Get-FileHash -Path $archivePath -Algorithm SHA256).Hash.ToLowerInvariant()

    if ($actualHash -ne $expectedHash) {
        throw "Checksum mismatch for $assetName. Expected $expectedHash, got $actualHash."
    }
}

if (Test-Path $extractRoot) {
    Remove-Item -LiteralPath $extractRoot -Recurse -Force
}

New-Item -ItemType Directory -Path $extractRoot -Force | Out-Null
Expand-Archive -Path $archivePath -DestinationPath $extractRoot -Force

$magicExe = Get-ChildItem -Path $extractRoot -Recurse -Filter "magic.exe" | Select-Object -First 1
$portkillExe = Get-ChildItem -Path $extractRoot -Recurse -Filter "portkill.exe" | Select-Object -First 1

if (-not $magicExe -or -not $portkillExe) {
    throw "The release archive did not contain magic.exe and portkill.exe."
}

New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
Copy-Item -Path $magicExe.FullName -Destination (Join-Path $InstallDir "magic.exe") -Force
Copy-Item -Path $portkillExe.FullName -Destination (Join-Path $InstallDir "portkill.exe") -Force

$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
$pathParts = @()
if ($userPath) {
    $pathParts = $userPath -split ";" | Where-Object { $_ }
}

$normalizedInstallDir = $InstallDir.TrimEnd("\")
$alreadyOnPath = $false
foreach ($pathPart in $pathParts) {
    if ($pathPart.TrimEnd("\") -ieq $normalizedInstallDir) {
        $alreadyOnPath = $true
        break
    }
}

if (-not $alreadyOnPath) {
    $newPath = if ($userPath) { "$userPath;$InstallDir" } else { $InstallDir }
    [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
    $env:Path = "$env:Path;$InstallDir"
    Write-Host "Added $InstallDir to your user PATH."
}

Remove-Item -LiteralPath $extractRoot -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -LiteralPath $archivePath -Force -ErrorAction SilentlyContinue
Remove-Item -LiteralPath $checksumPath -Force -ErrorAction SilentlyContinue

Write-Host "Magic installed to $InstallDir"
Write-Host "Open a new terminal, then run: magic"
