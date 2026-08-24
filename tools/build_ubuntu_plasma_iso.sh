#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BUILD="$ROOT/build"
ROOTFS="$BUILD/ubuntu-plasma-rootfs"
STAGE="$BUILD/ubuntu-plasma-iso-stage"
OUT="${1:-$BUILD/eos-ubuntu-plasma-calamares.iso}"
KERNEL="${EOS_KERNEL:-$BUILD/vmlinuz-eos-dev}"
INIT="$BUILD/ubuntu-plasma-live-initramfs.img"

command -v grub-mkrescue >/dev/null || { echo 'missing grub-mkrescue' >&2; exit 2; }
command -v xorriso >/dev/null || { echo 'missing xorriso' >&2; exit 2; }
command -v mksquashfs >/dev/null || { echo 'missing mksquashfs' >&2; exit 2; }
command -v cpio >/dev/null || { echo 'missing cpio' >&2; exit 2; }
[[ -f "$KERNEL" ]] || { echo "kernel not found: $KERNEL" >&2; exit 2; }
[[ -x "$ROOTFS/usr/bin/calamares" ]] || { echo 'Calamares is absent from the rootfs; run build_ubuntu_plasma_reference.sh first' >&2; exit 2; }
[[ -x "$ROOTFS/usr/bin/startplasma-x11" || -x "$ROOTFS/usr/bin/startplasma-wayland" ]] || { echo 'Plasma session is absent from the rootfs' >&2; exit 2; }

rm -rf "$STAGE"
mkdir -p "$STAGE/boot/grub" "$STAGE/live" "$BUILD/ubuntu-plasma-live-init"
rm -rf "$BUILD/ubuntu-plasma-live-init"/*
mkdir -p "$BUILD/ubuntu-plasma-live-init"/{bin,dev,proc,sys,newroot,cdrom}
cp "$(command -v busybox)" "$BUILD/ubuntu-plasma-live-init/bin/busybox"
for app in sh mount umount mkdir sleep switch_root cat insmod; do ln -sf busybox "$BUILD/ubuntu-plasma-live-init/bin/$app"; done
KERNEL_RELEASE="$(file "$KERNEL" | sed -n 's/.*version \([^ ]*\).*/\1/p')"
ISO9660_MODULE="/lib/modules/$KERNEL_RELEASE/kernel/fs/isofs/isofs.ko.zst"
if [[ -f "$ISO9660_MODULE" ]] && command -v unzstd >/dev/null; then
    mkdir -p "$BUILD/ubuntu-plasma-live-init/lib/modules/$KERNEL_RELEASE/kernel/fs/isofs"
    unzstd -c "$ISO9660_MODULE" > "$BUILD/ubuntu-plasma-live-init/lib/modules/$KERNEL_RELEASE/kernel/fs/isofs/isofs.ko"
fi
cat > "$BUILD/ubuntu-plasma-live-init/init" <<'EOF'
#!/bin/sh
mount -t proc proc /proc 2>/dev/null || true
mount -t sysfs sysfs /sys 2>/dev/null || true
mount -t devtmpfs devtmpfs /dev 2>/dev/null || true
for module in /lib/modules/*/kernel/fs/isofs/isofs.ko; do [ -f "$module" ] && insmod "$module" 2>/dev/null || true; done
mkdir -p /cdrom /newroot
for device in /dev/sr0 /dev/cdrom; do
    if mount -t iso9660 "$device" /cdrom 2>/dev/null; then break; fi
done
until [ -f /cdrom/live/filesystem.squashfs ]; do sleep 1; done
mount -t squashfs -o ro /cdrom/live/filesystem.squashfs /newroot
mkdir -p /newroot/run /newroot/tmp
exec switch_root /newroot /sbin/init systemd.unit=graphical.target
EOF
chmod +x "$BUILD/ubuntu-plasma-live-init/init"
(cd "$BUILD/ubuntu-plasma-live-init" && find . -print0 | sort -z | cpio --null -o -H newc 2>/dev/null | gzip -n -9 > "$INIT")
mksquashfs "$ROOTFS" "$STAGE/live/filesystem.squashfs" -comp zstd -noappend -quiet
cp "$KERNEL" "$STAGE/boot/eos-linux"
cp "$INIT" "$STAGE/boot/ubuntu-plasma-live-initramfs.img"
cat > "$STAGE/boot/grub/grub.cfg" <<'EOF'
set timeout=5
set default=0
menuentry 'Ubuntu Plasma Reference (KDE Plasma + Calamares)' {
    linux /boot/eos-linux console=ttyS0 rdinit=/init boot=live systemd.unit=graphical.target
    initrd /boot/ubuntu-plasma-live-initramfs.img
}
menuentry 'Ubuntu Plasma Reference (recovery console)' {
    linux /boot/eos-linux console=ttyS0 rdinit=/init boot=live systemd.unit=multi-user.target
    initrd /boot/ubuntu-plasma-live-initramfs.img
}
EOF
mkdir -p "$(dirname "$OUT")"
grub-mkrescue -o "$OUT" "$STAGE" >/tmp/eos-ubuntu-plasma-grub-mkrescue.log 2>&1
sha256sum "$OUT" > "$OUT.sha256"
printf 'created %s (%s bytes)\n' "$OUT" "$(stat -c %s "$OUT")"
