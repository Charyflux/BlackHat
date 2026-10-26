param(
    [string[]]$Hostnames = @('minghat.com.br', 'www.minghat.com.br', 'chat.minghat.com.br'),
    [int]$LocalPort = 8811,
    [string]$LandingHost = 'www.minghat.com.br',
    [int]$LandingPort = 8815,
    [string]$LandingPath = '^/home(/.*)?$',
    # Ambiente de staging/teste (worktree D:\IA-staging), atras do proxy com
    # Basic Auth (scripts/staging-basic-auth-proxy.cjs). Nao aponta direto pro
    # vite do staging para nao expor sem senha.
    [string]$StagingHost = 'teste.minghat.com.br',
    [int]$StagingPort = 8822,
    [string]$TunnelName = 'minghat',
    [string]$TunnelId = '870b4e6a-8362-4168-91c8-9653bc035185'
)

$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $PSScriptRoot
$runtimeDir = Join-Path $projectRoot '.runtime'
$configPath = Join-Path $runtimeDir 'cloudflared-minghat.yml'
$credentialsFile = Join-Path $env:USERPROFILE ".cloudflared\$TunnelId.json"

if (-not (Get-Command cloudflared -ErrorAction SilentlyContinue)) {
    throw 'cloudflared nao encontrado no PATH. Instale o conector antes de iniciar o tunnel.'
}

if (-not (Test-Path -LiteralPath $credentialsFile)) {
    throw "Credenciais do tunnel nao encontradas em: $credentialsFile"
}

$localService = "http://127.0.0.1:$LocalPort"
$localUp = Test-NetConnection -ComputerName '127.0.0.1' -Port $LocalPort -InformationLevel Quiet -WarningAction SilentlyContinue
if (-not $localUp) {
    Write-Warning "Nada escutando em $localService. Inicie a MingHat antes (start-local.ps1 ou start-production.ps1)."
}

New-Item -ItemType Directory -Path $runtimeDir -Force | Out-Null

# A regra de path da landing precisa vir ANTES da regra geral do mesmo host.
$landingRule = "  - hostname: $LandingHost`n    path: $LandingPath`n    service: http://127.0.0.1:$LandingPort"
$stagingRule = "  - hostname: $StagingHost`n    service: http://127.0.0.1:$StagingPort"

$ingressLines = foreach ($hostname in $Hostnames) {
    "  - hostname: $hostname`n    service: $localService"
}

$config = @"
tunnel: $TunnelId
credentials-file: $credentialsFile

ingress:
$landingRule
$stagingRule
$($ingressLines -join "`n")
  - service: http_status:404
"@

Set-Content -LiteralPath $configPath -Value $config -Encoding ASCII

Write-Host "Tunnel '$TunnelName' -> $localService" -ForegroundColor Cyan
foreach ($hostname in $Hostnames) {
    Write-Host "  https://$hostname" -ForegroundColor Cyan
}
Write-Host "  https://$LandingHost/home -> http://127.0.0.1:$LandingPort (landing)" -ForegroundColor Cyan
Write-Host "  https://$StagingHost -> http://127.0.0.1:$StagingPort (staging, com Basic Auth)" -ForegroundColor Cyan

$dnsRouteCheck = cloudflared tunnel route dns $TunnelName $StagingHost 2>&1
Write-Host $dnsRouteCheck -ForegroundColor DarkGray

cloudflared tunnel --config $configPath run $TunnelName
