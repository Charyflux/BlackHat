# Ambiente de DESENVOLVIMENTO da MingHat.
# Roda a partir do worktree D:\IA-dev (branch "dev"), portas proprias, sem
# tunel publico (so localhost). Aqui e onde mudanças sao testadas primeiro,
# antes de ir para staging.
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$runtimeDir = Join-Path $projectRoot '.runtime'
$mainRepoRoot = 'D:\IA'

$pythonPath = Join-Path $mainRepoRoot '.venv/Scripts/python.exe'
$temporaryPython = Join-Path $env:TEMP 'ia-8811-backend/Scripts/python.exe'
if (Test-Path -LiteralPath $temporaryPython) {
    $pythonPath = $temporaryPython
}
if (-not (Test-Path -LiteralPath $pythonPath)) {
    throw 'Ambiente Python ausente: instale as dependencias em .venv antes de iniciar.'
}
New-Item -ItemType Directory -Path $runtimeDir -Force | Out-Null

# Reaproveita as ferramentas de recon ja baixadas no repo principal (evita
# reinstalar em cada worktree).
$env:MINGHAT_RECON_TOOLS_DIR = Join-Path $mainRepoRoot '.runtime\tools'
$env:SUBFINDER_PATH = Join-Path $mainRepoRoot '.runtime\tools\subfinder.exe'

function Test-LocalPort([int]$Port) {
    $client = New-Object System.Net.Sockets.TcpClient
    try {
        $client.Connect('127.0.0.1', $Port)
        return $true
    } catch {
        return $false
    } finally {
        $client.Dispose()
    }
}

if (-not (Test-LocalPort 11434)) {
    throw 'Ollama indisponivel. Inicie o Ollama e execute novamente.'
}

$BackendPort = 8070
$FrontendPort = 8801

if (-not (Test-LocalPort $BackendPort)) {
    $secretPath = Join-Path $runtimeDir 'webui-secret.key'
    if (-not (Test-Path -LiteralPath $secretPath)) {
        $secretBytes = New-Object byte[] 48
        $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
        $rng.GetBytes($secretBytes)
        $rng.Dispose()
        [System.IO.File]::WriteAllText($secretPath, [Convert]::ToBase64String($secretBytes))
    }
    $env:WEBUI_SECRET_KEY = [System.IO.File]::ReadAllText($secretPath)
    $env:DATA_DIR = Join-Path $runtimeDir 'data'
    $env:STATIC_DIR = Join-Path $runtimeDir 'static'
    $env:FRONTEND_BUILD_DIR = Join-Path $projectRoot 'static'
    $env:OLLAMA_BASE_URL = 'http://127.0.0.1:11434'
    $env:DEFAULT_MODELS = 'llama32-abliterated:latest'
    $env:DEFAULT_LOCALE = 'pt-BR'
    $env:WEBUI_NAME = 'MingHat (dev)'
    $env:WEBUI_AUTH = 'True'
    $env:ENABLE_SIGNUP = 'True'
    $env:ENABLE_LOGIN_FORM = 'True'
    $env:DEFAULT_USER_ROLE = 'user'
    $env:USER_PERMISSIONS_CHAT_CONTROLS = 'False'
    $env:USER_PERMISSIONS_CHAT_SYSTEM_PROMPT = 'False'
    $env:USER_PERMISSIONS_CHAT_PARAMS = 'False'
    $env:USER_PERMISSIONS_CHAT_VALVES = 'False'
    $env:ENABLE_OPENAI_API = 'False'
    $env:ENABLE_EVALUATION_ARENA_MODELS = 'False'
    $env:ENABLE_VERSION_UPDATE_CHECK = 'False'
    $env:OFFLINE_MODE = 'False'
    $env:RAG_EMBEDDING_MODEL_AUTO_UPDATE = 'False'
    $env:RAG_RERANKING_MODEL_AUTO_UPDATE = 'False'
    $env:WHISPER_MODEL_AUTO_UPDATE = 'False'
    $env:ANONYMIZED_TELEMETRY = 'False'
    $env:CORS_ALLOW_ORIGIN = "http://127.0.0.1:$FrontendPort;http://localhost:$FrontendPort"
    $env:HF_HOME = Join-Path $mainRepoRoot '.runtime\huggingface'
    # MINGHAT_SMTP_* fica de fora de proposito: dev nunca deve mandar e-mail de
    # verdade para clientes. O webhook so grava a allowlist local.
    Start-Process -FilePath $pythonPath -ArgumentList '-m','uvicorn','open_webui.main:app','--host','127.0.0.1','--port',"$BackendPort" -WorkingDirectory (Join-Path $projectRoot 'backend') -WindowStyle Hidden -RedirectStandardOutput (Join-Path $runtimeDir 'backend.log') -RedirectStandardError (Join-Path $runtimeDir 'backend-error.log') | Out-Null
}

if (-not (Test-LocalPort $FrontendPort)) {
    Start-Process -FilePath (Get-Command node).Source -ArgumentList 'node_modules/vite/bin/vite.js','--host','127.0.0.1','--port',"$FrontendPort" -WorkingDirectory $projectRoot -WindowStyle Hidden -RedirectStandardOutput (Join-Path $runtimeDir 'frontend.log') -RedirectStandardError (Join-Path $runtimeDir 'frontend-error.log') | Out-Null
}
Write-Output "DEV iniciado. Interface: http://localhost:$FrontendPort (backend $BackendPort). Logs: $runtimeDir"
