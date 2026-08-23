#!/usr/bin/env python3
"""Validate an EOS .edisk development firmware against a device profile.

This tool is validation-only and never opens a block device or flashes hardware.
"""
from __future__ import annotations

import argparse
import gzip
import json
from pathlib import Path
import struct

HEADER = struct.Struct("<8sQQ")
MAGIC = b"EOSDISK\x01"


def read_edisk(path: Path) -> dict:
    with path.open("rb") as handle:
        magic, metadata_len, payload_len = HEADER.unpack(handle.read(HEADER.size))
        if magic != MAGIC:
            raise ValueError("not an EOS .edisk v1 development image")
        if metadata_len > 1024 * 1024 or payload_len > 8 * 1024 * 1024 * 1024:
            raise ValueError("unsafe .edisk size")
        manifest = json.loads(handle.read(metadata_len).decode("utf-8"))
        if not isinstance(manifest, dict):
            raise ValueError("invalid .edisk manifest")
        return manifest


def main() -> int:
    parser = argparse.ArgumentParser(prog="eos-device", description="Validate an EOS .edisk firmware image")
    parser.add_argument("edisk", type=Path)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--architecture", required=True)
    parser.add_argument("--bootloader", default="eos-boot-0.1")
    args = parser.parse_args()
    try:
        manifest = read_edisk(args.edisk)
        checks = {
            "profile": manifest.get("profile") == args.profile,
            "architecture": manifest.get("architecture") == args.architecture,
            "bootloader": manifest.get("bootloader") == args.bootloader,
            "format": manifest.get("format") == "edisk",
        }
        if not all(checks.values()):
            raise ValueError(f"device profile mismatch: {checks}")
        print(json.dumps({"compatible": True, "checks": checks, "flashed": False, "manifest": manifest}, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, TypeError, json.JSONDecodeError, struct.error) as exc:
        print(f"eos-device error: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
