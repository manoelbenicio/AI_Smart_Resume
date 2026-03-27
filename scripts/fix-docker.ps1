#Requires -RunAsAdministrator
<#
.SYNOPSIS
    Fixes Docker Desktop startup by recreating the missing registry key.
.DESCRIPTION
    Docker Desktop fails to start when its registry key at
    HKLM:\SOFTWARE\Docker Inc.\Docker Desktop is missing.
    This script recreates it with the correct install path,
    then relaunches Docker Desktop.
.NOTES
    Run this from an elevated PowerShell terminal:
    powershell -ExecutionPolicy Bypass -File .\scripts\fix-docker.ps1
#>

$ErrorActionPreference = "Stop"

$dockerExe     = "C:\Program Files\Docker\Docker\Docker Desktop.exe"
$regPath       = "HKLM:\SOFTWARE\Docker Inc.\Docker Desktop"
$installPath   = "C:\Program Files\Docker\Docker"

# 1. Validate Docker Desktop installation
if (-not (Test-Path $dockerExe)) {
    Write-Error "Docker Desktop not found at $dockerExe"
    exit 1
}
Write-Host "[OK] Docker Desktop binary found" -ForegroundColor Green

# 2. Kill any orphan Docker processes (safe — they're already non-functional)
$dockerProcs = Get-Process -Name "*Docker*" -ErrorAction SilentlyContinue
if ($dockerProcs) {
    Write-Host "[INFO] Stopping orphan Docker processes..."
    $dockerProcs | Stop-Process -Force -ErrorAction SilentlyContinue
    Start-Sleep 3
}

# 3. Create the missing registry key
Write-Host "[FIX] Creating registry key: $regPath"
New-Item -Path "HKLM:\SOFTWARE\Docker Inc." -Force | Out-Null
New-Item -Path $regPath -Force | Out-Null
Set-ItemProperty -Path $regPath -Name "InstallPath" -Value $installPath -Type String
Set-ItemProperty -Path $regPath -Name "BinPath"     -Value "$installPath\resources\bin" -Type String
Set-ItemProperty -Path $regPath -Name "Version"     -Value "4.39.0" -Type String

# Verify
$check = Get-ItemProperty -Path $regPath -ErrorAction SilentlyContinue
if ($check) {
    Write-Host "[OK] Registry key created:" -ForegroundColor Green
    Write-Host "     InstallPath = $($check.InstallPath)"
    Write-Host "     BinPath     = $($check.BinPath)"
} else {
    Write-Error "Failed to create registry key"
    exit 1
}

# 4. Ensure Docker CLI is on PATH
$currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
$binPath = "$installPath\resources\bin"
if ($currentPath -notlike "*$binPath*") {
    Write-Host "[FIX] Adding Docker CLI to system PATH..."
    [Environment]::SetEnvironmentVariable("Path", "$currentPath;$binPath", "Machine")
    $env:Path = "$env:Path;$binPath"
    Write-Host "[OK] PATH updated" -ForegroundColor Green
} else {
    Write-Host "[OK] Docker CLI already on PATH" -ForegroundColor Green
}

# 5. Relaunch Docker Desktop
Write-Host "[INFO] Launching Docker Desktop..."
Start-Process $dockerExe
Write-Host ""
Write-Host "=== Docker Desktop is starting ===" -ForegroundColor Cyan
Write-Host "Wait 60-90 seconds, then verify with: docker info"
Write-Host ""
