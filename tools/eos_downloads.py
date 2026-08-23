#!/usr/bin/env python3
"""EOS downloads queue: offline planning and local verification only."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import urlparse
import uuid


def load(path: Path) -> dict:
    if not path.exists():
        return {"schema": "eos-downloads-0.1", "items": []}
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != "eos-downloads-0.1" or not isinstance(data.get("items"), list):
        raise ValueError("invalid EOS downloads queue")
    return data


def save(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def plan(args: argparse.Namespace) -> int:
    parsed = urlparse(args.url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("only explicit http(s) URLs are accepted")
    destination = Path(args.destination)
    if destination.is_absolute() or ".." in destination.parts:
        raise ValueError("destination must be a relative EOS download path")
    data = load(args.queue)
    item = {
        "id": "dl-" + uuid.uuid4().hex[:12],
        "url": args.url,
        "destination": str(destination),
        "expected_size": args.size,
        "sha256": args.sha256,
        "status": "planned",
        "network": "disabled-until-user-consent",
    }
    data["items"].append(item)
    save(args.queue, data)
    print(json.dumps(item, ensure_ascii=False, indent=2))
    return 0


def verify(args: argparse.Namespace) -> int:
    data = load(args.queue)
    matches = [item for item in data["items"] if item["id"] == args.id]
    if len(matches) != 1:
        raise ValueError("download id not found")
    item = matches[0]
    file_path = args.root / item["destination"]
    if not file_path.is_file():
        raise ValueError("download payload is missing")
    size = file_path.stat().st_size
    digest = hashlib.sha256(file_path.read_bytes()).hexdigest()
    if item["expected_size"] is not None and size != item["expected_size"]:
        raise ValueError(f"size mismatch: expected {item['expected_size']}, got {size}")
    if item["sha256"] is not None and digest != item["sha256"]:
        raise ValueError("sha256 mismatch")
    item["status"] = "verified"
    item["actual_size"] = size
    item["actual_sha256"] = digest
    save(args.queue, data)
    print(json.dumps(item, ensure_ascii=False, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="eos-downloads")
    parser.add_argument("--queue", type=Path, required=True)
    sub = parser.add_subparsers(dest="command", required=True)
    plan_parser = sub.add_parser("plan")
    plan_parser.add_argument("url")
    plan_parser.add_argument("destination")
    plan_parser.add_argument("--size", type=int, default=None)
    plan_parser.add_argument("--sha256", default=None)
    verify_parser = sub.add_parser("verify")
    verify_parser.add_argument("id")
    verify_parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    try:
        return plan(args) if args.command == "plan" else verify(args)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"eos-downloads error: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
