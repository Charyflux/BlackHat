# Ambiente de STAGING (teste) da MingHat.
# Roda a partir do worktree D:\IA-staging (branch "staging"), portas proprias,
# exposto publicamente em teste.minghat.com.br atras de um proxy com Basic
# Auth (scripts/staging-basic-auth-proxy.cjs), banco de dados isolado do de
# producao. So promove para "main"/producao depois de aprovado aqui.
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

$BackendPort = 8090
$FrontendPort = 8821
$ProxyPort = 8822

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
    $env:WEBUI_NAME = 'MingHat (staging)'
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
    $env:CORS_ALLOW_ORIGIN = "http://127.0.0.1:$FrontendPort;http://localhost:$FrontendPort;https://teste.minghat.com.br"
    $env:HF_HOME = Join-Path $mainRepoRoot '.runtime\huggingface'
    # MINGHAT_SMTP_* fica de fora de proposito: staging nunca deve mandar
    # e-mail de verdade. Testa o webhook so pela allowlist local isolada
    # (DATA_DIR proprio, nao encosta na lista de assinantes de producao).
    Start-Process -FilePath $pythonPath -ArgumentList '-m','uvicorn','open_webui.main:app','--host','127.0.0.1','--port',"$BackendPort" -WorkingDirectory (Join-Path $projectRoot 'backend') -WindowStyle Hidden -RedirectStandardOutput (Join-Path $runtimeDir 'backend.log') -RedirectStandardError (Join-Path $runtimeDir 'backend-error.log') | Out-Null
}

if (-not (Test-LocalPort $FrontendPort)) {
    Start-Process -FilePath (Get-Command node).Source -ArgumentList 'node_modules/vite/bin/vite.js','--host','127.0.0.1','--port',"$FrontendPort" -WorkingDirectory $projectRoot -WindowStyle Hidden -RedirectStandardOutput (Join-Path $runtimeDir 'frontend.log') -RedirectStandardError (Join-Path $runtimeDir 'frontend-error.log') | Out-Null
}

# Proxy com Basic Auth na frente do vite de staging (e o que o Cloudflare
# Tunnel de teste.minghat.com.br deve apontar, nao direto pro vite).
if (-not (Test-LocalPort $ProxyPort)) {
    $authPasswordPath = Join-Path $runtimeDir 'staging-auth-password.txt'
    if (-not (Test-Path -LiteralPath $authPasswordPath)) {
        $passwordBytes = New-Object byte[] 18
        $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
        $rng.GetBytes($passwordBytes)
        $rng.Dispose()
        $generatedPassword = [Convert]::ToBase64String($passwordBytes) -replace '[+/=]', ''
        [System.IO.File]::WriteAllText($authPasswordPath, $generatedPassword)
    }
    $env:STAGING_AUTH_USER = 'minghat'
    $env:STAGING_AUTH_PASS = [System.IO.File]::ReadAllText($authPasswordPath).Trim()
    $env:STAGING_PROXY_PORT = "$ProxyPort"
    $env:STAGING_TARGET_PORT = "$FrontendPort"
    Start-Process -FilePath (Get-Command node).Source -ArgumentList (Join-Path $projectRoot 'scripts\staging-basic-auth-proxy.cjs') -WorkingDirectory $projectRoot -WindowStyle Hidden -RedirectStandardOutput (Join-Path $runtimeDir 'staging-proxy.log') -RedirectStandardError (Join-Path $runtimeDir 'staging-proxy-error.log') | Out-Null
}

Write-Output "STAGING iniciado. Interface local: http://localhost:$FrontendPort (backend $BackendPort)."
Write-Output "Publico (via proxy com Basic Auth): https://teste.minghat.com.br"
Write-Output "Usuario: minghat | Senha: veja $runtimeDir\staging-auth-password.txt"
