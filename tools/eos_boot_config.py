#!/usr/bin/env python3
"""Generate a reviewable EOS boot configuration.

The generated file is data only. Installing it into an EFI System Partition
will require a future, explicit installer action.
"""
from __future__ import annotations

import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(prog="eos-boot-config", description="Generate EOS bootloader configuration")
    parser.add_argument("--kernel", type=Path, required=True)
    parser.add_argument("--initramfs", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--title", default="Etternhall Operating System")
    parser.add_argument("--console", default="ttyS0")
    args = parser.parse_args()
    if not args.kernel.is_file() or not args.initramfs.is_file():
        raise SystemExit("eos-boot-config error: kernel and initramfs must exist")
    config = f"""# Generated EOS boot configuration; review before installation.
set timeout=3
set default=0

menuentry '{args.title}' {{
    linux /EFI/EOS/{args.kernel.name} console={args.console} rdinit=/init eos.mode=normal
    initrd /EFI/EOS/{args.initramfs.name}
}}

menuentry '{args.title} Recovery' {{
    linux /EFI/EOS/{args.kernel.name} console={args.console} rdinit=/init eos.mode=recovery
    initrd /EFI/EOS/{args.initramfs.name}
}}
"""
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(config, encoding="utf-8")
    print(f"generated {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
