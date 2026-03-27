param(
    [Parameter(Position = 0)]
    [ValidateSet("up", "down", "build", "test", "logs", "shell", "health", "clean", "help")]
    [string]$Target = "help"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$useLegacyCompose = $null -ne (Get-Command docker-compose -ErrorAction SilentlyContinue)

function Invoke-Compose {
    param([string[]]$ComposeArgs)
    if ($useLegacyCompose) {
        & docker-compose @ComposeArgs
    }
    else {
        & docker compose @ComposeArgs
    }
}

switch ($Target) {
    "up" { Invoke-Compose @("up", "-d") }
    "down" { Invoke-Compose @("down") }
    "build" { Invoke-Compose @("up", "-d", "--build") }
    "test" { Invoke-Compose @("exec", "-T", "smart-resume-api", "pytest", "tests/", "-v") }
    "logs" { Invoke-Compose @("logs", "-f", "smart-resume-api") }
    "shell" { Invoke-Compose @("exec", "smart-resume-api", "/bin/sh") }
    "health" {
        $response = Invoke-WebRequest -Uri "http://localhost:8001/api/v1/health"
        $response.Content
    }
    "clean" { Invoke-Compose @("down", "-v", "--remove-orphans") }
    default {
        Write-Host "Usage: .\scripts\run.ps1 <target>"
        Write-Host "Targets: up, down, build, test, logs, shell, health, clean"
    }
}
