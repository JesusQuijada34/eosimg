#!/usr/bin/env python3
"""Passive .ipa inspector for EOS.

This tool reads a ZIP container, Info.plist and Mach-O headers. It does not
execute, resign, decrypt, patch or alter the application.
"""
from __future__ import annotations

import argparse
import json
import plistlib
import struct
import zipfile
from pathlib import PurePosixPath
from typing import Any

MACHO_64_LE = b"\xcf\xfa\xed\xfe"
MACHO_64_BE = b"\xfe\xed\xfa\xcf"
MACHO_32_LE = b"\xce\xfa\xed\xfe"
MACHO_32_BE = b"\xfe\xed\xfa\xce"
FAT_LE = b"\xca\xfe\xba\xbe"
FAT_BE = b"\xbe\xba\xfe\xca"
CPU_TYPE_ARM64 = 0x0100000C
CPU_TYPE_X86_64 = 0x01000007


def macho_summary(data: bytes) -> dict[str, Any]:
    if len(data) < 8:
        return {"kind": "unknown", "reason": "too-small"}
    magic = data[:4]
    result: dict[str, Any] = {"magic": magic.hex()}
    if magic in {MACHO_64_LE, MACHO_64_BE, MACHO_32_LE, MACHO_32_BE}:
        result["kind"] = "mach-o"
        result["bits"] = 64 if magic in {MACHO_64_LE, MACHO_64_BE} else 32
        endian = "<" if magic in {MACHO_64_LE, MACHO_32_LE} else ">"
        cputype = struct.unpack(endian + "I", data[4:8])[0]
        result["cputype"] = f"0x{cputype:08x}"
        result["architecture"] = {
            CPU_TYPE_ARM64: "arm64",
            CPU_TYPE_X86_64: "x86_64",
        }.get(cputype, "unknown")
        return result
    if magic in {FAT_LE, FAT_BE}:
        result["kind"] = "fat-mach-o"
        endian = ">" if magic == FAT_LE else "<"
        result["architecture"] = "multi-architecture"
        if len(data) >= 8:
            result["slice_count"] = struct.unpack(endian + "I", data[4:8])[0]
        return result
    return {"kind": "not-mach-o", "magic": magic.hex()}


def inspect(path: str) -> dict[str, Any]:
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        app_roots = sorted({
            "/".join(PurePosixPath(name).parts[:2])
            for name in names
            if len(PurePosixPath(name).parts) >= 2
            and PurePosixPath(name).parts[0] == "Payload"
            and PurePosixPath(name).parts[1].endswith(".app")
        })
        apps = []
        for app_root in app_roots:
            plist_name = app_root + "/Info.plist"
            info: dict[str, Any] = {}
            if plist_name in archive.namelist():
                try:
                    raw_info = plistlib.loads(archive.read(plist_name))
                    if isinstance(raw_info, dict):
                        for key in ("CFBundleIdentifier", "CFBundleDisplayName", "CFBundleName", "CFBundleShortVersionString", "MinimumOSVersion", "UIDeviceFamily"):
                            if key in raw_info:
                                info[key] = raw_info[key]
                        executable = raw_info.get("CFBundleExecutable")
                        if isinstance(executable, str):
                            executable_name = app_root + "/" + executable
                            if executable_name in archive.namelist():
                                info["executable"] = executable
                                info["macho"] = macho_summary(archive.read(executable_name))
                except (plistlib.InvalidFileException, ValueError, TypeError) as exc:
                    info["plist_error"] = str(exc)
            apps.append({"root": app_root, "info": info})
        return {
            "file": path,
            "zip_entries": len(names),
            "apps": apps,
            "execution": "not-performed",
            "signature": "not-validated-by-prototype",
        }


def main() -> int:
    parser = argparse.ArgumentParser(description="Passively inspect an iOS .ipa bundle")
    parser.add_argument("ipa")
    args = parser.parse_args()
    print(json.dumps(inspect(args.ipa), indent=2, ensure_ascii=False, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
