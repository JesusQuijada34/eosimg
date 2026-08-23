#!/usr/bin/env python3
"""Local ePhoto/Carrousel media index; no upload or AI execution."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".mp4", ".mov", ".webm"}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(prog="eos-photo-index")
    parser.add_argument("root", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        if not args.root.is_dir():
            raise ValueError("media root must be a directory")
        items = []
        for path in sorted(args.root.rglob("*")):
            if path.is_symlink():
                raise ValueError(f"symlink is not allowed: {path}")
            if path.is_file() and path.suffix.lower() in EXTENSIONS:
                relative = path.relative_to(args.root)
                items.append({
                    "path": str(relative),
                    "kind": "video" if path.suffix.lower() in {".mp4", ".mov", ".webm"} else "image",
                    "size": path.stat().st_size,
                    "sha256": digest(path),
                    "ai_labels": [],
                    "ai_status": "not-run",
                })
        result = {"schema": "eos-photo-index-0.1", "root": str(args.root), "upload": "disabled", "items": items}
        args.output.parent.mkdir(parents=True, exist_ok=True)
        temp = args.output.with_suffix(args.output.suffix + ".tmp")
        temp.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        temp.replace(args.output)
        print(json.dumps({"items": len(items), "output": str(args.output), "upload": "disabled"}, indent=2))
        return 0
    except (OSError, ValueError) as exc:
        print(f"eos-photo-index error: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
