$ErrorActionPreference = "Stop"
$BridgeRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -LiteralPath $BridgeRoot

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    throw "No existe .venv. Ejecute primero scripts\install.ps1 con Python de 32 bits."
}

& ".venv\Scripts\python.exe" -m uvicorn app.main:app `
    --host ((Get-Content ".env" | Where-Object { $_ -match '^BRIDGE_HOST=' }) -replace '^BRIDGE_HOST=', '') `
    --port 8787

