$commands = @("multica", "node", "npx")
$missing = $commands | Where-Object { -not (Get-Command $_ -ErrorAction SilentlyContinue) }
if ($missing) { throw "Missing commands: $($missing -join ', ')" }

if (-not (Test-Path "config/mcp-servers.json")) {
  Write-Warning "Copy config/mcp-servers.example.json to config/mcp-servers.json and set the JetBrains JAR path."
} else {
  Get-Content "config/mcp-servers.json" -Raw | ConvertFrom-Json | Out-Null
  Write-Host "MCP configuration is valid JSON."
}
