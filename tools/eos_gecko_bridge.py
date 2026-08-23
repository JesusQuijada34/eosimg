#!/usr/bin/env python3
"""EOS Browser bridge for a trusted Gecko host process.

The bridge does not treat Firefox as a user app: it must be supplied as an
internal EOS component and execution is opt-in. Plan mode is the default.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
from urllib.parse import urlparse


def main() -> int:
    parser = argparse.ArgumentParser(prog="eos-gecko-bridge")
    parser.add_argument("uri", nargs="?", default="about:blank")
    parser.add_argument("--gecko-runner", type=Path, required=True)
    parser.add_argument("--profile-root", type=Path, required=True)
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        parsed = urlparse(args.uri)
        if parsed.scheme not in {"http", "https", "about"}:
            raise ValueError("EOS Browser accepts only http(s) or about: URIs")
        if not args.gecko_runner.is_file() or not os.access(args.gecko_runner, os.X_OK):
            raise ValueError("Gecko runner must be an executable internal EOS component")
        args.profile_root.mkdir(parents=True, exist_ok=True)
        command = [str(args.gecko_runner), "--no-remote", "--profile", str(args.profile_root), args.uri]
        if args.headless:
            command.insert(1, "--headless")
        result = {
            "backend": "gecko",
            "runner": str(args.gecko_runner),
            "profile": str(args.profile_root),
            "uri": args.uri,
            "network": "requested-by-page-policy",
            "execution": "not-performed",
            "command": command,
        }
        if not args.run:
            print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else json.dumps(result, ensure_ascii=False))
            return 0
        result["execution"] = "started"
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2), file=sys.stderr)
        environment = os.environ.copy()
        environment["MOZ_DISABLE_AUTO_SAFE_MODE"] = "1"
        completed = subprocess.run(command, env=environment, check=False, timeout=120)
        return completed.returncode
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(f"eos-gecko-bridge error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
