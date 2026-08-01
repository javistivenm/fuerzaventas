$ErrorActionPreference = "Stop"
$BridgeRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location -LiteralPath $BridgeRoot

Write-Host "Arquitectura de Python:"
& py -3-32 -c "import struct; print(struct.calcsize('P') * 8, 'bits')"

& py -3-32 -m venv .venv
& ".venv\Scripts\python.exe" -m pip install --upgrade pip
& ".venv\Scripts\python.exe" -m pip install -r requirements.txt

if (-not (Test-Path ".env")) {
    Copy-Item -LiteralPath ".env.example" -Destination ".env"
}

New-Item -ItemType Directory -Force -Path "logs" | Out-Null
Write-Host "Instalación completada. Edite .env antes de ejecutar run.ps1."

