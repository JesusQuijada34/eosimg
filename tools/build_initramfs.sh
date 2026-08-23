#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ROOTFS="$ROOT/build/rootfs"
OUT="$ROOT/build/eos-initramfs.img"

rm -rf "$ROOTFS"
mkdir -p "$ROOTFS"/{bin,etc,proc,sys,dev,tmp,var/log}

# Build a self-contained init service so the initramfs does not depend on host libraries.
g++ -std=c++20 -O2 -static "$ROOT/src/eos-init/main.cpp" -o "$ROOTFS/eos-init"
cp "$(command -v busybox)" "$ROOTFS/bin/busybox"
for app in sh mount echo cat ls uname sleep; do
    ln -s busybox "$ROOTFS/bin/$app"
done

cat > "$ROOTFS/etc/eos-release" <<'EOF'
NAME="Etternhall Operating System"
ID=etternhall
VERSION_ID="0.1"
PRETTY_NAME="Etternhall Operating System 0.1"
BASE_KERNEL="Linux"
EOF

cat > "$ROOTFS/init" <<'EOF'
#!/bin/sh
mount -t proc proc /proc 2>/dev/null || true
mount -t sysfs sysfs /sys 2>/dev/null || true
mount -t devtmpfs devtmpfs /dev 2>/dev/null || true
echo "[eos-initramfs] Etternhall Operating System 0.1"
echo "[eos-initramfs] Linux kernel handoff complete"
/eos-init --dry-run
exec /bin/sh
EOF
chmod +x "$ROOTFS/init"

(cd "$ROOTFS" && find . -print0 | sort -z | cpio --null -o -H newc 2>/dev/null | gzip -n -9 > "$OUT")
printf 'created %s (%s bytes)\n' "$OUT" "$(stat -c %s "$OUT")"
