#!/usr/bin/env python3
"""EOS application launcher policy prototype.

The production launcher will start only an installed, trusted .eapp through
EOSRuntime. This prototype validates the boundary and offers dry-run only.
"""
from __future__ import annotations

import argparse
import base64
from pathlib import Path
import sys

from eapp import load_public_key, read_package, verify_signature, version_tuple

EAPP_V2 = b"EAPP\x00\x02\x00\x00"
ELF = b"\x7fELF"
DEB_AR = b"!<arch>\n"


def reject_host_format(path: Path) -> None:
    with path.open("rb") as handle:
        prefix = handle.read(8)
    if prefix.startswith(ELF):
        raise ValueError("ELF Linux de usuario rechazado por la ABI de EOS")
    if prefix == DEB_AR or path.suffix.lower() == ".deb":
        raise ValueError("paquete .deb rechazado: EOS no implementa dpkg/apt")
    if prefix != EAPP_V2:
        raise ValueError("formato rechazado: se requiere un contenedor .eapp EOS v2")


def main() -> int:
    parser = argparse.ArgumentParser(prog="eos-launch", description="Validate an EOS application launch")
    parser.add_argument("package", type=Path)
    parser.add_argument("--eos-version", default="0.1.0")
    parser.add_argument("--trusted-key", default=None)
    parser.add_argument("--dry-run", action="store_true", help="validate only; do not launch")
    args = parser.parse_args()
    try:
        reject_host_format(args.package)
        metadata, payload = read_package(args.package)
        status = verify_signature(metadata, payload)
        if status != "ed25519-ok":
            raise ValueError(f"launcher requires a valid signature, got {status}")
        if args.trusted_key:
            signature = metadata["signature"]
            package_public = base64.b64decode(signature["public_key"], validate=True)
            trusted_public = load_public_key(Path(args.trusted_key)).public_bytes_raw()
            if package_public != trusted_public:
                raise ValueError("package signer is not trusted")
        if version_tuple(args.eos_version) < version_tuple(str(metadata.get("min_eos", ">=0.0.0"))):
            raise ValueError("installed EOS is below package min_eos")
        if not args.dry_run:
            raise ValueError("prototype launcher is validation-only; --dry-run is required")
        print(f"validated launch: {metadata['identity']['bundle_id']} {metadata['version']} ({status})")
        return 0
    except (OSError, KeyError, TypeError, ValueError) as exc:
        print(f"eos-launch error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
