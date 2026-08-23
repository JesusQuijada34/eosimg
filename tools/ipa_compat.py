#!/usr/bin/env python3
"""Passive IPA compatibility report for EOS.

This tool does not execute, decrypt, resign, patch or bypass any app. It helps
EACR decide whether an authorized test app fits the currently supported surface.
"""
from __future__ import annotations

import argparse
import json
import plistlib
import struct
from pathlib import Path
import zipfile
from pathlib import PurePosixPath
from typing import Any

MACHO64_LE = 0xFEEDFACF
CPU_ARM64 = 0x0100000C
LC_LOAD_DYLIB = {0x0000000C, 0x00000018, 0x80000018}
LC_BUILD_VERSION = 0x00000032
SUPPORTED_FRAMEWORKS = {"Foundation", "CoreFoundation", "UIKit", "QuartzCore"}


def macho_report(data: bytes) -> dict[str, Any]:
    if len(data) < 32:
        return {"kind": "unknown", "compatible": False, "reason": "short-header"}
    magic, cpu, subtype, filetype, ncmds, sizeofcmds, flags, reserved = struct.unpack("<IIIIIIII", data[:32])
    report: dict[str, Any] = {
        "kind": "mach-o-64" if magic == MACHO64_LE else "unknown",
        "cpu": f"0x{cpu:08x}",
        "architecture": "arm64" if cpu == CPU_ARM64 else "unknown",
        "load_commands": ncmds,
        "dylibs": [],
        "platform_command": False,
    }
    if magic != MACHO64_LE:
        report["compatible"] = False
        report["reason"] = "not-little-endian-macho64"
        return report
    offset = 32
    for _ in range(ncmds):
        if offset + 8 > len(data):
            report["reason"] = "truncated-load-command"
            report["compatible"] = False
            return report
        command, command_size = struct.unpack("<II", data[offset:offset + 8])
        if command_size < 8 or offset + command_size > len(data):
            report["reason"] = "invalid-load-command-size"
            report["compatible"] = False
            return report
        command_base = command & 0x7FFFFFFF
        if command_base in LC_LOAD_DYLIB and command_size >= 24:
            name_offset = struct.unpack("<I", data[offset + 8:offset + 12])[0]
            start = offset + name_offset
            end = data.find(b"\0", start, offset + command_size)
            if start >= offset and end >= 0:
                report["dylibs"].append(data[start:end].decode("utf-8", errors="replace"))
        if command_base == LC_BUILD_VERSION:
            report["platform_command"] = True
        offset += command_size
    frameworks = {path.rsplit("/", 1)[-1].split(".", 1)[0] for path in report["dylibs"] if "/Frameworks/" in path}
    report["frameworks"] = sorted(frameworks)
    report["unsupported_frameworks"] = sorted(frameworks - SUPPORTED_FRAMEWORKS)
    report["compatible"] = report["architecture"] == "arm64" and not report["unsupported_frameworks"]
    return report


def inspect(path: Path) -> dict[str, Any]:
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        apps: list[dict[str, Any]] = []
        for name in names:
            parts = PurePosixPath(name).parts
            if len(parts) != 3 or parts[0] != "Payload" or not parts[1].endswith(".app") or parts[2] != "Info.plist":
                continue
            root = "/".join(parts[:2])
            info = plistlib.loads(archive.read(name))
            executable = info.get("CFBundleExecutable") if isinstance(info, dict) else None
            executable_report: dict[str, Any] = {"kind": "missing", "compatible": False}
            if isinstance(executable, str):
                executable_path = root + "/" + executable
                if executable_path in names:
                    executable_report = macho_report(archive.read(executable_path))
            apps.append({
                "bundle": root,
                "bundle_id": info.get("CFBundleIdentifier") if isinstance(info, dict) else None,
                "minimum_os": info.get("MinimumOSVersion") if isinstance(info, dict) else None,
                "executable": executable,
                "macho": executable_report,
            })
        return {"file": str(path), "apps": apps, "mode": "analysis-only", "execution": "not-performed"}


def main() -> int:
    parser = argparse.ArgumentParser(prog="eos-ipa-compat", description="Report passive EOS compatibility for an IPA")
    parser.add_argument("ipa", type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(inspect(args.ipa), ensure_ascii=False, indent=2))
    except (OSError, KeyError, TypeError, ValueError, zipfile.BadZipFile) as exc:
        raise SystemExit(f"eos-ipa-compat error: {exc}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
