param([switch]$Launch)
$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    if (-not (Test-Path -LiteralPath '.venv/Scripts/python.exe')) {
        python -m venv .venv
        if ($LASTEXITCODE -ne 0) { throw 'Could not create .venv.' }
    }
    $coursePython = Join-Path $PSScriptRoot '.venv/Scripts/python.exe'
    $courseRequirements = if (Test-Path 'requirements-lock.txt') { 'requirements-lock.txt' } else { 'requirements.txt' }
    & $coursePython -m pip install --no-compile -r $courseRequirements
    if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }
    if (-not (Test-Path -LiteralPath '.env')) { Copy-Item '.env.example' '.env' }
    & $coursePython -m ipykernel install --sys-prefix --name agentic-ai-course --display-name 'Python (Agentic AI Course)'
    if ($LASTEXITCODE -ne 0) { throw 'Kernel registration failed.' }
    & $coursePython scripts/preflight.py
    if ($LASTEXITCODE -ne 0) { throw 'Preflight failed. Check the messages above and your .env settings.' }
    . ./.venv/Scripts/Activate.ps1
    Write-Host 'Course environment activated. The notebooks load .env automatically.'
    if ($Launch) { & $coursePython -m jupyterlab }
} finally { Pop-Location }
