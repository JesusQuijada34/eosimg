#!/usr/bin/env python3
"""EOS Studio preview runner for activities and declarative UI."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def load(project: Path) -> tuple[dict, list[dict]]:
    manifest = json.loads((project / "eapp.json").read_text(encoding="utf-8"))
    activities = manifest.get("activities", {}).get("definitions", [])
    if not activities:
        raise ValueError("project has no activities")
    return manifest, activities


def controls(ui_path: Path) -> list[str]:
    values = []
    for line in ui_path.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("- type:"):
            values.append(line.split(":", 1)[1].strip())
    return values


def main() -> int:
    parser = argparse.ArgumentParser(prog="eos-preview")
    parser.add_argument("project", type=Path)
    parser.add_argument("--activity", default=None)
    parser.add_argument("--event", default="app.launch")
    args = parser.parse_args()
    try:
        manifest, activities = load(args.project)
        main_activity = manifest["activities"]["main"]
        selected = args.activity or main_activity
        definition = next((item for item in activities if item.get("id") == selected), None)
        if definition is None:
            raise ValueError(f"unknown activity: {selected}")
        ui = args.project / definition["ui"]
        report = {
            "schema": "eos-preview-0.1",
            "bundle_id": manifest["identity"]["bundle_id"],
            "activity": selected,
            "main_activity": main_activity,
            "event": args.event,
            "lifecycle": ["created", "started", "resumed"],
            "ui": str(definition["ui"]),
            "controls": controls(ui),
            "safe_area": "safe_area: true" in ui.read_text(encoding="utf-8"),
            "styles": (args.project / "styles").exists(),
            "animations": (args.project / "animations").exists(),
            "hardware": "simulated",
            "permissions": "not-granted",
            "status": "preview-ready",
        }
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise SystemExit(f"eos-preview error: {exc}")


if __name__ == "__main__":
    raise SystemExit(main())
