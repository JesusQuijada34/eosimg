#!/usr/bin/env python3
"""Verify the populated development GPT image of EOS without mounting it."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess


def run(*command: str) -> str:
    return subprocess.run(command, check=True, text=True, capture_output=True).stdout + subprocess.run(command, check=True, text=True, capture_output=True).stderr


def sector_start(image: Path, partition: str) -> int:
    output = subprocess.run(["sgdisk", "-i", partition, str(image)], check=True, text=True, capture_output=True).stdout
    match = re.search(r"^First sector: *(\d+)", output, re.MULTILINE)
    if not match:
        raise ValueError(f"could not read start sector for partition {partition}")
    return int(match.group(1))


def main() -> int:
    parser = argparse.ArgumentParser(prog="eos-img-verify", description="Verify an EOS GPT development image")
    parser.add_argument("image", type=Path)
    args = parser.parse_args()
    if not args.image.is_file():
        raise SystemExit("eos-img-verify error: image does not exist")
    try:
        verify = subprocess.run(["sgdisk", "--verify", str(args.image)], check=True, text=True, capture_output=True).stdout
        esp = sector_start(args.image, "1")
        system = sector_start(args.image, "2")
        offset = str(esp * 512)
        boot_listing = run("mdir", "-i", f"{args.image}@@{offset}", "::/EFI/BOOT")
        eos_listing = run("mdir", "-i", f"{args.image}@@{offset}", "::/EFI/EOS")
        checks = {
            "gpt": "No problems found" in verify,
            "esp": "BOOTX64" in boot_listing,
            "kernel": "EOS-LINUX" in eos_listing.upper(),
            "initramfs": "EOS-INITRAMFS" in eos_listing.upper(),
            "system_partition_present": system > esp,
        }
        if not all(checks.values()):
            raise ValueError(f"image verification failed: {checks}")
        print(json.dumps({"image": str(args.image), "checks": checks, "mounts_performed": False, "writes_performed": False}, ensure_ascii=False, indent=2))
        return 0
    except (OSError, subprocess.CalledProcessError, ValueError) as exc:
        print(f"eos-img-verify error: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
