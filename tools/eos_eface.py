#!/usr/bin/env python3
"""eFace enrollment stub: no camera or biometric matching is implemented."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import secrets

CONSENT = "I CONSENT TO LOCAL EFACE ENROLLMENT"


def load(path: Path) -> dict:
    if not path.exists():
        return {"schema": "eos-eface-0.1", "status": "not-enrolled", "biometric_engine": "not-implemented"}
    return json.loads(path.read_text(encoding="utf-8"))


def save(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)


def pin_verifier(pin: str, salt: bytes) -> str:
    return hashlib.pbkdf2_hmac("sha256", pin.encode(), salt, 240_000).hex()


def main() -> int:
    parser = argparse.ArgumentParser(prog="eos-eface")
    parser.add_argument("--root", type=Path, required=True)
    sub = parser.add_subparsers(dest="command", required=True)
    enroll = sub.add_parser("enroll")
    enroll.add_argument("--consent", required=True)
    enroll.add_argument("--fallback-pin", required=True)
    sub.add_parser("status")
    args = parser.parse_args()
    path = args.root / "eface.json"
    try:
        if args.command == "status":
            print(json.dumps(load(path), ensure_ascii=False, indent=2))
            return 0
        if args.consent != CONSENT:
            raise ValueError("exact consent phrase is required")
        if not args.fallback_pin.isdigit() or not 4 <= len(args.fallback_pin) <= 12:
            raise ValueError("fallback PIN must contain 4..12 digits")
        salt = secrets.token_bytes(16)
        data = {
            "schema": "eos-eface-0.1",
            "status": "enrollment-ready",
            "biometric_engine": "not-implemented",
            "camera_capture": "not-performed",
            "local_only": True,
            "fallback": {"method": "pbkdf2-sha256", "salt": salt.hex(), "verifier": pin_verifier(args.fallback_pin, salt)},
            "consent": "recorded",
        }
        save(path, data)
        print(json.dumps({k: v for k, v in data.items() if k != "fallback"}, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"eos-eface error: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
