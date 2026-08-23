#!/usr/bin/env python3
"""EOS firmware/image container prototype for .edisk and .img.

This is a development container, not yet a raw GPT disk writer. It keeps the
format explicit so a future writer can map the same manifest to real partitions.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from pathlib import Path
import struct
import tarfile
import io

MAGIC = {"edisk": b"EOSDISK\x01", "img": b"EOSIMG\x01\x00"}
HEADER = struct.Struct("<8sQQ")


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def make_payload(directory: Path) -> bytes:
    stream = io.BytesIO()
    with tarfile.open(fileobj=stream, mode="w:gz", compresslevel=9) as archive:
        for item in sorted(directory.rglob("*")):
            relative = item.relative_to(directory)
            info = archive.gettarinfo(str(item), arcname=str(relative))
            if info.isreg():
                with item.open("rb") as handle:
                    archive.addfile(info, handle)
            else:
                archive.addfile(info)
    return stream.getvalue()


def main() -> int:
    parser = argparse.ArgumentParser(prog="eos-image", description="Build a development EOS .edisk or .img container")
    parser.add_argument("kind", choices=("edisk", "img"))
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--architecture", default="x86_64")
    parser.add_argument("--bootloader", default="eos-boot-0.1")
    args = parser.parse_args()
    if not args.source.is_dir():
        raise SystemExit("eos-image error: source must be a directory")
    payload = make_payload(args.source)
    manifest = {
        "format": args.kind,
        "format_version": 1,
        "profile": args.profile,
        "version": args.version,
        "architecture": args.architecture,
        "bootloader": args.bootloader,
        "compression": "gzip+tar",
        "payload_sha256": hashlib.sha256(payload).hexdigest(),
        "partitions": ["boot", "system", "vendor", "recovery", "data", "cache"] if args.kind == "edisk" else ["efi", "system", "recovery", "data", "cache"],
        "status": "development-container-not-raw-disk",
    }
    metadata = (json.dumps(manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("wb") as handle:
        handle.write(HEADER.pack(MAGIC[args.kind], len(metadata), len(payload)))
        handle.write(metadata)
        handle.write(payload)
    print(json.dumps({"output": str(args.output), "manifest": manifest}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
