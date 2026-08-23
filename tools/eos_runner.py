#!/usr/bin/env python3
"""EOS runner prototype.

The runner is not part of the EOS kernel. It starts an EOS Linux image on a
host that cannot boot EOS directly. It only runs an explicitly supplied kernel
and initramfs; it never downloads or executes untrusted images automatically.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path


def build_command(args: argparse.Namespace) -> list[str]:
    if args.arch == "x86_64":
        qemu = shutil.which("qemu-system-x86_64") or "qemu-system-x86_64"
        machine = "q35"
        cpu = "max"
    else:
        qemu = shutil.which("qemu-system-aarch64") or "qemu-system-aarch64"
        machine = "virt"
        cpu = "cortex-a72"
    return [
        qemu,
        "-machine", machine,
        "-cpu", cpu,
        "-m", args.memory,
        "-nographic" if args.headless else "-display", "none" if args.headless else "gtk",
        "-kernel", str(args.kernel),
        "-initrd", str(args.initramfs),
        "-append", "console=ttyS0 rdinit=/init",
    ]


def main() -> int:
    parser = argparse.ArgumentParser(prog="eos-runner", description="Run an EOS image in a host VM")
    parser.add_argument("--kernel", type=Path, required=True)
    parser.add_argument("--initramfs", type=Path, required=True)
    parser.add_argument("--arch", choices=("x86_64", "aarch64"), default="x86_64")
    parser.add_argument("--memory", default="1024M")
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if not args.kernel.is_file() or not args.initramfs.is_file():
        raise SystemExit("eos-runner error: kernel and initramfs must be explicit existing files")
    command = build_command(args)
    print(" ".join(command))
    if args.dry_run:
        return 0
    return subprocess.run(command, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
