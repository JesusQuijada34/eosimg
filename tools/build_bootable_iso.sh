#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
STAGE="$ROOT/build/iso-stage"
OUT="${1:-$ROOT/build/eos-dev.iso}"
KERNEL="${EOS_KERNEL:-$ROOT/build/vmlinuz-eos-dev}"
if [[ ! -f "$KERNEL" && -f /boot/vmlinuz-6.8.0-138-generic ]]; then
    KERNEL=/boot/vmlinuz-6.8.0-138-generic
fi
INITRAMFS="$ROOT/build/eos-initramfs.img"

for tool in grub-mkrescue xorriso; do
    command -v "$tool" >/dev/null || { echo "missing required tool: $tool" >&2; exit 2; }
done
[[ -f "$KERNEL" ]] || { echo "kernel not found: $KERNEL" >&2; exit 2; }
"$ROOT/tools/build_initramfs.sh" >/dev/null
rm -rf "$STAGE"
mkdir -p "$STAGE/boot/grub"
cp "$KERNEL" "$STAGE/boot/eos-linux"
cp "$INITRAMFS" "$STAGE/boot/eos-initramfs.img"
cat > "$STAGE/boot/grub/grub.cfg" <<'EOF'
set timeout=3
set default=0

menuentry 'Etternhall Operating System (development)' {
    linux /boot/eos-linux console=ttyS0 rdinit=/init eos.mode=normal
    initrd /boot/eos-initramfs.img
}

menuentry 'Etternhall Operating System (recovery)' {
    linux /boot/eos-linux console=ttyS0 rdinit=/init eos.mode=recovery
    initrd /boot/eos-initramfs.img
}
EOF
mkdir -p "$(dirname "$OUT")"
grub-mkrescue -o "$OUT" "$STAGE" >/tmp/eos-grub-mkrescue.log 2>&1
printf 'created %s (%s bytes)\n' "$OUT" "$(stat -c %s "$OUT")"
