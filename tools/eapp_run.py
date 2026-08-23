#!/usr/bin/env python3
"""Execute the EOSBC entrypoint contained in a signed .eapp.

Only EOSBC JSON instructions are accepted. Native host executables and scripts
are never invoked by this prototype.
"""
from __future__ import annotations

import argparse
import io
import json
import tarfile
import tempfile
from pathlib import Path
import subprocess
import sys

from eapp import read_package, verify_signature, version_tuple


def main() -> int:
    parser = argparse.ArgumentParser(prog="eapp-run", description="Run a signed EOSBC .eapp")
    parser.add_argument("package", type=Path)
    parser.add_argument("--eos-version", default="0.1.0")
    args = parser.parse_args()
    try:
        metadata, payload = read_package(args.package)
        if verify_signature(metadata, payload) != "ed25519-ok":
            raise ValueError("eapp-run requires an Ed25519-signed package")
        if version_tuple(args.eos_version) < version_tuple(str(metadata.get("min_eos", ">=0.0.0"))):
            raise ValueError("EOS version does not satisfy package min_eos")
        entrypoint = str(metadata.get("entrypoint", ""))
        if not entrypoint.endswith(".eosbc") or entrypoint.startswith("/") or ".." in Path(entrypoint).parts:
            raise ValueError("only a relative .eosbc entrypoint is supported")
        with tarfile.open(fileobj=io.BytesIO(payload), mode="r:gz") as archive:
            member = archive.getmember(entrypoint)
            if not member.isfile():
                raise ValueError("entrypoint is not a regular file")
            bytecode = archive.extractfile(member).read()
        with tempfile.NamedTemporaryFile(prefix="eosbc-", suffix=".json", delete=False) as temp:
            temp.write(bytecode)
            bytecode_path = Path(temp.name)
        try:
            runtime = Path(__file__).with_name("eosrun.py")
            result = subprocess.run([sys.executable, str(runtime), str(bytecode_path)], check=False)
            return result.returncode
        finally:
            bytecode_path.unlink(missing_ok=True)
    except (OSError, KeyError, TypeError, ValueError, tarfile.TarError, json.JSONDecodeError) as exc:
        print(f"eapp-run error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
