#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ROOTFS="$ROOT/build/rootfs"
OUT="$ROOT/build/eos-initramfs.img"

rm -rf "$ROOTFS"
mkdir -p "$ROOTFS"/{bin,etc,proc,sys,dev,tmp,var/log,var/lib/eos,eos-system/{bin,etc,docs}}

# Record the exact compiled targets staged by the development build. The
# manifest is generated locally and is never committed as a release artifact.
python3 "$ROOT/tools/eos_userland_manifest.py" "$ROOT/build/cmake" "$ROOT/build/eos-userland-manifest.json" >/dev/null

# Init and first-boot provisioning are static so the development image does not
# depend on host libraries. Applications remain signed .eapp payloads and are
# not converted into Linux user ELF programs.
g++ -std=c++20 -O2 -static "$ROOT/src/eos-init/main.cpp" -o "$ROOTFS/eos-init"
cp "$(command -v busybox)" "$ROOTFS/bin/busybox"
for app in sh mount echo cat ls uname sleep mkdir test grep reboot; do
    ln -sf busybox "$ROOTFS/bin/$app"
done

cp "$ROOT/config/eos-services.json" "$ROOTFS/eos-system/etc/eos-services.json"
cp "$ROOT/sdk/eos-sdk.json" "$ROOTFS/eos-system/etc/eos-sdk.json"
cp "$ROOT/build/eos-userland-manifest.json" "$ROOTFS/eos-system/etc/eos-userland-manifest.json"
cp "$ROOT/docs/PLATFORM_ARCHITECTURE.md" "$ROOTFS/eos-system/docs/PLATFORM_ARCHITECTURE.md"
cp "$ROOT/docs/ETTERNHALL_DESKTOP_ARCHITECTURE.md" "$ROOTFS/eos-system/docs/ETTERNHALL_DESKTOP_ARCHITECTURE.md"

cat > "$ROOTFS/eos-firstboot" <<'EOF'
#!/bin/sh
set -eu
ROOT="${1:-/var/lib/eos}"
REBOOT="${2:-0}"
/eos-init --first-boot-root "$ROOT"
if [ "$REBOOT" = "1" ] && [ -f "$ROOT/firstboot.done" ]; then
    echo "[eos-firstboot] restart requested"
    /bin/reboot -f || true
fi
EOF
chmod +x "$ROOTFS/eos-firstboot"

cat > "$ROOTFS/etc/eos-release" <<'EOF'
NAME="Etternhall Operating System"
ID=etternhall
VERSION_ID="0.2-dev"
PRETTY_NAME="Etternhall Operating System 0.2 development"
BASE_KERNEL="Linux"
USERLAND="EOS"
APP_FORMAT="signed .eapp / EOSBC"
EOF

cat > "$ROOTFS/init" <<'EOF'
#!/bin/sh
mount -t proc proc /proc 2>/dev/null || true
mount -t sysfs sysfs /sys 2>/dev/null || true
mount -t devtmpfs devtmpfs /dev 2>/dev/null || true
mkdir -p /eos-data /var/lib/eos
# If a persistent EOS-DATA partition is attached in QEMU, use it for the
# first-boot marker. Otherwise remain in safe volatile development mode.
mount -t ext4 /dev/vda4 /eos-data 2>/dev/null || mount -t ext4 /dev/sda4 /eos-data 2>/dev/null || true
DATA_ROOT=/var/lib/eos
if [ -f /eos-data/.eos-data ]; then DATA_ROOT=/eos-data/var/lib/eos; fi

echo "[eos-initramfs] Etternhall Operating System 0.2-dev"
echo "[eos-initramfs] Linux kernel handoff complete; EOS userland staged"
/eos-init --dry-run
FIRSTBOOT=0
REBOOT=0
for arg in $(cat /proc/cmdline 2>/dev/null || true); do
    case "$arg" in
        eos.firstboot=1) FIRSTBOOT=1 ;;
        eos.reboot=1) REBOOT=1 ;;
    esac
done
if [ "$FIRSTBOOT" = "1" ]; then
    /eos-firstboot "$DATA_ROOT" "$REBOOT"
fi
exec /bin/sh
EOF
chmod +x "$ROOTFS/init"

(cd "$ROOTFS" && find . -print0 | sort -z | cpio --null -o -H newc 2>/dev/null | gzip -n -9 > "$OUT")
printf 'created %s (%s bytes)\n' "$OUT" "$(stat -c %s "$OUT")"
