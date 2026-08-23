#!/usr/bin/env python3
"""Validate and resolve the EOS service graph."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(prog="eos-service-graph")
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--all", action="store_true", help="resolve every service, not only the boot target")
    args = parser.parse_args()
    try:
        data = json.loads(args.manifest.read_text(encoding="utf-8"))
        services = {service["name"]: service for service in data["services"]}
        temporary: set[str] = set()
        permanent: set[str] = set()
        order: list[str] = []

        def visit(name: str) -> None:
            if name in permanent:
                return
            if name in temporary:
                raise ValueError(f"dependency cycle at {name}")
            if name not in services:
                raise ValueError(f"unknown service {name}")
            temporary.add(name)
            for dependency in services[name]["dependencies"]:
                visit(dependency)
            temporary.remove(name)
            permanent.add(name)
            order.append(name)

        roots = list(services) if args.all else [data["boot_target"]]
        for root in roots:
            visit(root)
        network = {name: services[name]["network"] for name in order}
        result = {"schema": "eos-service-plan-0.1", "boot_target": data["boot_target"], "scope": "all" if args.all else "boot-target", "order": order, "network": network, "status": "valid"}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, KeyError, ValueError, json.JSONDecodeError) as exc:
        print(f"eos-service-graph error: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
