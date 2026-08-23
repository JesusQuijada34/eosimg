#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
IMAGE="${1:-$ROOT/build/eos-pc-gpt.img}"
KERNEL="${EOS_KERNEL:-$ROOT/build/vmlinuz-eos-dev}"
INITRAMFS="$ROOT/build/eos-initramfs.img"
WORK="$ROOT/build/esp-work"
ESP="$WORK/esp.fat"
SYSTEM="$WORK/system.ext4"
CFG="$WORK/grub.cfg"
EFI="$WORK/BOOTX64.EFI"

[[ -f "$IMAGE" && -f "$KERNEL" && -f "$INITRAMFS" ]] || { echo "usage: populate_gpt_image.sh IMAGE with kernel/initramfs present" >&2; exit 2; }
for tool in sgdisk mkfs.fat mmd mcopy mkfs.ext4 debugfs grub-mkstandalone; do
    command -v "$tool" >/dev/null || { echo "missing required tool: $tool" >&2; exit 2; }
done
rm -rf "$WORK"
mkdir -p "$WORK/EFI/BOOT" "$WORK/EFI/EOS" "$WORK/boot/grub"
cat > "$CFG" <<'EOF'
set timeout=0
set default=0
insmod part_gpt
insmod fat
set root=(hd0,gpt1)
menuentry 'Etternhall Operating System (development)' {
    linux /EFI/EOS/eos-linux console=ttyS0 rdinit=/init eos.mode=normal
    initrd /EFI/EOS/eos-initramfs.img
}
menuentry 'Etternhall Operating System (recovery)' {
    linux /EFI/EOS/eos-linux console=ttyS0 rdinit=/init eos.mode=recovery
    initrd /EFI/EOS/eos-initramfs.img
}
EOF
grub-mkstandalone -O x86_64-efi -o "$EFI" "boot/grub/grub.cfg=$CFG" >/tmp/eos-grub-standalone.log 2>&1
truncate -s 64M "$ESP"
mkfs.fat -F32 -n EOSBOOT "$ESP" >/dev/null
mmd -i "$ESP" ::/EFI ::/EFI/BOOT ::/EFI/EOS
mcopy -i "$ESP" "$EFI" ::/EFI/BOOT/BOOTX64.EFI
mcopy -i "$ESP" "$KERNEL" ::/EFI/EOS/eos-linux
mcopy -i "$ESP" "$INITRAMFS" ::/EFI/EOS/eos-initramfs.img
sector=$(sgdisk -i 1 "$IMAGE" | sed -n 's/^First sector: *\([0-9][0-9]*\).*/\1/p')
[[ "$sector" =~ ^[0-9]+$ ]] || { echo "could not determine EOS-BOOT start sector" >&2; exit 3; }
dd if="$ESP" of="$IMAGE" bs=512 seek="$sector" conv=notrunc status=none

cat > "$WORK/eos-release" <<'EOF'
NAME="Etternhall Operating System"
ID=etternhall
VERSION_ID="0.1"
BASE_KERNEL="Linux"
USERLAND="EOS"
LINUX_USER_ABI="unsupported"
EOF
truncate -s 64M "$SYSTEM"
mkfs.ext4 -F -L EOSSYSTEM "$SYSTEM" >/dev/null
mkdir -p "$WORK/system-files"
printf '%s\n' 'EOS development system partition' > "$WORK/system-files/README"
debugfs -w -R 'mkdir /etc' "$SYSTEM" >/dev/null 2>&1
debugfs -w -R 'mkdir /usr' "$SYSTEM" >/dev/null 2>&1
debugfs -w -R 'mkdir /usr/share' "$SYSTEM" >/dev/null 2>&1
debugfs -w -R 'mkdir /usr/share/eos' "$SYSTEM" >/dev/null 2>&1
debugfs -w -R "write $WORK/eos-release /etc/eos-release" "$SYSTEM" >/dev/null 2>&1
debugfs -w -R "write $WORK/system-files/README /usr/share/eos/README" "$SYSTEM" >/dev/null 2>&1
system_sector=$(sgdisk -i 2 "$IMAGE" | sed -n 's/^First sector: *\([0-9][0-9]*\).*/\1/p')
[[ "$system_sector" =~ ^[0-9]+$ ]] || { echo "could not determine EOS-SYSTEM start sector" >&2; exit 3; }
dd if="$SYSTEM" of="$IMAGE" bs=512 seek="$system_sector" conv=notrunc status=none
printf 'populated UEFI ESP in %s at sector %s\n' "$IMAGE" "$sector"
printf 'populated EOS-SYSTEM ext4 in %s at sector %s\n' "$IMAGE" "$system_sector"
