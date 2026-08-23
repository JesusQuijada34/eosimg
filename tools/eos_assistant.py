#!/usr/bin/env python3
"""EOS local assistant launcher.

Selection is local and deterministic. Actual inference is opt-in and requires
an explicitly supplied local GGUF file plus an installed llama.cpp CLI.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

from eos_model_select import ram_gib, select


def main() -> int:
    parser = argparse.ArgumentParser(prog="eos-assistant", description="Select or run the EOS local assistant")
    parser.add_argument("prompt", nargs="?", default="Hola, EOS")
    parser.add_argument("--catalog", type=Path, default=Path(__file__).resolve().parents[1] / "config" / "eos-models.json")
    parser.add_argument("--ram-gib", type=float, default=None)
    parser.add_argument("--architecture", default=None)
    parser.add_argument("--model-file", type=Path, default=None)
    parser.add_argument("--run", action="store_true", help="run local inference; otherwise print plan")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
        import platform
        result = select(catalog, args.ram_gib if args.ram_gib is not None else ram_gib(), args.architecture or platform.machine(), "assistant")
        if result["selected"] is None:
            raise ValueError(result["reason"])
        if not args.run:
            result.update({"mode": "plan-only", "prompt": args.prompt, "network": "disabled"})
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        if args.model_file is None or not args.model_file.is_file():
            raise ValueError("--model-file must point to a local GGUF file")
        if args.model_file.suffix.lower() != ".gguf":
            raise ValueError("EOS assistant currently permits only local .gguf models")
        llama = shutil.which("llama-cli") or shutil.which("main")
        if llama is None:
            raise ValueError("llama.cpp CLI not installed; inference was not attempted")
        command = [llama, "-m", str(args.model_file), "-p", args.prompt, "-n", "256", "--no-display-prompt"]
        environment = os.environ.copy()
        environment["HF_HUB_OFFLINE"] = "1"
        environment["NO_PROXY"] = "*"
        completed = subprocess.run(command, check=False, env=environment)
        return completed.returncode
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"eos-assistant error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
