#!/usr/bin/env python3
"""EOS A/B update manager prototype.

Updates are staged under an explicit development root and activated by an
atomic pointer replacement. No host disks or boot variables are modified.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import tempfile


def load_state(root: Path) -> dict:
    path = root / "update-state.json"
    if not path.exists():
        return {"active": "A", "boot_once": None, "slots": {"A": None, "B": None}}
    return json.loads(path.read_text(encoding="utf-8"))


def save_state(root: Path, state: dict) -> None:
    root.mkdir(parents=True, exist_ok=True)
    path = root / "update-state.json"
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def stage(root: Path, image: Path, version: str) -> None:
    state = load_state(root)
    inactive = "B" if state["active"] == "A" else "A"
    slots = root / "slots"
    slots.mkdir(parents=True, exist_ok=True)
    target = slots / inactive
    if target.exists():
        shutil.rmtree(target)
    with tempfile.TemporaryDirectory(prefix="eos-slot-", dir=str(slots)) as tmp:
        staged = Path(tmp) / "image"
        staged.mkdir()
        shutil.copy2(image, staged / image.name)
        (staged / "slot.json").write_text(json.dumps({"slot": inactive, "version": version, "image": image.name}, indent=2) + "\n", encoding="utf-8")
        os.replace(staged, target)
    state["slots"][inactive] = {"version": version, "path": str(target), "verified": True}
    state["boot_once"] = inactive
    save_state(root, state)
    print(f"staged slot {inactive} version {version}; next boot will try it")


def mark_success(root: Path) -> None:
    state = load_state(root)
    if state.get("boot_once") not in {"A", "B"}:
        raise ValueError("no pending boot slot")
    state["active"] = state["boot_once"]
    state["boot_once"] = None
    save_state(root, state)
    print(f"slot {state['active']} marked successful")


def rollback(root: Path) -> None:
    state = load_state(root)
    state["boot_once"] = None
    state["active"] = "B" if state["active"] == "A" else "A"
    save_state(root, state)
    print(f"rollback selected slot {state['active']}")


def main() -> int:
    parser = argparse.ArgumentParser(prog="eos-update", description="EOS A/B update manager")
    sub = parser.add_subparsers(dest="command", required=True)
    stage_parser = sub.add_parser("stage")
    stage_parser.add_argument("image", type=Path)
    stage_parser.add_argument("--version", required=True)
    stage_parser.add_argument("--root", required=True, type=Path)
    for name in ("mark-success", "rollback", "status"):
        cmd = sub.add_parser(name)
        cmd.add_argument("--root", required=True, type=Path)
    args = parser.parse_args()
    try:
        if args.command == "stage":
            if not args.image.is_file():
                raise ValueError("image does not exist")
            stage(args.root, args.image, args.version)
        elif args.command == "mark-success":
            mark_success(args.root)
        elif args.command == "rollback":
            rollback(args.root)
        else:
            print(json.dumps(load_state(args.root), ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        raise SystemExit(f"eos-update error: {exc}")


if __name__ == "__main__":
    raise SystemExit(main())
