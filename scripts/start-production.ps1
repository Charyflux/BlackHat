param(
    [string]$PublicUrl = ''
)

$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $PSScriptRoot
$runtimeDir = Join-Path $projectRoot '.runtime'
$buildDir = Join-Path $projectRoot 'build'
$pythonPath = Join-Path $projectRoot '.venv\Scripts\python.exe'
$temporaryPython = Join-Path $env:TEMP 'ia-8811-backend\Scripts\python.exe'

if (Test-Path -LiteralPath $temporaryPython) {
    $pythonPath = $temporaryPython
}
if (-not (Test-Path -LiteralPath $pythonPath)) {
    throw 'Ambiente Python ausente. Instale as dependencias antes de iniciar.'
}
if (-not (Test-Path -LiteralPath (Join-Path $buildDir 'index.html'))) {
    throw 'Build de producao ausente. Execute: $env:NODE_OPTIONS="--max-old-space-size=8192"; npm.cmd run build'
}

New-Item -ItemType Directory -Path $runtimeDir -Force | Out-Null

$reconTools = @('subfinder.exe', 'dnsx.exe', 'httpx.exe', 'katana.exe', 'gau.exe')
$missingReconTool = $reconTools | Where-Object {
    -not (Test-Path -LiteralPath (Join-Path $runtimeDir "tools\$_"))
} | Select-Object -First 1
if ($missingReconTool) {
    & (Join-Path $PSScriptRoot 'install-recon-tools.ps1')
}

$ollamaAvailable = Test-NetConnection -ComputerName '127.0.0.1' -Port 11434 -InformationLevel Quiet -WarningAction SilentlyContinue
if (-not $ollamaAvailable) {
    throw 'Ollama indisponivel em 127.0.0.1:11434.'
}

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
$env:FRONTEND_BUILD_DIR = $buildDir
$env:MINGHAT_RECON_TOOLS_DIR = Join-Path $runtimeDir 'tools'
$env:SUBFINDER_PATH = Join-Path $runtimeDir 'tools\subfinder.exe'
$env:OLLAMA_BASE_URL = 'http://127.0.0.1:11434'
$env:DEFAULT_MODELS = 'uncensored-br:latest'
$env:DEFAULT_LOCALE = 'pt-BR'
$env:WEBUI_NAME = 'MingHat'
$env:WEBUI_AUTH = 'True'
$env:ENABLE_SIGNUP = 'False'
$env:ENABLE_OPENAI_API = 'False'
$env:ENABLE_EVALUATION_ARENA_MODELS = 'False'
$env:ENABLE_VERSION_UPDATE_CHECK = 'False'
$env:OFFLINE_MODE = 'False'
    $env:RAG_EMBEDDING_MODEL_AUTO_UPDATE = 'False'
    $env:RAG_RERANKING_MODEL_AUTO_UPDATE = 'False'
    $env:WHISPER_MODEL_AUTO_UPDATE = 'False'
$env:ANONYMIZED_TELEMETRY = 'False'
$env:XCONTENT_TYPE = 'nosniff'
$env:XFRAME_OPTIONS = 'DENY'
$env:XDOWNLOAD_OPTIONS = 'noopen'
$env:XPERMITTED_CROSS_DOMAIN_POLICIES = 'none'
$env:REFERRER_POLICY = 'strict-origin-when-cross-origin'
$env:PERMISSIONS_POLICY = 'accelerometer=(),autoplay=(),camera=(),clipboard-read=(),clipboard-write=(self),fullscreen=(self),geolocation=(),gyroscope=(),magnetometer=(),microphone=(),midi=(),payment=(),picture-in-picture=(),sync-xhr=(),usb=(),xr-spatial-tracking=()'
$env:CROSS_ORIGIN_OPENER_POLICY = 'same-origin'
$env:HSTS = 'max-age=31536000;includeSubDomains;preload'
$localOrigins = 'http://127.0.0.1:8080;http://localhost:8080;http://127.0.0.1:8811;http://localhost:8811'
$env:CORS_ALLOW_ORIGIN = if ($PublicUrl) { "$($PublicUrl.TrimEnd('/'));$localOrigins" } else { $localOrigins }
if ($PublicUrl) {
    $env:WEBUI_URL = $PublicUrl.TrimEnd('/')
}

Push-Location (Join-Path $projectRoot 'backend')
try {
    & $pythonPath -m uvicorn open_webui.main:app --host 127.0.0.1 --port 8080 --proxy-headers --forwarded-allow-ips '127.0.0.1'
} finally {
    Pop-Location
}

