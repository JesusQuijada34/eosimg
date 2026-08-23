#!/usr/bin/env python3
"""EOS PC/device boot planner.

The current implementation validates development image containers and emits a
boot/install plan. It never writes a block device; a future installer will add
an explicit confirmation gate and platform-specific raw image writer.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import struct

MAGIC = {b"EOSDISK\x01": "edisk", b"EOSIMG\x01\x00": "img"}
HEADER = struct.Struct("<8sQQ")


def inspect_image(path: Path) -> tuple[str, dict]:
    with path.open("rb") as handle:
        raw_header = handle.read(HEADER.size)
        if len(raw_header) != HEADER.size:
            raise ValueError("truncated EOS image")
        magic, metadata_len, payload_len = HEADER.unpack(raw_header)
        if magic not in MAGIC:
            raise ValueError("unsupported EOS image magic")
        if metadata_len > 1024 * 1024 or payload_len > 8 * 1024 * 1024 * 1024:
            raise ValueError("unsafe image size")
        metadata = json.loads(handle.read(metadata_len).decode("utf-8"))
        if not isinstance(metadata, dict):
            raise ValueError("invalid EOS image manifest")
        return MAGIC[magic], {**metadata, "payload_bytes": payload_len}


def main() -> int:
    parser = argparse.ArgumentParser(prog="eos-boot", description="Inspect and plan EOS boot/install")
    sub = parser.add_subparsers(dest="command", required=True)
    inspect = sub.add_parser("inspect")
    inspect.add_argument("image", type=Path)
    plan = sub.add_parser("plan")
    plan.add_argument("image", type=Path)
    plan.add_argument("--target", default="pc")
    plan.add_argument("--disk", default=None)
    plan.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    try:
        kind, manifest = inspect_image(args.image)
        if args.command == "inspect":
            print(json.dumps({"kind": kind, "manifest": manifest}, ensure_ascii=False, indent=2))
            return 0
        if kind == "img" and args.target != "pc":
            raise ValueError(".img requires --target pc")
        if kind == "edisk" and args.target == "pc":
            raise ValueError(".edisk requires a device target")
        destination = args.disk or "<select-disk-before-install>"
        print(json.dumps({
            "action": "boot/install-plan",
            "image": str(args.image),
            "kind": kind,
            "target": args.target,
            "destination": destination,
            "writes_performed": False,
            "next": "verify signature, confirm destination, then invoke platform writer",
        }, ensure_ascii=False, indent=2))
        return 0
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, struct.error, ValueError) as exc:
        raise SystemExit(f"eos-boot error: {exc}")


if __name__ == "__main__":
    raise SystemExit(main())
