#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BUILD="$ROOT/build"
ROOTFS="$BUILD/ubuntu-plasma-rootfs"
IMAGE="$BUILD/eos-ubuntu-plasma-reference.img"
MOUNT="$BUILD/ubuntu-plasma-mount"
SIZE="${EOS_PLASMA_IMAGE_SIZE:-8G}"
MIRROR="${EOS_UBUNTU_MIRROR:-http://archive.ubuntu.com/ubuntu}"
EOS_UBUNTU_SUITE="${EOS_UBUNTU_SUITE:-noble}"

PACKAGES="ubuntu-minimal systemd-sysv dbus-x11 xorg xserver-xorg-video-qxl xserver-xorg-input-all plasma-desktop plasma-workspace kwin-x11 sddm calamares konsole dolphin network-manager sudo locales fonts-noto"

sudo umount -R "$ROOTFS" 2>/dev/null || true
sudo rm -rf "$ROOTFS" "$MOUNT"
mkdir -p "$ROOTFS" "$MOUNT"

sudo mmdebstrap --mode=root --variant=apt --architectures=amd64 --include="$PACKAGES" \
  --components="main,universe" \
  "$EOS_UBUNTU_SUITE" "$ROOTFS" "$MIRROR"

sudo install -d -m 0755 "$ROOTFS/etc/systemd/system/graphical.target.wants"
sudo ln -sf /lib/systemd/system/sddm.service "$ROOTFS/etc/systemd/system/display-manager.service"
sudo ln -sf /lib/systemd/system/graphical.target "$ROOTFS/etc/systemd/system/default.target"
sudo install -d -m 0755 "$ROOTFS/etc/sddm.conf.d"
sudo install -d -m 0755 "$ROOTFS/usr/share/applications"
sudo tee "$ROOTFS/usr/share/applications/eos-installer.desktop" >/dev/null <<'EOF'
[Desktop Entry]
Type=Application
Name=EOS Installer
Name[es]=Instalador de EOS
Comment=Instalador gráfico basado en Calamares
Exec=pkexec calamares
Icon=system-software-install
Terminal=false
Categories=System;Settings;
EOF
sudo tee "$ROOTFS/etc/sddm.conf.d/eos-reference.conf" >/dev/null <<'EOF'
[Autologin]
User=eos
Session=plasma.desktop
Relogin=false

[X11]
DisplayServer=x11
EOF
sudo install -d -m 0755 "$ROOTFS/etc/systemd/system/getty@tty1.service.d"
sudo tee "$ROOTFS/etc/systemd/system/getty@tty1.service.d/autologin.conf" >/dev/null <<'EOF'
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin eos --noclear %I $TERM
EOF
sudo chroot "$ROOTFS" /bin/bash -c 'echo eos-plasma-reference > /etc/hostname; printf "127.0.0.1 localhost\n127.0.1.1 eos-plasma-reference\n" > /etc/hosts; useradd -m -s /bin/bash eos || true; usermod -aG sudo,audio,video,plugdev eos; echo "eos:eos" | chpasswd; echo "root:eos" | chpasswd; echo "en_US.UTF-8 UTF-8" > /etc/locale.gen; locale-gen; ln -sf /usr/share/zoneinfo/UTC /etc/localtime; dpkg-reconfigure -f noninteractive tzdata >/dev/null 2>&1 || true; systemctl enable sddm.service || true; systemctl set-default graphical.target || true; mkdir -p /home/eos/Desktop /home/eos/Documents; chown -R eos:eos /home/eos'

truncate -s "$SIZE" "$IMAGE"
mkfs.ext4 -F -L EOS-UBUNTU-PLASMA "$IMAGE" >/dev/null
sudo mount -o loop "$IMAGE" "$MOUNT"
sudo cp -a "$ROOTFS"/. "$MOUNT"/
sudo sync
sudo umount "$MOUNT"

sha256sum "$IMAGE" > "$BUILD/eos-ubuntu-plasma-reference.img.sha256"
printf 'created %s (%s bytes)\n' "$IMAGE" "$(stat -c %s "$IMAGE")"
