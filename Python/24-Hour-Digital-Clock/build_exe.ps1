[CmdletBinding()]
param(
    [switch]$Clean,
    [switch]$OneFile
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$distPath = Join-Path $projectRoot "dist"
$buildPath = Join-Path $projectRoot "build"

function Get-AvailablePythonCandidates {
    $windowsAppsPath = Join-Path $env:LOCALAPPDATA "Microsoft\WindowsApps"
    $windowsAppsResolved = [System.IO.Path]::GetFullPath($windowsAppsPath)
    $seen = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
    $candidates = [System.Collections.Generic.List[string]]::new()

    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCommand) {
        $commandPath = [System.IO.Path]::GetFullPath($pythonCommand.Source)
        if (-not $commandPath.StartsWith($windowsAppsResolved, [System.StringComparison]::OrdinalIgnoreCase)) {
            if ($seen.Add($commandPath)) {
                [void]$candidates.Add($commandPath)
            }
        }
    }

    foreach ($candidate in (& where.exe python 2>$null)) {
        if (-not [string]::IsNullOrWhiteSpace($candidate)) {
            $resolved = [System.IO.Path]::GetFullPath($candidate.Trim())
            if (-not $resolved.StartsWith($windowsAppsResolved, [System.StringComparison]::OrdinalIgnoreCase)) {
                if ($seen.Add($resolved)) {
                    [void]$candidates.Add($resolved)
                }
            }
        }
    }

    return $candidates
}

function Resolve-PythonCommand {
    $usableCandidates = [System.Collections.Generic.List[string]]::new()
    $pyInstallerCandidates = [System.Collections.Generic.List[string]]::new()

    foreach ($candidate in (Get-AvailablePythonCandidates)) {
        try {
            & $candidate -c "import sys" 2>$null | Out-Null
            [void]$usableCandidates.Add($candidate)
        }
        catch {
            continue
        }

        try {
            & $candidate -m PyInstaller --version 2>$null | Out-Null
            [void]$pyInstallerCandidates.Add($candidate)
        }
        catch {
            continue
        }
    }

    if ($pyInstallerCandidates.Count -gt 0) {
        return $pyInstallerCandidates[0]
    }

    if ($usableCandidates.Count -eq 0) {
        throw "No usable Python interpreter was found on PATH. Install Python 3.10+ and make sure it is available outside the Microsoft Store alias."
    }

    $pythonPath = $usableCandidates[0]
    throw "PyInstaller is not installed for '$pythonPath'. Run: `"$pythonPath`" -m pip install pyinstaller"
}

if ($Clean) {
    foreach ($targetPath in @($distPath, $buildPath)) {
        $resolvedTarget = [System.IO.Path]::GetFullPath($targetPath)
        $resolvedRoot = [System.IO.Path]::GetFullPath($projectRoot)
        if ($resolvedTarget.StartsWith($resolvedRoot) -and (Test-Path -LiteralPath $resolvedTarget)) {
            Remove-Item -LiteralPath $resolvedTarget -Recurse -Force
        }
    }
}

Set-Location $projectRoot

$pythonCommand = Resolve-PythonCommand
$bundleMode = if ($OneFile) { "--onefile" } else { "--onedir" }
$bundleLabel = if ($OneFile) { "onefile" } else { "onedir" }

Write-Host "Using Python: $pythonCommand"
Write-Host "Bundle mode: $bundleLabel"

& $pythonCommand -m PyInstaller `
    --noconfirm `
    --clean `
    --windowed `
    $bundleMode `
    --name "24-Hour-Digital-Clock" `
    --distpath "dist" `
    --workpath "build\pyinstaller" `
    --specpath "build" `
    "24-Hour-Digital-Clock.py"
