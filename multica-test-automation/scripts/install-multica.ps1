param([string]$Python = "python")

& $Python -m pip install --upgrade multica
if ($LASTEXITCODE -ne 0) { throw "Multica installation failed." }
Write-Host "Multica installed. Run scripts/verify-mcp.ps1 next."
