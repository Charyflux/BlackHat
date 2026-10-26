param(
    [string]$Email = 'admin@localhost'
)

# Define a senha do admin da MingHat. A senha e digitada por voce (oculta) e
# nunca sai desta maquina. Rode no PowerShell dentro de D:\IA:
#   .\scripts\set-admin-password.ps1

$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $PSScriptRoot
$runtimeDir = Join-Path $projectRoot '.runtime'
$pythonPath = Join-Path $projectRoot '.venv\Scripts\python.exe'
$temporaryPython = Join-Path $env:TEMP 'ia-8811-backend\Scripts\python.exe'
if (Test-Path -LiteralPath $temporaryPython) {
    $pythonPath = $temporaryPython
}
if (-not (Test-Path -LiteralPath $pythonPath)) {
    throw 'Ambiente Python ausente.'
}

$secretPath = Join-Path $runtimeDir 'webui-secret.key'
if (-not (Test-Path -LiteralPath $secretPath)) {
    throw "Chave secreta ausente em $secretPath. Inicie a MingHat ao menos uma vez."
}
$secret = (Get-Content -LiteralPath $secretPath -Raw).Trim()

$p1 = Read-Host -AsSecureString 'Nova senha do admin'
$p2 = Read-Host -AsSecureString 'Confirme a senha'
$plain1 = [System.Runtime.InteropServices.Marshal]::PtrToStringBSTR(
    [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($p1))
$plain2 = [System.Runtime.InteropServices.Marshal]::PtrToStringBSTR(
    [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($p2))

if ($plain1 -ne $plain2) {
    throw 'As senhas nao conferem.'
}
if ($plain1.Length -lt 8) {
    throw 'Use ao menos 8 caracteres.'
}

$env:WEBUI_SECRET_KEY = $secret
$env:WEBUI_AUTH = 'True'
$env:MINGHAT_ADMIN_EMAIL = $Email
$env:MINGHAT_ADMIN_PW = $plain1

$py = @'
import os, sqlite3, asyncio, sys
sys.path.insert(0, "backend")
from open_webui.utils.auth import get_password_hash

email = os.environ["MINGHAT_ADMIN_EMAIL"]
pw = os.environ["MINGHAT_ADMIN_PW"]
h = asyncio.new_event_loop().run_until_complete(get_password_hash(pw))

db = os.path.join("backend", "data", "webui.db")
con = sqlite3.connect(db)
n = con.execute("UPDATE auth SET password=?, active=1 WHERE email=?", (h, email)).rowcount
con.commit()
con.close()
print("OK" if n else "NENHUM_USUARIO", email)
'@

Push-Location $projectRoot
try {
    & $pythonPath -c $py
} finally {
    Pop-Location
    Remove-Item Env:MINGHAT_ADMIN_EMAIL -ErrorAction SilentlyContinue
    Remove-Item Env:MINGHAT_ADMIN_PW -ErrorAction SilentlyContinue
    Remove-Item Env:WEBUI_SECRET_KEY -ErrorAction SilentlyContinue
    Remove-Item Env:WEBUI_AUTH -ErrorAction SilentlyContinue
    $plain1 = $null; $plain2 = $null
}

Write-Host ''
Write-Host "Senha definida para $Email." -ForegroundColor Green
Write-Host "Entre em https://minghat.com.br com $Email e a senha que voce digitou." -ForegroundColor Cyan
