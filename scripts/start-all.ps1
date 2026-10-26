# MingHat: sobe TODOS os serviços (Ollama, backend, frontend, landing, tunnel).
# Idempotente: só inicia o que estiver parado. Usado pela Tarefa Agendada no logon
# e como watchdog (a cada poucos minutos) para reerguer o que cair.

$ErrorActionPreference = 'SilentlyContinue'
$scriptDir = $PSScriptRoot
$root = Split-Path -Parent $scriptDir

function Test-Port([int]$Port) {
    try {
        $c = New-Object System.Net.Sockets.TcpClient
        $c.Connect('127.0.0.1', $Port)
        $c.Close()
        return $true
    } catch {
        return $false
    }
}

# 1) Ollama (normalmente já sobe sozinho no login; garante mesmo assim)
if (-not (Test-Port 11434)) {
    $ollama = Join-Path $env:LOCALAPPDATA 'Programs\Ollama\ollama.exe'
    if (Test-Path -LiteralPath $ollama) {
        Start-Process -FilePath $ollama -ArgumentList 'serve' -WindowStyle Hidden
    }
    for ($i = 0; $i -lt 20 -and -not (Test-Port 11434); $i++) { Start-Sleep -Seconds 1 }
}

# 2) Backend (8080) + Frontend (8811) — start-local é idempotente por porta
if (-not (Test-Port 8080) -or -not (Test-Port 8811)) {
    try { & (Join-Path $scriptDir 'start-local.ps1') } catch {}
}

# 3) Landing (8815) — checa por processo E porta para nunca duplicar
$landingRunning = [bool](Get-CimInstance Win32_Process -Filter "Name='python.exe'" -ErrorAction SilentlyContinue |
    Where-Object { $_.CommandLine -like '*serve-landing*' })
if (-not $landingRunning -and -not (Test-Port 8815)) {
    $py = Join-Path $env:TEMP 'ia-8811-backend\Scripts\python.exe'
    if (-not (Test-Path -LiteralPath $py)) { $py = Join-Path $root '.venv\Scripts\python.exe' }
    if (Test-Path -LiteralPath $py) {
        Start-Process -FilePath $py -ArgumentList (Join-Path $scriptDir 'serve-landing.py') -WorkingDirectory $root -WindowStyle Hidden
    }
}

# 4) Cloudflare Tunnel
if (-not (Get-Process cloudflared -ErrorAction SilentlyContinue)) {
    $cf = 'C:\Program Files (x86)\cloudflared\cloudflared.exe'
    $cfg = Join-Path $root '.runtime\cloudflared-minghat.yml'
    if ((Test-Path -LiteralPath $cf) -and (Test-Path -LiteralPath $cfg)) {
        Start-Process -FilePath $cf -ArgumentList 'tunnel', '--config', $cfg, 'run' -WindowStyle Hidden
    }
}
