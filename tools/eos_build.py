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
    parser.add_argument("--jobs", type=int, default=2)
    parser.add_argument("--skip-initramfs", action="store_true")
    parser.add_argument("--skip-app-audit", action="store_true")
    args = parser.parse_args()
    if args.jobs < 1 or args.jobs > 32:
        raise SystemExit("eos-build error: jobs must be in range 1..32")
    root = args.root.resolve()
    build = root / "build" / "engine"
    build.mkdir(parents=True, exist_ok=True)
    run(["cmake", "-S", str(root), "-B", str(build), f"-DCMAKE_BUILD_TYPE={args.configuration}"], root)
    run(["cmake", "--build", str(build), f"-j{args.jobs}"], root)
    run([sys.executable, str(root / "tools" / "eoslangc.py"), str(root / "tests" / "hello.elang"), str(build / "hello.eosbc")], root)
    if not args.skip_initramfs:
        run([str(root / "tools" / "build_initramfs.sh")], root)
    app_catalog = None
    if not args.skip_app_audit:
        app_catalog = build / "app-catalog.json"
        with app_catalog.open("w", encoding="utf-8") as catalog_file:
            subprocess.run([sys.executable, str(root / "tools" / "eos_app_catalog.py"), str(root / "apps")], cwd=root, stdout=catalog_file, check=True)
    try:
        revision = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        revision = "unavailable"
    targets = ["eos-init", "eos-serviced", "eos-logd", "eos-storaged", "eos-sessiond", "eos-netd", "eos-powerd", "eos-packaged", "eos-supervise", "eos-assistantd", "eos-audiod", "eos-modeld", "eos-inputd", "eos-oobe", "eos-displayd", "eos-windowd", "eos-immersived", "eos-browserd", "eos-mediad", "eos-launcherd", "eos-marketd", "eos-photod", "eos-blinked", "eos-policyd", "eos-phone-shell"]
    manifest = {
        "product": "Etternhall Operating System",
        "build_engine": "eos-build/0.2",
        "configuration": args.configuration,
        "jobs": args.jobs,
        "source_revision": revision,
        "targets": targets,
        "artifacts": {
            "eos_init": str(build / "eos-init"),
            "eos_serviced": str(build / "eos-serviced"),
            "userland_bin_dir": str(build),
            "phone_shell": str(build / "eos-phone-shell"),
            "elang_demo": str(build / "hello.eosbc"),
            "initramfs": None if args.skip_initramfs else str(root / "build" / "eos-initramfs.img"),
            "app_catalog": None if app_catalog is None else str(app_catalog),
        },
        "publishing": "disabled-until-stable",
        "source_only": True,
    }
    (build / "build-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"build manifest: {build / 'build-manifest.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
