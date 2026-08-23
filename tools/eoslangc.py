#!/usr/bin/env python3
"""EosLang 0.2 compiler to EOS bytecode JSON.

The language stays intentionally safe and explicit: applications compile to
EOSBC instructions and can only reach EOS services through named libraries.
There is no shell, native ELF, eval, or arbitrary filesystem instruction.
"""
from __future__ import annotations

import argparse
import json
import re
import shlex
from pathlib import Path
from typing import Any

IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_.-]*$")
TYPE_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_.-]*$")
FUNCTION = re.compile(r"^fn\s+([A-Za-z_][A-Za-z0-9_]*)\(([^)]*)\)(?:\s*->\s*([A-Za-z_][A-Za-z0-9_.-]*))?\s*$")
IMPORT = re.compile(r"^use\s+([A-Za-z_][A-Za-z0-9_.-]*)(?:\s+as\s+([A-Za-z_][A-Za-z0-9_]*))?\s*$")
STATE = re.compile(r"^(state|let)\s+([A-Za-z_][A-Za-z0-9_]*)(?:\s*:\s*([A-Za-z_][A-Za-z0-9_.-]*))?\s*=\s*(.+)$")
EVENT = re.compile(r"^on\s+([A-Za-z_][A-Za-z0-9_.-]*)\s*=>\s*([A-Za-z_][A-Za-z0-9_]*)\s*$")


class CompileError(ValueError):
    pass


def literal(token: str, line: int) -> Any:
    token = token.strip()
    if len(token) >= 2 and token[0] == '"' and token[-1] == '"':
        return bytes(token[1:-1], "utf-8").decode("unicode_escape")
    if token in {"true", "false"}:
        return token == "true"
    if token == "null":
        return None
    if re.fullmatch(r"-?[0-9]+", token):
        return int(token)
    if re.fullmatch(r"-?[0-9]+\.[0-9]+", token):
        return float(token)
    if IDENTIFIER.fullmatch(token):
        return {"ref": token}
    raise CompileError(f"line {line}: invalid literal {token!r}")


def ensure_ref_known(value: Any, known: set[str], line: int) -> None:
    if isinstance(value, dict) and set(value) == {"ref"} and value["ref"] not in known:
        raise CompileError(f"line {line}: unknown variable {value['ref']}")


def parse_call(raw: str, line: int, known: set[str]) -> dict[str, Any]:
    try:
        parts = shlex.split(raw, comments=True, posix=False)
    except ValueError as exc:
        raise CompileError(f"line {line}: {exc}") from exc
    if len(parts) < 2 or not IDENTIFIER.fullmatch(parts[0]):
        raise CompileError(f"line {line}: call requires a library function")
    function = parts[0]
    # EosLang permite separar argumentos por espacios o por comas, igual que
    # las llamadas habituales de JS/Python; las comas fuera de strings llegan
    # como sufijo de token con shlex(posix=False).
    parts = [part.rstrip(",") for part in parts]
    parts = [part for part in parts if part not in {"", ","}]
    args = [literal(part, line) for part in parts[1:]]
    for value in args:
        ensure_ref_known(value, known, line)
    return {"op": "call", "function": function, "args": args}


def parse_statement(stripped: str, line: int, known: set[str]) -> tuple[dict[str, Any] | None, bool]:
    if stripped == "end":
        return None, True
    state_match = STATE.fullmatch(stripped)
    if state_match:
        keyword, name, declared_type, raw_value = state_match.groups()
        if name in known:
            raise CompileError(f"line {line}: duplicate variable {name}")
        if declared_type and not TYPE_NAME.fullmatch(declared_type):
            raise CompileError(f"line {line}: invalid type")
        value = literal(raw_value, line)
        known.add(name)
        return {"op": "state.set" if keyword == "state" else "set", "name": name, "type": declared_type or "inferred", "value": value}, False
    if stripped.startswith("text "):
        raw = stripped[5:].strip()
        value = literal(raw, line)
        if not isinstance(value, str):
            raise CompileError(f"line {line}: text must be a string")
        return {"op": "ui.text", "value": value}, False
    if stripped.startswith("ui.show "):
        value = literal(stripped[8:].strip(), line)
        if not isinstance(value, str):
            raise CompileError(f"line {line}: ui.show requires a view id")
        return {"op": "ui.show", "view": value}, False
    if stripped.startswith("print "):
        value = literal(stripped[6:].strip(), line)
        ensure_ref_known(value, known, line)
        return {"op": "print", "value": value}, False
    if stripped.startswith("call "):
        return parse_call(stripped[5:].strip(), line, known), False
    if stripped.startswith("return"):
        raw = stripped[6:].strip()
        value = None if not raw else literal(raw, line)
        ensure_ref_known(value, known, line)
        return {"op": "return", "value": value}, False
    raise CompileError(f"line {line}: unknown or malformed statement")


def parse_parameters(raw: str, line: int) -> list[dict[str, str]]:
    if not raw.strip():
        return []
    result: list[dict[str, str]] = []
    for item in raw.split(","):
        bits = item.strip().split(":", 1)
        name = bits[0].strip()
        type_name = bits[1].strip() if len(bits) == 2 else "any"
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name) or not TYPE_NAME.fullmatch(type_name):
            raise CompileError(f"line {line}: invalid function parameter")
        result.append({"name": name, "type": type_name})
    return result


def compile_source(text: str) -> dict[str, Any]:
    app_name: str | None = None
    version: str | None = None
    imports: dict[str, str] = {}
    instructions: list[dict[str, Any]] = []
    functions: dict[str, dict[str, Any]] = {}
    events: list[dict[str, str]] = []
    known: set[str] = set()
    current_function: dict[str, Any] | None = None
    ended = False

    for line_number, raw_line in enumerate(text.splitlines(), 1):
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if ended:
            raise CompileError(f"line {line_number}: content after end")
        if stripped == "endfn":
            if current_function is None:
                raise CompileError(f"line {line_number}: endfn without fn")
            functions[current_function["name"]] = current_function
            current_function = None
            continue
        function_match = FUNCTION.fullmatch(stripped)
        if function_match:
            if current_function is not None:
                raise CompileError(f"line {line_number}: nested functions are not allowed")
            name, raw_params, return_type = function_match.groups()
            if name in functions:
                raise CompileError(f"line {line_number}: duplicate function {name}")
            current_function = {
                "name": name,
                "parameters": parse_parameters(raw_params, line_number),
                "return_type": return_type or "any",
                "instructions": [],
            }
            continue
        import_match = IMPORT.fullmatch(stripped)
        if import_match:
            if current_function is not None:
                raise CompileError(f"line {line_number}: use must be top-level")
            module, alias = import_match.groups()
            imports[alias or module] = module
            continue
        event_match = EVENT.fullmatch(stripped)
        if event_match:
            if current_function is not None:
                raise CompileError(f"line {line_number}: on must be top-level")
            events.append({"event": event_match.group(1), "handler": event_match.group(2)})
            continue
        if stripped.startswith("app ") and current_function is None:
            parts = stripped.split(maxsplit=1)
            if app_name is not None or len(parts) != 2 or not IDENTIFIER.fullmatch(parts[1]):
                raise CompileError(f"line {line_number}: invalid or duplicate app declaration")
            app_name = parts[1]
            continue
        if stripped.startswith("version ") and current_function is None:
            if version is not None:
                raise CompileError(f"line {line_number}: duplicate version declaration")
            value = literal(stripped[8:].strip(), line_number)
            if not isinstance(value, str):
                raise CompileError(f"line {line_number}: version must be a string")
            version = value
            continue
        statement, statement_ends = parse_statement(stripped, line_number, known if current_function is None else {p["name"] for p in current_function["parameters"]} | known)
        if statement_ends:
            ended = True
        elif statement is not None:
            if current_function is None:
                instructions.append(statement)
            else:
                current_function["instructions"].append(statement)

    if current_function is not None:
        raise CompileError("function must end with 'endfn'")
    if app_name is None or version is None:
        raise CompileError("source must declare app and version")
    if not ended:
        raise CompileError("source must end with 'end'")
    missing = [item["handler"] for item in events if item["handler"] not in functions]
    if missing:
        raise CompileError(f"event handler(s) not defined: {', '.join(missing)}")
    return {
        "bytecode": "EOSBC",
        "bytecode_version": 2,
        "app": app_name,
        "source_api": "elang-0.2",
        "version": version,
        "imports": imports,
        "state": sorted(name for name in known if name not in {p["name"] for fn in functions.values() for p in fn["parameters"]}),
        "instructions": instructions,
        "functions": functions,
        "events": events,
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
