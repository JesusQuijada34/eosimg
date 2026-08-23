#!/usr/bin/env python3
"""Official EOS .eapp prototype: pack, sign, inspect and safe extract.

Container layout:
  magic      8 bytes: b'EAPP\\x00\\x02\\x00\\x00'
  meta_len   uint64 little-endian
  data_len   uint64 little-endian
  metadata   canonical UTF-8 JSON
  payload    gzip-compressed tar archive

The tool never executes package contents. Signatures use Ed25519 from the
widely reviewed `cryptography` package. A public-key trust store is planned
for a future EOS repository client.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import struct
import tarfile
import tempfile
from typing import Any
import re

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

try:
    from eoslangc import compile_source
except ImportError:
    compile_source = None

MAGIC = b"EAPP\x00\x02\x00\x00"
HEADER = struct.Struct("<8sQQ")
MAX_META = 4 * 1024 * 1024
MAX_PAYLOAD = 4 * 1024 * 1024 * 1024
IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_.-]*$")


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def make_payload(source: Path) -> bytes:
    if not source.is_dir():
        raise ValueError(f"source is not a directory: {source}")
    stream = io.BytesIO()
    with tarfile.open(fileobj=stream, mode="w:gz", compresslevel=9) as archive:
        for item in sorted(source.rglob("*")):
            relative = item.relative_to(source)
            if any(part in {".", ".."} for part in relative.parts):
                raise ValueError(f"unsafe source path: {relative}")
            info = archive.gettarinfo(str(item), arcname=str(relative))
            if info.isreg():
                with item.open("rb") as handle:
                    archive.addfile(info, handle)
            else:
                archive.addfile(info)
    return stream.getvalue()


def load_private_key(path: Path) -> Ed25519PrivateKey:
    key = serialization.load_pem_private_key(path.read_bytes(), password=None)
    if not isinstance(key, Ed25519PrivateKey):
        raise ValueError("signing key is not Ed25519")
    return key


def load_public_key(path: Path) -> Ed25519PublicKey:
    key = serialization.load_pem_public_key(path.read_bytes())
    if not isinstance(key, Ed25519PublicKey):
        raise ValueError("trusted key is not Ed25519")
    return key


def unsigned_manifest(args: argparse.Namespace, payload: bytes) -> dict[str, Any]:
    return {
        "format": "eapp",
        "format_version": 2,
        "identity": {
            "bundle_id": args.name,
            "publisher": args.publisher,
        },
        "name": args.name,
        "version": args.version,
        "api": args.api,
        "min_eos": args.min_eos,
        "author": args.author,
        "license": args.license,
        "entrypoint": args.entrypoint,
        "targets": [args.target],
        "icon": args.icon,
        "splash": args.splash,
        "documentation": args.documentation,
        "permissions": sorted(set(args.permission)),
        "dependencies": [],
        "compression": "gzip+tar",
        "payload_sha256": sha256(payload),
        "signature": None,
        "created_by": "eos-eapp/0.2",
    }


def write_package(output: Path, metadata: dict[str, Any], payload: bytes) -> None:
    metadata_raw = canonical_json(metadata)
    if len(metadata_raw) > MAX_META or len(payload) > MAX_PAYLOAD:
        raise ValueError("package exceeds safety limits")
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("wb") as handle:
        handle.write(HEADER.pack(MAGIC, len(metadata_raw), len(payload)))
        handle.write(metadata_raw)
        handle.write(payload)


def validate_yaml_policy(path: Path, schema: str, required_key: str) -> None:
    """Validate the restricted declarative YAML subset used by EOS policies."""
    raw = path.read_text(encoding="utf-8")
    if "\t" in raw or f"schema: {schema}" not in raw:
        raise ValueError(f"invalid {schema} policy: {path}")
    if f"{required_key}:" not in raw:
        raise ValueError(f"missing {required_key} in policy: {path}")
    if any(line.lstrip().startswith(("!", "&", "*", "|", ">")) for line in raw.splitlines()):
        raise ValueError(f"unsupported YAML construct in policy: {path}")


def mf_record(subject: str, digest: str, signature: bytes, key_id: str) -> str:
    return ("MF-Version: 1\nAlgorithm: Ed25519\nKey-ID: " + key_id +
            "\nSubject: " + subject + "\nDigest-SHA256: " + digest +
            "\nSignature-Base64: " + base64.b64encode(signature).decode("ascii") + "\n")


def build_v3_payload(source: Path, manifest: dict[str, Any], args: argparse.Namespace) -> tuple[dict[str, Any], bytes]:
    required = ["policy.permissions", "policy.triggers", "ui.entry", "entrypoint", "signatures.manifest", "signatures.payload"]
    for field in required:
        current: Any = manifest
        for part in field.split("."):
            if not isinstance(current, dict) or part not in current:
                raise ValueError(f"v3 manifest missing {field}")
            current = current[part]
        if not isinstance(current, str):
            raise ValueError(f"v3 manifest field must be a path: {field}")
        if current == manifest.get("entrypoint"):
            source_candidate = source / "src" / (Path(current).stem + ".elang")
            if not (source / current).is_file() and not source_candidate.is_file():
                raise ValueError(f"entrypoint and source are missing: {current}")
        elif not (source / current).is_file() and not current.startswith("signatures/"):
            raise ValueError(f"manifest path is missing: {current}")
    validate_yaml_policy(source / manifest["policy"]["permissions"], "eos-permissions-0.1", "permissions")
    validate_yaml_policy(source / manifest["policy"]["triggers"], "eos-triggers-0.1", "triggers")
    if not (source / manifest["ui"]["entry"]).is_file():
        raise ValueError("v3 UI entry is missing")
    with tempfile.TemporaryDirectory(prefix="eapp-v3-") as temp:
        stage = Path(temp) / "payload"
        shutil.copytree(source, stage)
        entrypoint = stage / manifest["entrypoint"]
        if not entrypoint.is_file():
            if compile_source is None:
                raise ValueError("EosLang compiler is unavailable for v3 package")
            source_entry = stage / "src" / (entrypoint.stem + ".elang")
            if not source_entry.is_file():
                raise ValueError(f"entrypoint and source are missing: {manifest['entrypoint']}")
            entrypoint.parent.mkdir(parents=True, exist_ok=True)
            entrypoint.write_text(json.dumps(compile_source(source_entry.read_text(encoding="utf-8")), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        inner = dict(manifest)
        inner["payload_sha256"] = None
        inner["signature"] = None
        (stage / "manifest.json").write_bytes(canonical_json(inner))
        base_payload = make_payload(stage)
        if not args.signing_key:
            raise ValueError("v3 packages require --signing-key")
        private_key = load_private_key(Path(args.signing_key))
        public_bytes = private_key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        key_id = sha256(public_bytes)[:16]
        mf_signature = private_key.sign(canonical_json(inner) + base_payload)
        payload_signature = private_key.sign(base_payload)
        (stage / "signatures").mkdir(parents=True, exist_ok=True)
        (stage / manifest["signatures"]["manifest"]).write_text(mf_record("manifest.json", sha256(canonical_json(inner)), mf_signature, key_id), encoding="utf-8")
        (stage / manifest["signatures"]["payload"]).write_text(mf_record("payload", sha256(base_payload), payload_signature, key_id), encoding="utf-8")
        payload = make_payload(stage)
    manifest = dict(manifest)
    manifest["payload_sha256"] = sha256(payload)
    manifest["identity"] = dict(manifest["identity"])
    manifest["identity"]["key_id"] = key_id
    unsigned = dict(manifest)
    unsigned["signature"] = None
    unsigned_identity = dict(unsigned["identity"])
    unsigned_identity.pop("key_id", None)
    unsigned["identity"] = unsigned_identity
    manifest["signature"] = {
        "algorithm": "Ed25519",
        "key_id": key_id,
        "public_key": base64.b64encode(public_bytes).decode("ascii"),
        "value": base64.b64encode(private_key.sign(canonical_json(unsigned) + payload)).decode("ascii"),
    }
    return manifest, payload


def build_package(source: Path, output: Path, args: argparse.Namespace) -> None:
    source_manifest = source / "eapp.json"
    if source_manifest.is_file():
        candidate = json.loads(source_manifest.read_text(encoding="utf-8"))
        if candidate.get("format_version") == 3:
            manifest, payload = build_v3_payload(source, candidate, args)
            write_package(output, manifest, payload)
            return
    payload = make_payload(source)
    manifest = unsigned_manifest(args, payload)
    if args.signing_key:
        private_key = load_private_key(Path(args.signing_key))
        public_bytes = private_key.public_key().public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw
        )
        signature = private_key.sign(canonical_json(manifest) + payload)
        manifest["identity"]["key_id"] = sha256(public_bytes)[:16]
        manifest["signature"] = {
            "algorithm": "Ed25519",
            "key_id": manifest["identity"]["key_id"],
            "public_key": base64.b64encode(public_bytes).decode("ascii"),
            "value": base64.b64encode(signature).decode("ascii"),
        }
    write_package(output, manifest, payload)


def read_package(path: Path) -> tuple[dict[str, Any], bytes]:
    with path.open("rb") as handle:
        header = handle.read(HEADER.size)
        if len(header) != HEADER.size:
            raise ValueError("truncated eapp header")
        magic, meta_len, data_len = HEADER.unpack(header)
        if magic != MAGIC:
            raise ValueError("invalid eapp magic/version")
        if meta_len > MAX_META or data_len > MAX_PAYLOAD:
            raise ValueError("eapp exceeds safety limits")
        metadata_raw = handle.read(meta_len)
        payload = handle.read(data_len)
        if len(metadata_raw) != meta_len or len(payload) != data_len:
            raise ValueError("truncated eapp payload")
        if handle.read(1):
            raise ValueError("unexpected trailing bytes")
    try:
        metadata = json.loads(metadata_raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("invalid eapp metadata") from exc
    if not isinstance(metadata, dict) or metadata.get("format") != "eapp":
        raise ValueError("invalid eapp manifest")
    if metadata.get("payload_sha256") != sha256(payload):
        raise ValueError("payload integrity check failed")
    return metadata, payload


def verify_signature(metadata: dict[str, Any], payload: bytes) -> str:
    signature = metadata.get("signature")
    if not signature:
        return "unsigned"
    try:
        public_bytes = base64.b64decode(signature["public_key"], validate=True)
        value = base64.b64decode(signature["value"], validate=True)
        key_id = signature["key_id"]
        if sha256(public_bytes)[:16] != key_id:
            return "invalid-key-id"
        unsigned = dict(metadata)
        unsigned["signature"] = None
        # The key_id is part of identity only after signing; remove it for the
        # exact pre-signature manifest reconstruction.
        identity = dict(unsigned.get("identity", {}))
        identity.pop("key_id", None)
        unsigned["identity"] = identity
        Ed25519PublicKey.from_public_bytes(public_bytes).verify(value, canonical_json(unsigned) + payload)
        return "ed25519-ok"
    except (KeyError, TypeError, ValueError) as exc:
        return f"invalid-signature: {exc}"


def safe_extract(payload: bytes, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    destination_resolved = destination.resolve()
    with tempfile.TemporaryDirectory(prefix="eapp-verify-") as tmp:
        tmp_path = Path(tmp)
        with tarfile.open(fileobj=io.BytesIO(payload), mode="r:gz") as archive:
            members = archive.getmembers()
            for member in members:
                target = (tmp_path / member.name).resolve()
                if target != tmp_path and tmp_path not in target.parents:
                    raise ValueError(f"unsafe archive path: {member.name}")
                if member.issym() or member.islnk():
                    raise ValueError("links are not allowed in eapp payloads")
            archive.extractall(tmp_path)
        for item in tmp_path.iterdir():
            target = (destination_resolved / item.name).resolve()
            if target != destination_resolved and destination_resolved not in target.parents:
                raise ValueError("unsafe extraction destination")
            if target.exists():
                raise ValueError(f"refusing to overwrite: {target}")
            item.rename(target)


def cmd_keygen(args: argparse.Namespace) -> int:
    private_key = Ed25519PrivateKey.generate()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(private_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    ))
    public_key_path = Path(str(args.output) + ".pub.pem")
    public_key_path.write_bytes(private_key.public_key().public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    ))
    public = private_key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    print(json.dumps({"private_key": str(args.output), "public_key": str(public_key_path), "key_id": sha256(public)[:16]}, indent=2))
    return 0


def cmd_pack(args: argparse.Namespace) -> int:
    build_package(Path(args.source), Path(args.output), args)
    print(f"created {args.output}")
    return 0


def cmd_inspect(args: argparse.Namespace) -> int:
    metadata, payload = read_package(Path(args.package))
    print(json.dumps({**metadata, "payload_bytes": len(payload), "integrity": "sha256-ok", "signature_status": verify_signature(metadata, payload)}, indent=2, ensure_ascii=False))
    return 0


def cmd_extract(args: argparse.Namespace) -> int:
    metadata, payload = read_package(Path(args.package))
    status = verify_signature(metadata, payload)
    if status.startswith("invalid-"):
        raise ValueError(f"refusing package with {status}")
    safe_extract(payload, Path(args.destination))
    print(f"extracted {metadata['name']} {metadata['version']} to {args.destination} ({status})")
    return 0


def version_tuple(value: str) -> tuple[int, ...]:
    raw = value.removeprefix(">=").strip()
    parts = raw.split(".")
    if not parts or any(not part.isdigit() for part in parts):
        raise ValueError(f"invalid version: {value}")
    return tuple(int(part) for part in parts)


def cmd_install(args: argparse.Namespace) -> int:
    metadata, payload = read_package(Path(args.package))
    status = verify_signature(metadata, payload)
    if status == "unsigned" and not args.allow_unsigned:
        raise ValueError("unsigned package; pass --allow-unsigned only for local development")
    if status.startswith("invalid-"):
        raise ValueError(f"refusing package with {status}")
    if args.trusted_key:
        signature = metadata.get("signature") or {}
        package_public = base64.b64decode(signature.get("public_key", ""), validate=True)
        trusted_public = load_public_key(Path(args.trusted_key)).public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        if package_public != trusted_public:
            raise ValueError("package signer is not trusted by the supplied repository key")
    required = version_tuple(str(metadata.get("min_eos", ">=0.0.0")))
    current = version_tuple(args.eos_version)
    if current < required:
        raise ValueError(f"EOS {args.eos_version} does not satisfy min_eos {metadata['min_eos']}")
    bundle_id = str(metadata["identity"]["bundle_id"])
    if not IDENTIFIER.fullmatch(bundle_id):
        raise ValueError("invalid bundle identity")
    root = Path(args.root).expanduser().resolve()
    destination = root / "apps" / bundle_id / str(metadata["version"])
    if destination.exists():
        raise ValueError(f"version already installed: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="eapp-install-", dir=str(destination.parent)) as stage:
        stage_path = Path(stage) / "payload"
        safe_extract(payload, stage_path)
        os.replace(stage_path, destination)
    registry_path = root / "registry.json"
    registry: dict[str, Any] = {"format": 1, "apps": []}
    if registry_path.exists():
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
    apps = [entry for entry in registry.get("apps", []) if not (entry.get("bundle_id") == bundle_id and entry.get("version") == metadata["version"])]
    apps.append({"bundle_id": bundle_id, "version": metadata["version"], "path": str(destination), "signature_status": status, "entrypoint": metadata["entrypoint"]})
    registry["apps"] = sorted(apps, key=lambda entry: (entry["bundle_id"], entry["version"]))
    root.mkdir(parents=True, exist_ok=True)
    registry_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"installed {bundle_id} {metadata['version']} at {destination} ({status})")
    return 0


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="eapp", description="Official EOS .eapp package tool")
    sub = root.add_subparsers(dest="command", required=True)
    keygen = sub.add_parser("keygen", help="generate an Ed25519 signing key")
    keygen.add_argument("output", type=Path)
    keygen.set_defaults(func=cmd_keygen)
    pack = sub.add_parser("pack", help="pack a directory")
    pack.add_argument("source")
    pack.add_argument("output")
    pack.add_argument("--name", required=True)
    pack.add_argument("--version", required=True)
    pack.add_argument("--entrypoint", required=True)
    pack.add_argument("--target", default="eos-x86_64")
    pack.add_argument("--publisher", default="Etternhall Community")
    pack.add_argument("--author", default="Unknown")
    pack.add_argument("--license", default="UNLICENSED")
    pack.add_argument("--api", default="elang-0.1")
    pack.add_argument("--min-eos", default=">=0.1.0")
    pack.add_argument("--icon", default=None)
    pack.add_argument("--splash", default=None)
    pack.add_argument("--documentation", default=None)
    pack.add_argument("--permission", action="append", default=[])
    pack.add_argument("--signing-key", default=None)
    pack.set_defaults(func=cmd_pack)
    inspect = sub.add_parser("inspect", help="verify and inspect a package")
    inspect.add_argument("package")
    inspect.set_defaults(func=cmd_inspect)
    extract = sub.add_parser("extract", help="verify and safely extract a package")
    extract.add_argument("package")
    extract.add_argument("destination")
    extract.set_defaults(func=cmd_extract)
    install = sub.add_parser("install", help="verify and install into an EOS prefix")
    install.add_argument("package")
    install.add_argument("--root", default="~/.eos")
    install.add_argument("--eos-version", default="0.1.0")
    install.add_argument("--trusted-key", default=None, help="trusted Ed25519 public key in PEM")
    install.add_argument("--allow-unsigned", action="store_true")
    install.set_defaults(func=cmd_install)
    return root


if __name__ == "__main__":
    arguments = parser().parse_args()
    try:
        raise SystemExit(arguments.func(arguments))
    except ValueError as exc:
        raise SystemExit(f"eapp error: {exc}")
