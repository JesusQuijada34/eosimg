#!/usr/bin/env python3
"""Validate and list EOS application source projects."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re

BUNDLE_ID = re.compile(r"^[a-z][a-z0-9]*(?:\.[a-z0-9]+)+$")


def validate(project: Path) -> dict:
    manifest_path = project / "eapp.json"
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    identity = data.get("identity", {})
    bundle_id = identity.get("bundle_id")
    required = ["format", "format_version", "identity", "version", "api", "min_eos", "entrypoint", "targets", "permissions", "resources"]
    missing = [key for key in required if key not in data]
    if missing:
        raise ValueError(f"{manifest_path}: missing {', '.join(missing)}")
    if data["format"] != "eapp" or data["format_version"] != 2:
        raise ValueError(f"{manifest_path}: unsupported eapp format")
    if not isinstance(bundle_id, str) or not BUNDLE_ID.fullmatch(bundle_id):
        raise ValueError(f"{manifest_path}: invalid bundle_id")
    for field in ("publisher", "author"):
        if not identity.get(field):
            raise ValueError(f"{manifest_path}: identity.{field} is required")
    entrypoint = project / data["entrypoint"].replace(".eosbc", ".elang")
    if not entrypoint.is_file():
        raise ValueError(f"{manifest_path}: source entrypoint missing: {entrypoint}")
    resources = data["resources"]
    for label in ("icon", "splash", "docs"):
        resource = project / resources[label]
        if not resource.is_file():
            raise ValueError(f"{manifest_path}: resource {label} missing: {resource}")
    return {"bundle_id": bundle_id, "version": data["version"], "api": data["api"], "project": str(project)}


def main() -> int:
    parser = argparse.ArgumentParser(prog="eos-app-catalog")
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    try:
        apps = []
        errors = []
        for manifest in sorted(args.root.glob("*/eapp.json")):
            try:
                apps.append(validate(manifest.parent))
            except (OSError, ValueError, json.JSONDecodeError) as exc:
                errors.append(str(exc))
        result = {"schema": "eos-app-catalog-0.1", "apps": apps, "errors": errors}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1 if errors else 0
    except OSError as exc:
        print(f"eos-app-catalog error: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
