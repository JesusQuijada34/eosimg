#!/usr/bin/env python3
"""EOS adapter for a locally built llama.cpp executable."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys

DEFAULT_BIN = Path(__file__).resolve().parents[1] / "build" / "third_party" / "llama.cpp" / "build" / "bin" / "llama-simple-chat"
DEFAULT_COMMIT = Path(__file__).resolve().parents[1] / "build" / "third_party" / "llama.cpp.commit"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(prog="eos-llama-backend")
    parser.add_argument("prompt", nargs="?", default="Hola, Hi Eaid")
    parser.add_argument("--llama-bin", type=Path, default=Path(os.environ.get("EOS_LLAMA_BIN", DEFAULT_BIN)))
    parser.add_argument("--commit-file", type=Path, default=DEFAULT_COMMIT)
    parser.add_argument("--model", type=Path, default=None)
    parser.add_argument("--sha256", default=None)
    parser.add_argument("--context-size", type=int, default=2048)
    parser.add_argument("--gpu-layers", type=int, default=0)
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        if not args.llama_bin.is_file() or not os.access(args.llama_bin, os.X_OK):
            raise ValueError(f"llama.cpp executable not found or not executable: {args.llama_bin}")
        commit = args.commit_file.read_text(encoding="utf-8").strip() if args.commit_file.is_file() else "unknown"
        result = {
            "backend": "llama.cpp",
            "executable": str(args.llama_bin),
            "llama_commit": commit,
            "architecture": platform.machine(),
            "network": "disabled",
            "model_download": "not-performed",
            "execution": "not-performed",
        }
        if not args.run:
            print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else json.dumps(result, ensure_ascii=False))
            return 0
        if args.model is None or not args.model.is_file():
            raise ValueError("--run requires an existing local --model GGUF")
        if args.model.suffix.lower() != ".gguf":
            raise ValueError("EOS llama backend accepts only .gguf models")
        actual_hash = sha256(args.model)
        if not args.sha256 or actual_hash.lower() != args.sha256.lower():
            raise ValueError("--sha256 is required and must match the local model")
        if args.context_size < 256 or args.context_size > 131072:
            raise ValueError("context size outside EOS safety range")
        if args.gpu_layers < 0:
            raise ValueError("gpu layers cannot be negative")
        command = [str(args.llama_bin), "-m", str(args.model), "-c", str(args.context_size), "-ngl", str(args.gpu_layers)]
        environment = os.environ.copy()
        environment["HF_HUB_OFFLINE"] = "1"
        environment["NO_PROXY"] = "*"
        result.update({"model": str(args.model), "model_sha256": actual_hash, "execution": "started", "command": command})
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2), file=sys.stderr)
        completed = subprocess.run(command, input=args.prompt + "\n", text=True, env=environment, timeout=120, check=False)
        return completed.returncode
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(f"eos-llama-backend error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
