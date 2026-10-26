$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$toolsDir = Join-Path $projectRoot '.runtime\tools'
$architecture = switch ([System.Runtime.InteropServices.RuntimeInformation]::OSArchitecture) {
    'X64' { 'amd64' }
    # Windows on ARM runs x64 binaries through the built-in emulation layer.
    # DNSx and GAU do not currently publish Windows ARM64 archives.
    'Arm64' { 'amd64' }
    default { throw "Arquitetura não suportada: $_" }
}

$tools = @(
    @{ Name = 'subfinder'; Version = '2.14.0'; Repository = 'projectdiscovery/subfinder' },
    @{ Name = 'dnsx'; Version = '1.3.1'; Repository = 'projectdiscovery/dnsx' },
    @{ Name = 'httpx'; Version = '1.12.0'; Repository = 'projectdiscovery/httpx' },
    @{ Name = 'katana'; Version = '1.7.0'; Repository = 'projectdiscovery/katana'; ChecksumName = 'katana-1.7.0-checksums.txt' },
    @{ Name = 'gau'; Version = '2.2.4'; Repository = 'lc/gau' }
)

New-Item -ItemType Directory -Path $toolsDir -Force | Out-Null

foreach ($tool in $tools) {
    $executable = Join-Path $toolsDir "$($tool.Name).exe"
    if (Test-Path -LiteralPath $executable) {
        Write-Output "$($tool.Name) já está instalado."
        continue
    }

    $archiveName = "$($tool.Name)_$($tool.Version)_windows_${architecture}.zip"
    $checksumsName = if ($tool.ChecksumName) {
        $tool.ChecksumName
    } else {
        "$($tool.Name)_$($tool.Version)_checksums.txt"
    }
    $releaseBase = "https://github.com/$($tool.Repository)/releases/download/v$($tool.Version)"
    $archivePath = Join-Path $toolsDir $archiveName
    $checksumsPath = Join-Path $toolsDir $checksumsName

    try {
        Write-Output "Baixando $releaseBase/$archiveName"
        Invoke-WebRequest -Uri "$releaseBase/$archiveName" -OutFile $archivePath
        Invoke-WebRequest -Uri "$releaseBase/$checksumsName" -OutFile $checksumsPath
        $expectedLine = Get-Content -LiteralPath $checksumsPath |
            Where-Object { $_ -match "\s$([regex]::Escape($archiveName))$" } |
            Select-Object -First 1
        if (-not $expectedLine) { throw "Checksum oficial de $archiveName não encontrado." }
        $expectedHash = ($expectedLine -split '\s+')[0].ToLowerInvariant()
        $actualHash = (Get-FileHash -LiteralPath $archivePath -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($actualHash -ne $expectedHash) { throw "SHA-256 inválido para $archiveName." }
        Expand-Archive -LiteralPath $archivePath -DestinationPath $toolsDir -Force
        if (-not (Test-Path -LiteralPath $executable)) {
            throw "$($tool.Name).exe não foi encontrado após a extração."
        }
        Write-Output "$($tool.Name) $($tool.Version) instalado e verificado."
    } finally {
        Remove-Item -LiteralPath $archivePath -Force -ErrorAction SilentlyContinue
        Remove-Item -LiteralPath $checksumsPath -Force -ErrorAction SilentlyContinue
    }
}
