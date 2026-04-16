[CmdletBinding()]
param(
    [switch]$Clean
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$distPath = Join-Path $projectRoot "dist"
$buildPath = Join-Path $projectRoot "build"

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

try {
    python -m PyInstaller --version | Out-Null
}
catch {
    throw "PyInstaller is not installed. Run: python -m pip install pyinstaller"
}

python -m PyInstaller `
    --noconfirm `
    --clean `
    --windowed `
    --onedir `
    --name "24-Hour-Digital-Clock" `
    --distpath "dist" `
    --workpath "build\pyinstaller" `
    --specpath "build" `
    "24-Hour-Digital-Clock.py"
