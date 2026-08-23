#!/usr/bin/env python3
"""EOS development build engine.

This orchestrator builds source artifacts only. It does not create GitHub
releases or publish images.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def run(command: list[str], cwd: Path) -> None:
    print("+", " ".join(command))
    subprocess.run(command, cwd=cwd, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(prog="eos-build", description="Build EOS development artifacts")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--configuration", choices=("Debug", "Release"), default="Debug")
    args = parser.parse_args()
    root = args.root.resolve()
    build = root / "build" / "engine"
    build.mkdir(parents=True, exist_ok=True)
    run(["cmake", "-S", str(root), "-B", str(build), f"-DCMAKE_BUILD_TYPE={args.configuration}"], root)
    run(["cmake", "--build", str(build), "-j2"], root)
    run([sys.executable, str(root / "tools" / "eoslangc.py"), str(root / "tests" / "hello.elang"), str(build / "hello.eosbc")], root)
    run([str(root / "tools" / "build_initramfs.sh")], root)
    manifest = {
        "product": "Etternhall Operating System",
        "build_engine": "eos-build/0.1",
        "configuration": args.configuration,
        "artifacts": {
            "eos_init": str(build / "eos-init"),
            "eos_serviced": str(build / "eos-serviced"),
            "phone_shell": str(build / "eos-phone-shell"),
            "elang_demo": str(build / "hello.eosbc"),
            "initramfs": str(root / "build" / "eos-initramfs.img"),
        },
        "publishing": "disabled-until-stable",
    }
    (build / "build-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"build manifest: {build / 'build-manifest.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
