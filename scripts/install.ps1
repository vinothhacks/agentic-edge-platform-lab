# Agentic Edge Platform Lab - one-line installer (Windows / PowerShell)
#
# Usage:
#   irm https://raw.githubusercontent.com/vinothhacks/agentic-edge-platform-lab/main/scripts/install.ps1 | iex

$ErrorActionPreference = "Stop"

$Repo   = "https://github.com/vinothhacks/agentic-edge-platform-lab.git"
$Dir    = if ($env:AEPL_DIR)    { $env:AEPL_DIR }    else { "agentic-edge-platform-lab" }
$Branch = if ($env:AEPL_BRANCH) { $env:AEPL_BRANCH } else { "main" }

function Say($m)  { Write-Host "==> $m" -ForegroundColor Cyan }
function Ok($m)   { Write-Host "OK  $m" -ForegroundColor Green }
function Warn($m) { Write-Host "!   $m" -ForegroundColor Yellow }
function Die($m)  { Write-Host "X   $m" -ForegroundColor Red; exit 1 }

function Need($cmd) {
    if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) {
        Die "Missing required tool: $cmd"
    }
}

Say "Checking prerequisites"
Need git
Need docker
try { docker compose version | Out-Null } catch { Die "docker compose v2 plugin is required" }
Ok  "git + docker compose present"

if (Test-Path "$Dir\.git") {
    Say "Repo already exists at $Dir - pulling latest"
    git -C $Dir fetch --depth=1 origin $Branch | Out-Null
    git -C $Dir reset --hard "origin/$Branch" | Out-Null
} else {
    Say "Cloning $Repo into $Dir"
    git clone --depth=1 --branch $Branch $Repo $Dir | Out-Null
}
Ok "Source ready"

Set-Location $Dir

if ($env:AEPL_SKIP_UP) {
    Warn "AEPL_SKIP_UP set - not booting the stack"
} else {
    Say "Building and starting the stack (this is a one-time cost)"
    docker compose up -d --build
    Ok "Stack is up"

    Write-Host ""
    Write-Host "Done." -ForegroundColor Green
    Write-Host "  Broker API:    http://localhost:8000/docs"
    Write-Host "  Edge (Envoy):  http://localhost:10000"
}
