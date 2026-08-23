#!/usr/bin/env python3
"""Select a local EOS model from a reviewed Hugging Face catalog."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import platform
import shutil


def ram_gib() -> float:
    meminfo = Path("/proc/meminfo")
    if meminfo.exists():
        for line in meminfo.read_text(encoding="utf-8").splitlines():
            if line.startswith("MemTotal:"):
                return int(line.split()[1]) / 1024 / 1024
    return 4.0


def select(catalog: dict, ram: float, architecture: str, task: str) -> dict:
    candidates = [
        model for model in catalog.get("models", [])
        if architecture in model.get("architectures", [])
        and task in model.get("tasks", [])
        and float(model.get("min_ram_gib", 10**9)) <= ram * 0.65
    ]
    if not candidates:
        return {"selected": None, "reason": "no model fits the protected memory budget", "ram_gib": round(ram, 2), "architecture": architecture, "task": task}
    chosen = max(candidates, key=lambda model: float(model.get("estimated_ram_gib", 0)))
    return {
        "selected": chosen,
        "ram_gib": round(ram, 2),
        "protected_budget_gib": round(ram * 0.65, 2),
        "architecture": architecture,
        "task": task,
        "download": "not-performed",
        "execution": "not-performed",
        "license": "must-be-reviewed-before-install",
        "revision": "must-be-pinned-before-download",
    }


def main() -> int:
    parser = argparse.ArgumentParser(prog="eos-model-select", description="Select an EOS local model")
    parser.add_argument("--catalog", type=Path, default=Path(__file__).resolve().parents[1] / "config" / "eos-models.json")
    parser.add_argument("--ram-gib", type=float, default=None)
    parser.add_argument("--architecture", default=platform.machine())
    parser.add_argument("--task", default="assistant")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
        ram = args.ram_gib if args.ram_gib is not None else ram_gib()
        result = select(catalog, ram, args.architecture, args.task)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["selected"] is not None else 3
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"eos-model-select error: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
