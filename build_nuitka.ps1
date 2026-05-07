# PDF Compare Viewer V2 - Nuitka Build Script (PowerShell)
# This script builds a lightweight single-file exe using Nuitka

param(
    [switch]$SkipCleanup
)

$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot
$OutputName = "PDF_Compare_Viewer_V2.exe"
$OutputDir = Join-Path $ProjectRoot "dist\PDF_Compare_Viewer_V2_Nuitka_Light"

Write-Host "================================================"
Write-Host "PDF Compare Viewer V2 - Nuitka Builder"
Write-Host "================================================"
Write-Host ""

# Check if icon.ico exists
$IconPath = Join-Path $ProjectRoot "icon.ico"
if (-not (Test-Path $IconPath)) {
    Write-Host "ERROR: icon.ico not found in project root!" -ForegroundColor Red
    Write-Host "Please ensure icon.ico exists in: $ProjectRoot" -ForegroundColor Red
    exit 1
}

# Check if Python 3.11 is available
try {
    $pythonVersion = py -3.11 --version 2>&1
    Write-Host "Found: $pythonVersion"
} catch {
    Write-Host "ERROR: Python 3.11 not found. Please install Python 3.11." -ForegroundColor Red
    exit 1
}

# Check if Nuitka is available
try {
    $nuitkaVersion = py -3.11 -m nuitka --version 2>&1
    Write-Host "Nuitka: $nuitkaVersion"
} catch {
    Write-Host "Nuitka not found. Installing..." -ForegroundColor Yellow
    py -3.11 -m pip install nuitka
}

# Set working directory
Set-Location $ProjectRoot

# Clean previous build
if (-not $SkipCleanup -and (Test-Path $OutputDir)) {
    Write-Host "Cleaning previous build..." -ForegroundColor Cyan
    Remove-Item -Recurse -Force $OutputDir
}

# Create dist folder
$DistDir = Join-Path $ProjectRoot "dist"
if (-not (Test-Path $DistDir)) {
    New-Item -ItemType Directory -Path $DistDir | Out-Null
}

Write-Host ""
Write-Host "================================================"
Write-Host "Building with Nuitka..."
Write-Host "================================================"
Write-Host ""

# Build command with anti-bloat options
$BuildArgs = @(
    "--onefile",
    "--windows-disable-console",
    "--windows-icon-from-ico=`"$ProjectRoot\icon.ico`"",
    "--enable-plugin=pyside6",
    "--assume-yes-for-downloads",
    "--show-progress",
    "--report=compilation_report.html",
    "--output-filename=$OutputName",
    "--output-dir=$OutputDir",
    "--include-data-file=`"$ProjectRoot\icon.ico`"=`"icon.ico`"",
    "--noinclude-pytest-mode=nofollow",
    "--noinclude-unittest-mode=nofollow",
    "--noinclude-IPython-mode=nofollow",
    "--noinclude-setuptools-mode=nofollow",
    "--noinclude-pydoc-mode=nofollow",
    "starter/main.py"
)

& py -3.11 -m nuitka $BuildArgs

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERROR: Nuitka build failed!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "================================================"
Write-Host "Build completed successfully!" -ForegroundColor Green
Write-Host "================================================"
Write-Host ""

# Get file size
$ExePath = Join-Path $OutputDir $OutputName
if (Test-Path $ExePath) {
    $FileSize = (Get-Item $ExePath).Length
    $FileSizeMB = [math]::Round($FileSize / 1MB, 2)
    Write-Host "Output: $ExePath"
    Write-Host "Size: $FileSizeMB MB ($FileSize bytes)"
}

# Show comparison if old build exists
$OldExePath = Join-Path $ProjectRoot "dist\PDF_Compare_Viewer_V2_Nuitka\PDF_Compare_Viewer_V2.exe"
if (Test-Path $OldExePath) {
    $OldFileSize = (Get-Item $OldExePath).Length
    $OldFileSizeMB = [math]::Round($OldFileSize / 1MB, 2)
    Write-Host ""
    Write-Host "Comparison with previous build:"
    Write-Host "  Previous: $OldFileSizeMB MB"
    if ($FileSize -and $OldFileSize) {
        $Diff = $OldFileSize - $FileSize
        $DiffMB = [math]::Round($Diff / 1MB, 2)
        $Pct = [math]::Round(($FileSize / $OldFileSize) * 100, 1)
        Write-Host "  New:      $FileSizeMB MB"
        Write-Host "  Saved:    $DiffMB MB ($Pct%)"
    }
}

Write-Host ""
Write-Host "Compilation report: $ProjectRoot\compilation_report.html"
Write-Host ""
