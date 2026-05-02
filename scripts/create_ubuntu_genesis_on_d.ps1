param(
    [string]$TargetDistro = "Ubuntu-Genesis",
    [string]$Target = "D:\WSL\Ubuntu-Genesis",
    [string]$ImageDir = "D:\WSL\Images",
    [string]$RootfsUrl = "https://cloud-images.ubuntu.com/wsl/releases/noble/current/ubuntu-noble-wsl-amd64-24.04lts.rootfs.tar.gz",
    [string]$DefaultUser = "crazat"
)

$ErrorActionPreference = "Stop"

$existing = Get-ItemProperty "HKCU:\Software\Microsoft\Windows\CurrentVersion\Lxss\*" |
    Where-Object { $_.DistributionName -eq $TargetDistro } |
    Select-Object -First 1

if ($existing) {
    throw "Target distro already exists: $TargetDistro at $($existing.BasePath). Refusing to overwrite."
}

New-Item -ItemType Directory -Force $Target | Out-Null
New-Item -ItemType Directory -Force $ImageDir | Out-Null

$rootfs = Join-Path $ImageDir "ubuntu-noble-wsl-amd64-24.04lts.rootfs.tar.gz"
if (-not (Test-Path $rootfs)) {
    Write-Host "Downloading Ubuntu 24.04 WSL rootfs: $RootfsUrl"
    curl.exe -L --fail --output $rootfs $RootfsUrl
}

Write-Host "Importing $TargetDistro to $Target"
wsl --import $TargetDistro $Target $rootfs --version 2

Write-Host "Configuring user $DefaultUser"
wsl -d $TargetDistro -u root -- bash -lc @"
set -e
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y sudo rsync git curl ca-certificates
if getent passwd 1000 >/dev/null 2>&1; then
    current=\$(getent passwd 1000 | cut -d: -f1)
    if [ "\$current" != "$DefaultUser" ]; then
        usermod -l "$DefaultUser" -d "/home/$DefaultUser" -m "\$current"
        groupmod -n "$DefaultUser" "\$current" || true
    fi
else
    useradd -m -s /bin/bash -u 1000 "$DefaultUser"
fi
usermod -aG sudo "$DefaultUser"
printf '[user]\ndefault=$DefaultUser\n[automount]\noptions=metadata,umask=22,fmask=11\n' > /etc/wsl.conf
chown -R "$DefaultUser:$DefaultUser" "/home/$DefaultUser"
"@

wsl --terminate $TargetDistro

Write-Host "Created $TargetDistro. Next run scripts/stage_genesis_to_ubuntu_genesis.sh from the source Ubuntu."
