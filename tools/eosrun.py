#!/usr/bin/env python3
"""Reference interpreter for EOSBC 1/2.

EOSBC 2 exposes only EOSKit-style calls. It never evaluates source text,
launches a shell, imports native ELF, or accesses the host filesystem directly.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


class RuntimeErrorEOS(ValueError):
    pass


def resolve(value: Any, variables: dict[str, Any]) -> Any:
    if isinstance(value, dict) and set(value) == {"ref"}:
        name = value["ref"]
        if name not in variables:
            raise RuntimeErrorEOS(f"unknown variable {name}")
        return variables[name]
    return value


def safe_call(function: str, args: list[Any], output: list[str]) -> Any:
    allowed_prefixes = ("eos.ui.", "eos.storage.", "eos.events.", "eos.navigation.", "eos.lifecycle.", "ui.", "storage.", "events.", "navigation.", "lifecycle.")
    if not function.startswith(allowed_prefixes):
        raise RuntimeErrorEOS(f"library call is not allowed: {function}")
    canonical = {"ui.": "eos.ui.", "storage.": "eos.storage.", "events.": "eos.events.", "navigation.": "eos.navigation.", "lifecycle.": "eos.lifecycle."}
    for alias, prefix in canonical.items():
        if function.startswith(alias):
            function = prefix + function[len(alias):]
            break
    rendered = ", ".join(str(item) for item in args)
    output.append(f"[eos.call] {function}({rendered})")
    if function == "eos.storage.append":
        return True
    if function == "eos.events.ack":
        return True
    return None


def execute(instructions: list[dict[str, Any]], variables: dict[str, Any], output: list[str]) -> Any:
    for instruction in instructions:
        op = instruction.get("op")
        if op in {"set", "state.set"}:
            variables[instruction["name"]] = resolve(instruction["value"], variables)
        elif op == "ui.text":
            output.append(f"[ui.text] {resolve(instruction['value'], variables)}")
        elif op == "ui.show":
            output.append(f"[ui.show] {instruction['view']}")
        elif op == "print":
            output.append(str(resolve(instruction["value"], variables)))
        elif op == "call":
            safe_call(instruction["function"], [resolve(arg, variables) for arg in instruction.get("args", [])], output)
        elif op == "return":
            return resolve(instruction.get("value"), variables)
        else:
            raise RuntimeErrorEOS(f"unsupported opcode {op!r}")
    return None


def run(program: dict[str, Any], event: str | None = None) -> list[str]:
    if program.get("bytecode") != "EOSBC" or program.get("bytecode_version") not in {1, 2}:
        raise RuntimeErrorEOS("unsupported EOS bytecode")
    variables: dict[str, Any] = {}
    output: list[str] = [f"[eosrun] {program['app']} {program['version']}"]
    execute(program.get("instructions", []), variables, output)
    if program.get("bytecode_version") == 2:
        events = {entry["event"]: entry["handler"] for entry in program.get("events", [])}
        selected = event or ("app.launch" if "app.launch" in events else None)
        if selected:
            handler = events.get(selected)
            if handler is None:
                raise RuntimeErrorEOS(f"unknown event {selected}")
            function = program.get("functions", {}).get(handler)
            if function is None:
                raise RuntimeErrorEOS(f"missing event handler {handler}")
            output.append(f"[event] {selected} -> {handler}")
            execute(function.get("instructions", []), variables, output)
    return output


def main() -> int:
    parser = argparse.ArgumentParser(prog="eosrun", description="Run EOS bytecode")
    parser.add_argument("bytecode", type=Path)
    parser.add_argument("--event", default=None, help="dispatch one declared EOS event")
    args = parser.parse_args()
    try:
        program = json.loads(args.bytecode.read_text(encoding="utf-8"))
        for line in run(program, args.event):
            print(line)
    except (OSError, json.JSONDecodeError, KeyError, TypeError, RuntimeErrorEOS) as exc:
        raise SystemExit(f"eosrun error: {exc}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
