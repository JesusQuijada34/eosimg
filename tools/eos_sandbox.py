#!/usr/bin/env python3
"""Generate an EOS sandbox policy from a validated .eapp package.

This prototype produces policy data only. Enforcement will be implemented in
the EOS process supervisor using namespaces, seccomp and cgroups.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from eapp import read_package, verify_signature

KNOWN_PERMISSIONS = {
    "filesystem.user": {"user_data": "read-write"},
    "filesystem.documents": {"documents": "read-write"},
    "network.client": {"network": "outbound-only"},
    "camera": {"devices.camera": "prompt"},
    "microphone": {"devices.microphone": "prompt"},
    "location": {"sensors.location": "prompt"},
}


def policy_for(package: Path) -> dict:
    metadata, payload = read_package(package)
    signature_status = verify_signature(metadata, payload)
    if signature_status != "ed25519-ok":
        raise ValueError(f"sandbox requires a valid package signature, got {signature_status}")
    requested = metadata.get("permissions", [])
    if not isinstance(requested, list) or any(permission not in KNOWN_PERMISSIONS for permission in requested):
        unknown = [permission for permission in requested if permission not in KNOWN_PERMISSIONS]
        raise ValueError(f"unknown permissions: {unknown}")
    mounts = {"app": "read-only", "user_data": "private", "cache": "private"}
    capabilities: dict[str, str] = {}
    for permission in requested:
        capabilities.update(KNOWN_PERMISSIONS[permission])
    return {
        "policy": "eos-sandbox-0.1",
        "bundle_id": metadata["identity"]["bundle_id"],
        "version": metadata["version"],
        "signature_status": signature_status,
        "network": capabilities.pop("network", "none"),
        "mounts": mounts,
        "capabilities": capabilities,
        "process": {"no_new_privileges": True, "memory_limit_mb": 512, "cpu_quota_percent": 100, "device_access": "deny-by-default"},
        "enforcement": "planned-in-eos-process-supervisor",
    }


def main() -> int:
    parser = argparse.ArgumentParser(prog="eos-sandbox", description="Generate an EOS app sandbox policy")
    parser.add_argument("package", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        policy = policy_for(args.package)
        encoded = json.dumps(policy, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(encoded, encoding="utf-8")
        else:
            print(encoded, end="")
        return 0
    except (OSError, KeyError, TypeError, ValueError) as exc:
        print(f"eos-sandbox error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
