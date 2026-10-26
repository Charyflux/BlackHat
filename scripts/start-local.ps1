$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$runtimeDir = Join-Path $projectRoot '.runtime'
$pythonPath = Join-Path $projectRoot '.venv/Scripts/python.exe'
$temporaryPython = Join-Path $env:TEMP 'ia-8811-backend/Scripts/python.exe'
if (Test-Path -LiteralPath $temporaryPython) {
    $pythonPath = $temporaryPython
}
if (-not (Test-Path -LiteralPath $pythonPath)) {
    throw 'Ambiente Python ausente: instale as dependencias em .venv antes de iniciar.'
}
New-Item -ItemType Directory -Path $runtimeDir -Force | Out-Null

# Lock exclusivo: evita que este script rode em paralelo com outra instancia
# dele mesmo (ex.: o watchdog minghat-supervisor.ps1 disparando ao mesmo tempo
# que um restart manual). Sem isso, dois processos de backend podem tentar
# escrever no mesmo backend.log ao mesmo tempo e derrubar um ao outro.
$lockPath = Join-Path $runtimeDir 'start-local.lock'
# Lock "travado" (script anterior morreu sem liberar) com mais de 2 minutos
# e tratado como resto de uma execucao abortada, nao uma instancia ativa.
if (Test-Path -LiteralPath $lockPath) {
    $lockAge = (Get-Date) - (Get-Item -LiteralPath $lockPath).LastWriteTime
    if ($lockAge.TotalSeconds -gt 120) {
        Remove-Item -LiteralPath $lockPath -Force -ErrorAction SilentlyContinue
    }
}
try {
    $lockStream = [System.IO.File]::Open($lockPath, [System.IO.FileMode]::CreateNew, [System.IO.FileAccess]::Write, [System.IO.FileShare]::None)
} catch {
    Write-Output 'Outra instancia do start-local.ps1 ja esta rodando (lock ativo). Saindo.'
    exit 0
}
try {
$reconTools = @('subfinder.exe', 'dnsx.exe', 'httpx.exe', 'katana.exe', 'gau.exe')
$missingReconTool = $reconTools | Where-Object {
    -not (Test-Path -LiteralPath (Join-Path $runtimeDir "tools\$_"))
} | Select-Object -First 1
if ($missingReconTool) {
    & (Join-Path $PSScriptRoot 'install-recon-tools.ps1')
}
$env:MINGHAT_RECON_TOOLS_DIR = Join-Path $runtimeDir 'tools'
$env:SUBFINDER_PATH = Join-Path $runtimeDir 'tools\subfinder.exe'

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

if (-not (Test-LocalPort 8080)) {
    $secretPath = Join-Path $runtimeDir 'webui-secret.key'
    if (-not (Test-Path -LiteralPath $secretPath)) {
        $secretBytes = New-Object byte[] 48
        $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
        $rng.GetBytes($secretBytes)
        $rng.Dispose()
        [System.IO.File]::WriteAllText($secretPath, [Convert]::ToBase64String($secretBytes))
    }
    $env:WEBUI_SECRET_KEY = [System.IO.File]::ReadAllText($secretPath)
    $env:STATIC_DIR = Join-Path $runtimeDir 'static'
    $env:FRONTEND_BUILD_DIR = Join-Path $projectRoot 'static'
    $env:OLLAMA_BASE_URL = 'http://127.0.0.1:11434'
    $env:DEFAULT_MODELS = 'llama32-abliterated:latest'
    $env:DEFAULT_LOCALE = 'pt-BR'
    $env:WEBUI_NAME = 'MingHat'
    $env:WEBUI_AUTH = 'True'
    $env:ENABLE_SIGNUP = 'True'
    $env:ENABLE_LOGIN_FORM = 'True'
    $env:DEFAULT_USER_ROLE = 'user'
    # Esconde o painel "Controles" (prompt do sistema + parametros) para usuarios
    # comuns. O admin continua vendo. O bloqueio real e imposto no backend.
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
    $env:CORS_ALLOW_ORIGIN = 'http://127.0.0.1:8811;http://localhost:8811;https://minghat.com.br;https://www.minghat.com.br;https://chat.minghat.com.br'
    $env:HF_HOME = Join-Path $runtimeDir 'huggingface'
    Start-Process -FilePath $pythonPath -ArgumentList '-m','uvicorn','open_webui.main:app','--host','127.0.0.1','--port','8080' -WorkingDirectory (Join-Path $projectRoot 'backend') -WindowStyle Hidden -RedirectStandardOutput (Join-Path $runtimeDir 'backend.log') -RedirectStandardError (Join-Path $runtimeDir 'backend-error.log') | Out-Null
}

if (-not (Test-LocalPort 8811)) {
    Start-Process -FilePath (Get-Command node).Source -ArgumentList 'node_modules/vite/bin/vite.js','--host','127.0.0.1','--port','8811' -WorkingDirectory $projectRoot -WindowStyle Hidden -RedirectStandardOutput (Join-Path $runtimeDir 'frontend.log') -RedirectStandardError (Join-Path $runtimeDir 'frontend-error.log') | Out-Null
}
Write-Output 'Servicos iniciados. Interface: http://localhost:8811. Logs: .runtime'
} finally {
    $lockStream.Close()
    Remove-Item -LiteralPath $lockPath -Force -ErrorAction SilentlyContinue
}

