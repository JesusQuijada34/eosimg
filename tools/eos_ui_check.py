#!/usr/bin/env python3
"""Validate the restricted EOS UI declarative format."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re

CONTROL_TYPES = {"app_bar", "text", "text_input", "button", "floating_button", "list", "image", "navigation"}
ACTIVITY = re.compile(r"^activity:\s+([a-z][a-z0-9_.-]*)$")


def check(path: Path) -> dict[str, object]:
    raw = path.read_text(encoding="utf-8")
    lines = [line.rstrip() for line in raw.splitlines() if line.strip()]
    if not lines or lines[0] != "schema: eos-ui-0.1":
        raise ValueError(f"{path}: expected schema eos-ui-0.1")
    activity = None
    controls = []
    for line in lines:
        match = ACTIVITY.match(line.strip())
        if match:
            activity = match.group(1)
        stripped = line.strip()
        if stripped.startswith("- type:"):
            control = stripped.split(":", 1)[1].strip()
            if control not in CONTROL_TYPES:
                raise ValueError(f"{path}: unsupported control type {control}")
            controls.append(control)
        if "bind:" in stripped and not re.fullmatch(r"bind:\s+[A-Za-z_][A-Za-z0-9_.]*", stripped):
            raise ValueError(f"{path}: invalid state binding")
        if "action:" in stripped and not re.fullmatch(r"(?:action|navigation):\s+[A-Za-z_][A-Za-z0-9_.-]*", stripped):
            raise ValueError(f"{path}: invalid action")
    if activity is None:
        raise ValueError(f"{path}: activity is required")
    if "safe_area: true" not in raw:
        raise ValueError(f"{path}: safe_area must be declared explicitly")
    return {"file": str(path), "activity": activity, "controls": controls, "status": "valid"}


def main() -> int:
    parser = argparse.ArgumentParser(prog="eos-ui-check")
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    try:
        files = sorted(args.path.glob("*.eosui")) if args.path.is_dir() else [args.path]
        reports = [check(path) for path in files]
        print(json.dumps({"schema": "eos-ui-report-0.1", "files": reports, "status": "valid"}, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError) as exc:
        raise SystemExit(f"eos-ui-check error: {exc}")


if __name__ == "__main__":
    raise SystemExit(main())
