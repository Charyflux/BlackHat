param(
    [string]$Root = (Split-Path -Parent $PSScriptRoot)
)

$ErrorActionPreference = 'Stop'

$ignoreDirs = @(
    '.git',
    '.runtime',
    '.svelte-kit',
    'build',
    'coverage',
    'node_modules',
    'dist',
    'static\pyodide',
    'static/pyodide',
    '.venv',
    'venv'
)

$allowedExtensions = @(
    '.env',
    '.example',
    '.js',
    '.ts',
    '.svelte',
    '.py',
    '.ps1',
    '.json',
    '.yaml',
    '.yml',
    '.md',
    '.toml',
    '.html',
    '.css'
)
$ignoredFiles = @('yarn.lock', 'package-lock.json', 'pnpm-lock.yaml')

$secretPatterns = [ordered]@{
    'AWS access key' = 'AKIA[0-9A-Z]{16}'
    'OpenAI API key' = 'sk-[A-Za-z0-9_\-]{20,}'
    'Cloudflare token' = '(?i)cloudflare(.{0,40})?(api[_-]?token|global[_-]?api[_-]?key|secret)'
    'Private key block' = '-----BEGIN (?:RSA |EC |OPENSSH |)?PRIVATE KEY-----'
    'GitHub token' = 'gh[pousr]_[A-Za-z0-9_]{36,}'
    'Google API key' = 'AIza[0-9A-Za-z\-_]{35}'
}

$allowedFake = @(
    'AKIAFAKEFAKEFAKEFAKE',
    'sk-fake-minghat-decoy-token-do-not-use'
)

$gitFiles = @()
try {
    Push-Location $Root
    $gitFiles = git ls-files --cached --others --exclude-standard 2>$null
} finally {
    Pop-Location
}

if ($gitFiles.Count -gt 0) {
    $files = $gitFiles | ForEach-Object { Get-Item -LiteralPath (Join-Path $Root $_) -ErrorAction SilentlyContinue } | Where-Object {
        $null -ne $_ -and -not $_.PSIsContainer
    }
} else {
    $files = Get-ChildItem -LiteralPath $Root -Recurse -File -Force
}

$files = $files | Where-Object {
    $rootPrefix = $Root.TrimEnd('\', '/') + [IO.Path]::DirectorySeparatorChar
    $relative = $_.FullName.Substring($rootPrefix.Length)
    $extensionAllowed = $allowedExtensions -contains $_.Extension.ToLowerInvariant() -or $_.Name -like '.env*'
    $notIgnoredDirectory = -not ($ignoreDirs | Where-Object { $relative -eq $_ -or $relative.StartsWith("$_\") -or $relative.StartsWith("$_/") })
    $notIgnoredFile = -not ($ignoredFiles -contains $_.Name)
    $extensionAllowed -and $notIgnoredDirectory -and $notIgnoredFile
}

$findings = New-Object System.Collections.Generic.List[string]
foreach ($file in $files) {
    $rootPrefix = $Root.TrimEnd('\', '/') + [IO.Path]::DirectorySeparatorChar
    $relative = $file.FullName.Substring($rootPrefix.Length)
    $content = Get-Content -LiteralPath $file.FullName -Raw -ErrorAction SilentlyContinue
    if ($null -eq $content) {
        continue
    }
    foreach ($patternName in $secretPatterns.Keys) {
        foreach ($match in [regex]::Matches($content, $secretPatterns[$patternName])) {
            if ($allowedFake -contains $match.Value) {
                continue
            }
            $findings.Add("$relative :: $patternName :: $($match.Value.Substring(0, [Math]::Min(80, $match.Value.Length)))")
        }
    }
}

if ($findings.Count -gt 0) {
    Write-Host 'Possíveis segredos encontrados:'
    $findings | ForEach-Object { Write-Host " - $_" }
    exit 1
}

Write-Host 'Nenhum segredo real aparente encontrado nos arquivos rastreáveis.'
