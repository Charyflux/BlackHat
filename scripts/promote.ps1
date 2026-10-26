# Promove codigo de um ambiente para o proximo (dev -> staging -> main/producao).
# So faz fast-forward/merge local, nao publica em nenhum remoto.
#
# Uso:
#   scripts\promote.ps1 -From dev -To staging
#   scripts\promote.ps1 -From staging -To main
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('dev', 'staging')]
    [string]$From,

    [Parameter(Mandatory = $true)]
    [ValidateSet('staging', 'main')]
    [string]$To
)

$ErrorActionPreference = 'Stop'

if ($From -eq 'dev' -and $To -ne 'staging') {
    throw 'De "dev" so pode promover para "staging".'
}
if ($From -eq 'staging' -and $To -ne 'main') {
    throw 'De "staging" so pode promover para "main".'
}

$worktrees = @{
    'dev'     = 'D:\IA-dev'
    'staging' = 'D:\IA-staging'
    'main'    = 'D:\IA'
}

$targetDir = $worktrees[$To]
if (-not (Test-Path -LiteralPath $targetDir)) {
    throw "Worktree de '$To' nao encontrado em $targetDir"
}

Write-Host "Promovendo '$From' -> '$To' (em $targetDir)..." -ForegroundColor Cyan
Push-Location $targetDir
try {
    $status = git status --porcelain
    if ($status) {
        throw "O worktree de '$To' tem mudancas nao commitadas. Resolva antes de promover:`n$status"
    }

    git merge --no-edit $From
    Write-Host "Merge de '$From' em '$To' concluido." -ForegroundColor Green

    if ($To -eq 'staging') {
        Write-Host "Reinicie o ambiente de staging: scripts\start-staging.ps1 (rodando dentro de $targetDir)" -ForegroundColor Yellow
    } elseif ($To -eq 'main') {
        Write-Host "Reinicie a producao: scripts\start-local.ps1 (rodando dentro de $targetDir)" -ForegroundColor Yellow
    }
} finally {
    Pop-Location
}
