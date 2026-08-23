#!/usr/bin/env python3
"""Create a local manifest for the compiled EOS userland payload."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(prog="eos-userland-manifest")
    parser.add_argument("build_dir", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    targets = []
    for path in sorted(args.build_dir.glob("eos-*")):
        if path.is_file() and path.stat().st_mode & 0o111:
            targets.append({"name": path.name, "sha256": sha256(path), "bytes": path.stat().st_size})
    manifest = {
        "schema": "eos-userland-manifest-0.1",
        "kind": "development-image-payload",
        "application_policy": "signed .eapp only; user ELF is not an application format",
        "targets": targets,
        "source_only_repository": True,
        "generated_artifacts": "local-only",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "target_count": len(targets), "status": "valid"}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
