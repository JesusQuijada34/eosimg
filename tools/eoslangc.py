#!/usr/bin/env python3
"""EosLang 0.1 compiler to EOS bytecode JSON."""
from __future__ import annotations

import argparse
import json
import re
import shlex
from pathlib import Path
from typing import Any

IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_.-]*$")


class CompileError(ValueError):
    pass


def literal(token: str, line: int) -> Any:
    if token.startswith('"') and token.endswith('"'):
        return token[1:-1]
    if re.fullmatch(r"-?[0-9]+", token):
        return int(token)
    if IDENTIFIER.fullmatch(token):
        return {"ref": token}
    raise CompileError(f"line {line}: invalid literal {token!r}")


def compile_source(text: str) -> dict[str, Any]:
    app_name: str | None = None
    version: str | None = None
    instructions: list[dict[str, Any]] = []
    variables: set[str] = set()
    ended = False
    for line_number, raw_line in enumerate(text.splitlines(), 1):
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        try:
            parts = shlex.split(stripped, comments=True, posix=False)
        except ValueError as exc:
            raise CompileError(f"line {line_number}: {exc}") from exc
        if not parts:
            continue
        command = parts[0]
        if ended:
            raise CompileError(f"line {line_number}: content after end")
        if command == "app" and len(parts) == 2:
            if app_name is not None or not IDENTIFIER.fullmatch(parts[1]):
                raise CompileError(f"line {line_number}: invalid or duplicate app declaration")
            app_name = parts[1]
        elif command == "version" and len(parts) == 2:
            if version is not None:
                raise CompileError(f"line {line_number}: duplicate version declaration")
            version_value = literal(parts[1], line_number)
            if not isinstance(version_value, str):
                raise CompileError(f"line {line_number}: version must be a string")
            version = version_value
        elif command == "let" and len(parts) == 4 and parts[2] == "=":
            if not IDENTIFIER.fullmatch(parts[1]) or parts[1] in variables:
                raise CompileError(f"line {line_number}: invalid or duplicate variable")
            variables.add(parts[1])
            instructions.append({"op": "set", "name": parts[1], "value": literal(parts[3], line_number)})
        elif command == "text" and len(parts) == 2:
            text_value = literal(parts[1], line_number)
            if not isinstance(text_value, str):
                raise CompileError(f"line {line_number}: text must be a string")
            instructions.append({"op": "ui.text", "value": text_value})
        elif command == "print" and len(parts) == 2:
            value = literal(parts[1], line_number)
            if isinstance(value, dict) and value["ref"] not in variables:
                raise CompileError(f"line {line_number}: unknown variable {value['ref']}")
            instructions.append({"op": "print", "value": value})
        elif command == "end" and len(parts) == 1:
            ended = True
        else:
            raise CompileError(f"line {line_number}: unknown or malformed statement")
    if app_name is None or version is None:
        raise CompileError("source must declare app and version")
    if not ended:
        raise CompileError("source must end with 'end'")
    return {
        "bytecode": "EOSBC",
        "bytecode_version": 1,
        "app": app_name,
        "source_api": "elang-0.1",
        "version": version,
        "instructions": instructions,
    }


def main() -> int:
    parser = argparse.ArgumentParser(prog="eoslangc", description="Compile EosLang to EOS bytecode")
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    try:
        bytecode = compile_source(args.source.read_text(encoding="utf-8"))
    except (OSError, CompileError) as exc:
        raise SystemExit(f"eoslangc error: {exc}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(bytecode, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"compiled {args.source} -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
