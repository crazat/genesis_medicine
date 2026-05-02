param(
    [string]$SourceDistro = "Ubuntu",
    [string]$TargetDistro = "Ubuntu-Genesis",
    [string]$Target = "D:\WSL\Ubuntu-Genesis",
    [string]$Archive = "D:\genesis_archive"
)

$ErrorActionPreference = "Stop"

function To-GB($bytes) {
    return [math]::Round($bytes / 1GB, 1)
}

$distros = Get-ItemProperty "HKCU:\Software\Microsoft\Windows\CurrentVersion\Lxss\*"
$source = $distros | Where-Object { $_.DistributionName -eq $SourceDistro } | Select-Object -First 1
$targetDistroInfo = $distros | Where-Object { $_.DistributionName -eq $TargetDistro } | Select-Object -First 1

if (-not $source) {
    throw "Source WSL distro not found: $SourceDistro"
}

New-Item -ItemType Directory -Force $Target | Out-Null
New-Item -ItemType Directory -Force $Archive | Out-Null
New-Item -ItemType Directory -Force "D:\WSL\Backups" | Out-Null

$d = Get-PSDrive -Name D
$c = Get-PSDrive -Name C

[PSCustomObject]@{
    SourceDistro = $SourceDistro
    SourceBasePath = $source.BasePath
    TargetDistro = $TargetDistro
    TargetAlreadyExists = [bool]$targetDistroInfo
    Target = $Target
    Archive = $Archive
    CFreeGB = To-GB $c.Free
    DFreeGB = To-GB $d.Free
    NextStep = "Use create_ubuntu_genesis_on_d.ps1 during a maintenance window"
} | Format-List

Write-Host ""
Write-Host "WSL state:"
wsl -l -v

Write-Host ""
Write-Host "Readiness check complete. This script does not stop WSL or move data."
