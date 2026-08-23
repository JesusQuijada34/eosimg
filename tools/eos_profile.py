#!/usr/bin/env python3
"""Local EOS ID/profile and eRalf/eJairo theme state."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import uuid

THEMES = {
    "ocean": {"accent": "#4E77D8", "surface": "#F6F8FF", "ink": "#101522"},
    "graphite": {"accent": "#9AA7C2", "surface": "#151A24", "ink": "#F5F7FC"},
    "meadow": {"accent": "#3D9970", "surface": "#F2FAF6", "ink": "#102019"},
}


def read(path: Path) -> dict:
    if not path.exists():
        return {"schema": "eos-profile-0.1", "identity": None, "theme": "ocean", "sync": "disabled"}
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != "eos-profile-0.1":
        raise ValueError("invalid EOS profile schema")
    return data


def write(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser(prog="eos-profile")
    parser.add_argument("--root", type=Path, required=True)
    sub = parser.add_subparsers(dest="command", required=True)
    create = sub.add_parser("create")
    create.add_argument("display_name")
    theme = sub.add_parser("theme")
    theme.add_argument("name", choices=sorted(THEMES))
    sub.add_parser("show")
    args = parser.parse_args()
    path = args.root / "profile.json"
    try:
        data = read(path)
        if args.command == "create":
            display_name = args.display_name.strip()
            if not display_name or len(display_name) > 80:
                raise ValueError("display name must contain 1..80 characters")
            if data["identity"] is None:
                data["identity"] = {"eos_id": "local-" + uuid.uuid4().hex, "display_name": display_name}
            else:
                data["identity"]["display_name"] = display_name
            data["sync"] = "disabled-until-consent"
            write(path, data)
        elif args.command == "theme":
            data["theme"] = args.name
            data["theme_tokens"] = THEMES[args.name]
            write(path, data)
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"eos-profile error: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
