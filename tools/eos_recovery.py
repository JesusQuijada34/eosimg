#!/usr/bin/env python3
"""EOS recovery operations for a specified data root.

This prototype never touches the host root by default. Destructive operations
require an explicit --root and --confirm phrase.
"""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

CONFIRM = "ERASE EOS DATA"


def require_confirmation(args: argparse.Namespace) -> Path:
    if not args.root:
        raise ValueError("--root is required")
    if args.confirm != CONFIRM:
        raise ValueError(f"destructive action requires --confirm '{CONFIRM}'")
    root = Path(args.root).expanduser().resolve()
    if root == Path("/") or len(root.parts) < 4:
        raise ValueError("refusing unsafe recovery root")
    return root


def wipe_cache(root: Path) -> None:
    cache = root / "cache"
    if cache.exists():
        for item in cache.iterdir():
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()
    cache.mkdir(parents=True, exist_ok=True)


def wipe_data(root: Path) -> None:
    data = root / "data"
    if data.exists():
        shutil.rmtree(data)
    data.mkdir(parents=True, exist_ok=True)


def factory_reset(root: Path) -> None:
    wipe_data(root)
    wipe_cache(root)
    for name in ("registry.json", "settings.json"):
        path = root / name
        if path.exists():
            path.unlink()


def main() -> int:
    parser = argparse.ArgumentParser(prog="eos-recovery", description="EOS recovery operations")
    parser.add_argument("action", choices=("wipe-cache", "wipe-data", "factory-reset"))
    parser.add_argument("--root", required=True)
    parser.add_argument("--confirm", default="")
    args = parser.parse_args()
    try:
        root = require_confirmation(args)
        root.mkdir(parents=True, exist_ok=True)
        if args.action == "wipe-cache":
            wipe_cache(root)
        elif args.action == "wipe-data":
            wipe_data(root)
        else:
            factory_reset(root)
        print(f"recovery complete: {args.action} ({root})")
        return 0
    except (OSError, ValueError) as exc:
        raise SystemExit(f"eos-recovery error: {exc}")


if __name__ == "__main__":
    raise SystemExit(main())
