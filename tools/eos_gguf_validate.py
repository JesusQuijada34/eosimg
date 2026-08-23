#!/usr/bin/env python3
"""Preflight validation for local GGUF models before llama.cpp execution."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import struct

MAGIC = b"GGUF"
MAX_VERSION = 3


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(prog="eos-gguf-validate")
    parser.add_argument("model", type=Path)
    parser.add_argument("--sha256", required=True)
    parser.add_argument("--max-size-gib", type=float, default=32.0)
    args = parser.parse_args()
    try:
        if args.model.is_symlink() or not args.model.is_file():
            raise ValueError("model must be a regular local file")
        size = args.model.stat().st_size
        if size <= 24 or size > args.max_size_gib * 1024**3:
            raise ValueError("model size outside EOS safety range")
        with args.model.open("rb") as stream:
            header = stream.read(24)
        if header[:4] != MAGIC:
            raise ValueError("invalid GGUF magic")
        version = struct.unpack_from("<I", header, 4)[0]
        if version < 1 or version > MAX_VERSION:
            raise ValueError(f"unsupported GGUF version: {version}")
        actual = sha256(args.model)
        if actual.lower() != args.sha256.lower():
            raise ValueError("sha256 mismatch")
        result = {"format": "GGUF", "version": version, "size": size, "sha256": actual, "execution": "eligible-for-llama.cpp"}
        print(json.dumps(result, indent=2))
        return 0
    except (OSError, ValueError, struct.error) as exc:
        print(f"eos-gguf-validate error: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
