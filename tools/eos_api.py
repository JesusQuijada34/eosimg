#!/usr/bin/env python3
"""EOS API registry and compatibility checker prototype."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

APIS = {
    "elang-0.1": {"status": "experimental", "features": ["strings", "integers", "ui.text", "print"]},
    "eos-ui-0.1": {"status": "experimental", "features": ["surfaces", "touch", "virtual-keyboard"]},
    "eos-storage-0.1": {"status": "experimental", "features": ["user-data", "cache"]},
    "eos-permissions-0.1": {"status": "experimental", "features": ["declarative-permissions", "sandbox-policy"]},
}


def valid_api(value: str) -> bool:
    return bool(re.fullmatch(r"[a-z0-9-]+-[0-9]+\.[0-9]+", value))


def check_package(package: Path) -> dict:
    from eapp import read_package, verify_signature
    metadata, payload = read_package(package)
    signature = verify_signature(metadata, payload)
    api = metadata.get("api")
    if not isinstance(api, str) or not valid_api(api):
        raise ValueError("invalid api identifier")
    if api not in APIS:
        raise ValueError(f"unsupported EOS API: {api}")
    return {"bundle_id": metadata["identity"]["bundle_id"], "api": api, "api_status": APIS[api]["status"], "signature_status": signature, "compatible": signature == "ed25519-ok"}


def main() -> int:
    parser = argparse.ArgumentParser(prog="eos-api", description="Inspect EOS API registry or check an eapp")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list")
    check = sub.add_parser("check")
    check.add_argument("package", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "list":
            print(json.dumps(APIS, ensure_ascii=False, indent=2))
        else:
            print(json.dumps(check_package(args.package), ensure_ascii=False, indent=2))
        return 0
    except (OSError, KeyError, TypeError, ValueError) as exc:
        print(f"eos-api error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
