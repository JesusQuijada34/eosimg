#!/usr/bin/env python3
"""EOS Studio debug driver for EosLang/EOSBC projects."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(prog="eos-debug")
    parser.add_argument("project", type=Path)
    parser.add_argument("--event", default="app.launch")
    args = parser.parse_args()
    source = args.project / "src/main.elang"
    if not source.is_file():
        raise SystemExit(f"eos-debug error: missing {source}")
    try:
        with tempfile.TemporaryDirectory(prefix="eos-debug-") as temp:
            bytecode = Path(temp) / "main.eosbc"
            subprocess.run([sys.executable, str(ROOT / "tools/eoslangc.py"), str(source), str(bytecode)], check=True, capture_output=True, text=True)
            completed = subprocess.run([sys.executable, str(ROOT / "tools/eosrun.py"), str(bytecode), "--event", args.event], check=True, capture_output=True, text=True)
            lines = completed.stdout.splitlines()
            report = {
                "schema": "eos-debug-0.1",
                "event": args.event,
                "trace": {
                    "lifecycle": [line for line in lines if "[event]" in line],
                    "ui": [line for line in lines if "[ui." in line or "eos.ui." in line],
                    "navigation": [line for line in lines if "eos.navigation." in line],
                    "services": [line for line in lines if "[eos.call]" in line and "eos.ui." not in line and "eos.navigation." not in line],
                },
                "stdout": lines,
                "status": "pass",
            }
            print(json.dumps(report, ensure_ascii=False, indent=2))
            return 0
    except subprocess.CalledProcessError as exc:
        raise SystemExit(f"eos-debug error: {exc.stderr or exc.stdout}") from exc


if __name__ == "__main__":
    raise SystemExit(main())
