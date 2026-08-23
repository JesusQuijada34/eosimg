#!/usr/bin/env python3
"""EOS SDK project generator prototype."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re

IDENTIFIER = re.compile(r"^[a-z][a-z0-9]*(?:\.[a-z0-9]+)+$")


def main() -> int:
    parser = argparse.ArgumentParser(prog="eos-sdk", description="Create a new EOS application project")
    parser.add_argument("command", choices=("new",))
    parser.add_argument("bundle_id")
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--author", default="EOS Developer")
    args = parser.parse_args()
    if not IDENTIFIER.fullmatch(args.bundle_id):
        raise SystemExit("eos-sdk error: bundle id must look like com.example.app")
    root = (args.output or Path(args.bundle_id.rsplit(".", 1)[-1])).resolve()
    if root.exists() and any(root.iterdir()):
        raise SystemExit(f"eos-sdk error: output directory is not empty: {root}")
    (root / "src").mkdir(parents=True, exist_ok=True)
    (root / "resources").mkdir()
    (root / "docs").mkdir()
    (root / "src" / "main.elang").write_text('app "' + args.bundle_id + '"\nversion "0.1.0"\ntext "Hello from EOS"\nprint "Etternhall app"\n', encoding="utf-8")
    manifest = {
        "format": "eapp",
        "format_version": 2,
        "identity": {"bundle_id": args.bundle_id, "publisher": "Etternhall Labs", "author": args.author},
        "version": "0.1.0",
        "api": "elang-0.1",
        "min_eos": ">=0.1.0",
        "entrypoint": "src/main.eosbc",
        "targets": ["eos-x86_64", "eos-aarch64"],
        "permissions": [],
        "resources": {"icon": "resources/icon.svg", "splash": "resources/splash.svg", "docs": "docs/README.md"},
    }
    (root / "eapp.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (root / "docs" / "README.md").write_text(f"# {args.bundle_id}\n\nAplicación EOS generada por eos-sdk.\n", encoding="utf-8")
    (root / "resources" / "icon.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#314f89"/><circle cx="32" cy="32" r="16" fill="#f6f8ff"/></svg>\n', encoding="utf-8")
    (root / "resources" / "splash.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 180"><rect width="320" height="180" fill="#101522"/><text x="160" y="96" text-anchor="middle" fill="#f6f8ff" font-size="24">EOS</text></svg>\n', encoding="utf-8")
    print(f"created EOS project at {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
