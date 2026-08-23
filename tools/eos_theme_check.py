#!/usr/bin/env python3
"""Validate Etternhall theme and accessibility contracts."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REQUIRED = {"surface", "surface-elevated", "surface-accent", "text", "text-secondary", "accent", "focus", "radius", "touch-target-min"}


def main() -> int:
    parser = argparse.ArgumentParser(prog="eos-theme-check")
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    try:
        data = json.loads(args.path.read_text(encoding="utf-8"))
        themes = data["themes"]
        if data["default"] not in themes:
            raise ValueError("default theme is not declared")
        for name, theme in themes.items():
            missing = REQUIRED - set(theme)
            if missing:
                raise ValueError(f"{name}: missing {sorted(missing)}")
            if int(theme["touch-target-min"]) < 44:
                raise ValueError(f"{name}: touch-target-min is too small")
            if int(theme["radius"]) < 0:
                raise ValueError(f"{name}: radius cannot be negative")
        accessibility = data["accessibility"]
        for key in ("focus-visible", "keyboard-navigation", "reduced-motion", "screen-reader-labels"):
            if key not in accessibility:
                raise ValueError(f"accessibility: missing {key}")
        print(json.dumps({"schema": "eos-theme-report-0.1", "themes": sorted(themes), "status": "valid"}, indent=2))
        return 0
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise SystemExit(f"eos-theme-check error: {exc}")


if __name__ == "__main__":
    raise SystemExit(main())
