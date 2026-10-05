$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
if (-not (Test-Path -LiteralPath '.venv/Scripts/python.exe')) {
    throw 'Run ./setup.ps1 first.'
}
. ./.venv/Scripts/Activate.ps1
& ./.venv/Scripts/python.exe scripts/preflight.py
if ($LASTEXITCODE -ne 0) { throw 'Fix the preflight errors before teaching.' }
& ./.venv/Scripts/python.exe -m jupyterlab
