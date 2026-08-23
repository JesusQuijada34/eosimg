#!/usr/bin/env python3
"""Reference interpreter for the deliberately small EosLang bytecode."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def resolve(value: Any, variables: dict[str, Any]) -> Any:
    if isinstance(value, dict) and set(value) == {"ref"}:
        name = value["ref"]
        if name not in variables:
            raise ValueError(f"unknown variable {name}")
        return variables[name]
    return value


def run(program: dict[str, Any]) -> list[str]:
    if program.get("bytecode") != "EOSBC" or program.get("bytecode_version") != 1:
        raise ValueError("unsupported EOS bytecode")
    variables: dict[str, Any] = {}
    output: list[str] = [f"[eosrun] {program['app']} {program['version']}"]
    for instruction in program.get("instructions", []):
        op = instruction.get("op")
        if op == "set":
            variables[instruction["name"]] = resolve(instruction["value"], variables)
        elif op == "ui.text":
            output.append(f"[ui.text] {instruction['value']}")
        elif op == "print":
            output.append(str(resolve(instruction["value"], variables)))
        else:
            raise ValueError(f"unsupported opcode {op!r}")
    return output


def main() -> int:
    parser = argparse.ArgumentParser(prog="eosrun", description="Run EOS bytecode")
    parser.add_argument("bytecode", type=Path)
    args = parser.parse_args()
    try:
        program = json.loads(args.bytecode.read_text(encoding="utf-8"))
        for line in run(program):
            print(line)
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        raise SystemExit(f"eosrun error: {exc}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
