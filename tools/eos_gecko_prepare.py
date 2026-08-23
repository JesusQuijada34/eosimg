#!/usr/bin/env python3
"""Prepare a reproducible Gecko build manifest without downloading sources."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess

MIN_RAM_GIB = 4.0
RECOMMENDED_RAM_GIB = 8.0
MIN_DISK_GIB = 30.0


def available_ram_gib() -> float:
    values = {}
    for line in Path("/proc/meminfo").read_text(encoding="utf-8").splitlines():
        key, value = line.split(":", 1)
        values[key] = int(value.split()[0])
    return values.get("MemTotal", 0) / 1024 / 1024


def main() -> int:
    parser = argparse.ArgumentParser(prog="eos-gecko-prepare")
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--revision", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--allow-low-resources", action="store_true")
    args = parser.parse_args()
    try:
        ram = available_ram_gib()
        disk = shutil.disk_usage(args.source if args.source.exists() else args.source.parent)
        free_gib = disk.free / 1024**3
        if not args.allow_low_resources and (ram < MIN_RAM_GIB or free_gib < MIN_DISK_GIB):
            raise ValueError(f"insufficient build resources: RAM={ram:.2f} GiB free_disk={free_gib:.2f} GiB")
        if not args.source.is_dir() or not (args.source / "mach").is_file() or not (args.source / ".git").exists():
            raise ValueError("source must be an explicit mozilla-central checkout containing mach and .git")
        actual = subprocess.run(["git", "-C", str(args.source), "rev-parse", "HEAD"], text=True, capture_output=True, check=False)
        if actual.returncode != 0:
            raise ValueError("cannot read Gecko source revision")
        actual_revision = actual.stdout.strip()
        if actual_revision != args.revision:
            raise ValueError(f"revision mismatch: expected {args.revision}, got {actual_revision}")
        result = {
            "schema": "eos-gecko-build-0.1",
            "source": str(args.source.resolve()),
            "revision": actual_revision,
            "ram_gib": round(ram, 2),
            "free_disk_gib": round(free_gib, 2),
            "recommended_ram_gib": RECOMMENDED_RAM_GIB,
            "engine": "Gecko",
            "frontend": "EOS Qt6; not Firefox XUL",
            "network": "managed-by-eos-browserd",
            "status": "ready-to-configure",
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        temp = args.output.with_suffix(args.output.suffix + ".tmp")
        temp.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        temp.replace(args.output)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(f"eos-gecko-prepare error: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
