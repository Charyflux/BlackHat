param(
    [string]$Version = '2.14.0'
)

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$toolsDir = Join-Path $projectRoot '.runtime\tools'
$subfinderPath = Join-Path $toolsDir 'subfinder.exe'

if (Test-Path -LiteralPath $subfinderPath) {
    Write-Output "Subfinder já instalado em $subfinderPath"
    exit 0
}

$architecture = switch ([System.Runtime.InteropServices.RuntimeInformation]::OSArchitecture) {
    'X64' { 'amd64' }
    'Arm64' { 'arm64' }
    default { throw "Arquitetura não suportada: $_" }
}

New-Item -ItemType Directory -Path $toolsDir -Force | Out-Null
$archiveName = "subfinder_${Version}_windows_${architecture}.zip"
$releaseBase = "https://github.com/projectdiscovery/subfinder/releases/download/v$Version"
$archivePath = Join-Path $toolsDir $archiveName
$checksumsPath = Join-Path $toolsDir "subfinder_${Version}_checksums.txt"

try {
    Invoke-WebRequest -Uri "$releaseBase/$archiveName" -OutFile $archivePath
    Invoke-WebRequest -Uri "$releaseBase/subfinder_${Version}_checksums.txt" -OutFile $checksumsPath

    $expectedLine = Get-Content -LiteralPath $checksumsPath |
        Where-Object { $_ -match "\s$([regex]::Escape($archiveName))$" } |
        Select-Object -First 1
    if (-not $expectedLine) {
        throw 'Checksum oficial do arquivo não encontrado.'
    }
    $expectedHash = ($expectedLine -split '\s+')[0].ToLowerInvariant()
    $actualHash = (Get-FileHash -LiteralPath $archivePath -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actualHash -ne $expectedHash) {
        throw 'A verificação SHA-256 do Subfinder falhou.'
    }

    Expand-Archive -LiteralPath $archivePath -DestinationPath $toolsDir -Force
    if (-not (Test-Path -LiteralPath $subfinderPath)) {
        throw 'O executável não foi encontrado após a extração.'
    }
    & $subfinderPath -version
    Write-Output "Subfinder $Version instalado em $subfinderPath"
} finally {
    Remove-Item -LiteralPath $archivePath -Force -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath $checksumsPath -Force -ErrorAction SilentlyContinue
}
