# Prepare-ROMs.ps1 - build a runtime-ready KOF '97 ROM folder from your own
# dumps.  This script extracts the MAME kof97 and neogeo sets; it does not
# download anything and contains no ROM data.
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File .\Prepare-ROMs.ps1
#   powershell -ExecutionPolicy Bypass -File .\Prepare-ROMs.ps1 -Kof97Zip C:\path\kof97.zip -NeoGeoZip C:\path\neogeo.zip

param(
    [string]$Kof97Zip = "",
    [string]$NeoGeoZip = "",
    [string]$OutDir = ""
)

$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $OutDir) { $OutDir = Join-Path $here "roms" }

function Ask-Zip($label, $current) {
    if ($current -and (Test-Path $current)) { return (Resolve-Path $current).Path }
    while ($true) {
        $p = Read-Host "Path to $label"
        $p = $p.Trim('"').Trim()
        if (Test-Path $p) { return (Resolve-Path $p).Path }
        Write-Host "Not found: $p" -ForegroundColor Yellow
    }
}

$Kof97Zip = Ask-Zip "kof97.zip" $Kof97Zip
$NeoGeoZip = Ask-Zip "neogeo.zip" $NeoGeoZip

New-Item -ItemType Directory -Force $OutDir | Out-Null

Write-Host "Extracting $Kof97Zip"
tar -xf $Kof97Zip -C $OutDir
if ($LASTEXITCODE -ne 0) { throw "Could not extract kof97.zip with tar" }
Write-Host "Extracting $NeoGeoZip"
tar -xf $NeoGeoZip -C $OutDir
if ($LASTEXITCODE -ne 0) { throw "Could not extract neogeo.zip with tar" }

Write-Host ""
Write-Host "Done. Run:" -ForegroundColor Green
Write-Host "  .\`"kof 97.exe`" --rom-path `"$OutDir`""
