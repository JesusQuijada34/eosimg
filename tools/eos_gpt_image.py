#!/usr/bin/env python3
"""Create a local GPT layout for an EOS PC image.

The image is deliberately a development artifact: it has a real GPT layout,
but the ESP and system partitions are not populated with a production
bootloader yet. The script only writes the output image path supplied by the
caller, never a host block device.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess

PARTITIONS = [
    (1, 2048, "+32M", "EF00", "EOS-BOOT"),
    (2, 0, "+64M", "8300", "EOS-SYSTEM"),
    (3, 0, "+32M", "8300", "EOS-RECOVERY"),
    (4, 0, "+64M", "8300", "EOS-DATA"),
    (5, 0, "+32M", "8300", "EOS-CACHE"),
]


def main() -> int:
    parser = argparse.ArgumentParser(prog="eos-gpt-image", description="Create a development GPT image for EOS")
    parser.add_argument("output", type=Path)
    parser.add_argument("--size", default="256M")
    parser.add_argument("--profile", default="eos-pc-reference")
    parser.add_argument("--version", default="0.1.0")
    parser.add_argument("--architecture", default="x86_64")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    if shutil.which("qemu-img") is None or shutil.which("sgdisk") is None:
        raise SystemExit("eos-gpt-image error: qemu-img and sgdisk are required")
    if args.output.exists() and not args.force:
        raise SystemExit(f"eos-gpt-image error: refusing to overwrite {args.output}; use --force")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["qemu-img", "create", "-f", "raw", str(args.output), args.size], check=True, stdout=subprocess.DEVNULL)
    commands = ["sgdisk", "--zap-all", "--clear"]
    for number, start, size, typecode, name in PARTITIONS:
        start_arg = str(start) if start else "0"
        commands.extend([f"--new={number}:{start_arg}:{size}", f"--typecode={number}:{typecode}", f"--change-name={number}:{name}"])
    commands.append(str(args.output))
    subprocess.run(commands, check=True, stdout=subprocess.DEVNULL)
    manifest = {
        "format": "img",
        "format_version": 2,
        "profile": args.profile,
        "version": args.version,
        "architecture": args.architecture,
        "partition_table": "GPT",
        "partitions": [{"number": n, "name": name, "type": t} for n, _, _, t, name in PARTITIONS],
        "status": "development-gpt-layout-not-bootable-until-populated",
    }
    sidecar = args.output.with_suffix(args.output.suffix + ".json")
    sidecar.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"image": str(args.output), "manifest": str(sidecar), **manifest}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
