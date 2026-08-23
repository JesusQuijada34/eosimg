#!/usr/bin/env python3
"""Swimmer Time: local, explicit-root snapshots for EOS development."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import time

CONFIRM = "RESTORE SWIMMER TIME"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def files(root: Path) -> list[Path]:
    result = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"symlink is not allowed: {path}")
        if path.is_file():
            result.append(path.relative_to(root))
    return result


def snapshot(args: argparse.Namespace) -> int:
    source = args.root / "data"
    if not source.is_dir():
        raise ValueError(f"source data directory missing: {source}")
    stamp = time.strftime("%Y%m%d-%H%M%S", time.gmtime())
    destination = args.root / "swimmer-time" / stamp
    destination.mkdir(parents=True, exist_ok=False)
    manifest = {"schema": "swimmer-time-0.1", "created_utc": stamp, "files": {}}
    for relative in files(source):
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source / relative, target)
        manifest["files"][str(relative)] = {"sha256": digest(target), "size": target.stat().st_size}
    (destination / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"snapshot": stamp, "path": str(destination), "file_count": len(manifest["files"])}, indent=2))
    return 0


def restore(args: argparse.Namespace) -> int:
    if args.confirm != CONFIRM:
        raise ValueError(f"restore requires --confirm '{CONFIRM}'")
    snapshot_path = args.root / "swimmer-time" / args.snapshot
    manifest_path = snapshot_path / "manifest.json"
    if not manifest_path.is_file():
        raise ValueError("snapshot manifest missing")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    destination = args.root / "data"
    staging = args.root / ".swimmer-restore.tmp"
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True)
    for name, metadata in manifest.get("files", {}).items():
        source = snapshot_path / name
        target = staging / name
        if not source.is_file() or source.is_symlink():
            raise ValueError(f"snapshot file missing or unsafe: {name}")
        if digest(source) != metadata["sha256"] or source.stat().st_size != metadata["size"]:
            raise ValueError(f"snapshot verification failed: {name}")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    old = args.root / ".swimmer-old.tmp"
    if old.exists():
        shutil.rmtree(old)
    if destination.exists():
        destination.rename(old)
    staging.rename(destination)
    if old.exists():
        shutil.rmtree(old)
    print(json.dumps({"restored": args.snapshot, "root": str(destination)}, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="swimmer-time")
    parser.add_argument("--root", type=Path, required=True)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("snapshot")
    restore_parser = sub.add_parser("restore")
    restore_parser.add_argument("snapshot")
    restore_parser.add_argument("--confirm", required=True)
    args = parser.parse_args()
    try:
        return snapshot(args) if args.command == "snapshot" else restore(args)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"swimmer-time error: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
