# Start script for the PLC MCP Bridge
$PROJECT_ROOT = "c:\Users\hugod\Documents\Projects\PLC_MCP\Core"

# Set environment mode (MOCK or LIVE)
if ($null -eq $env:PLC_MODE) {
    $env:PLC_MODE = "LIVE"
}

$VENV_PYTHON = Join-Path $PROJECT_ROOT ".venv\Scripts\python.exe"

if (Test-Path $VENV_PYTHON) {
    Write-Host "Starting PLC-Bridge using virtual environment: $VENV_PYTHON" -ForegroundColor Cyan
    & $VENV_PYTHON "$PROJECT_ROOT\server.py"
}
else {
    Write-Host "Warning: .venv not found at $VENV_PYTHON. Using system python..." -ForegroundColor Yellow
    python "$PROJECT_ROOT\server.py"
}
