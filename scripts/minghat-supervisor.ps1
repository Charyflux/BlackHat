# MingHat: supervisor. Sobe tudo no início e reergue o que cair a cada 5 minutos.
# Iniciado pelo atalho na pasta Inicializar do Windows (logon), rodando oculto.

$scriptDir = $PSScriptRoot
while ($true) {
    try {
        & (Join-Path $scriptDir 'start-all.ps1')
    } catch {}
    Start-Sleep -Seconds 300
}
