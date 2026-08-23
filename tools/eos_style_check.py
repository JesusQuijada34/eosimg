#!/usr/bin/env python3
"""Validate EOS CSS-like styles and EOS animation YAML contracts."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re

STYLE_PROPERTIES = {"background", "color", "safe-area", "touch-target", "focus-ring", "material", "notch-avoidance", "elevation"}
ANIMATION_PROPERTIES = {"opacity", "translate-x", "translate-y", "scale", "color"}


def check_css(path: Path) -> dict[str, object]:
    raw = path.read_text(encoding="utf-8")
    if "@activity " not in raw:
        raise ValueError(f"{path}: missing @activity block")
    for line in raw.splitlines():
        stripped = line.strip()
        if ":" in stripped and not stripped.startswith(("@", "#")):
            property_name = stripped.split(":", 1)[0].strip()
            if property_name not in STYLE_PROPERTIES:
                raise ValueError(f"{path}: unsupported EOS CSS property {property_name}")
    return {"file": str(path), "kind": "eos-css", "status": "valid"}


def check_animation(path: Path) -> dict[str, object]:
    raw = path.read_text(encoding="utf-8")
    if "schema: eos-animation-0.1" not in raw or "animations:" not in raw:
        raise ValueError(f"{path}: invalid animation schema")
    if "duration_ms:" not in raw or "property:" not in raw:
        raise ValueError(f"{path}: duration and property are required")
    properties = re.findall(r"^\s+property:\s*([A-Za-z0-9_-]+)\s*$", raw, flags=re.MULTILINE)
    if any(value not in ANIMATION_PROPERTIES for value in properties):
        raise ValueError(f"{path}: unsupported EOS animation property")
    return {"file": str(path), "kind": "eos-animation", "status": "valid"}


def main() -> int:
    parser = argparse.ArgumentParser(prog="eos-style-check")
    parser.add_argument("project", type=Path)
    args = parser.parse_args()
    try:
        reports = []
        for path in sorted((args.project / "styles").glob("*.eos.css")):
            reports.append(check_css(path))
        for path in sorted((args.project / "animations").glob("*.eos.yml")):
            reports.append(check_animation(path))
        print(json.dumps({"schema": "eos-style-report-0.1", "files": reports, "status": "valid"}, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError) as exc:
        raise SystemExit(f"eos-style-check error: {exc}")


if __name__ == "__main__":
    raise SystemExit(main())
