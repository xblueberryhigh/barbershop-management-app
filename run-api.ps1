$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$apiDir = Join-Path $repoRoot "api"
$uvicornPath = Join-Path $apiDir ".venv\Scripts\uvicorn.exe"

if (-not (Test-Path $uvicornPath)) {
    throw "uvicorn executable not found at $uvicornPath"
}

& $uvicornPath "app.main:app" --reload --app-dir $apiDir
