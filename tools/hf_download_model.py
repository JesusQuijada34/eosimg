#!/usr/bin/env python3
"""Download one explicitly selected HF model file at a pinned revision."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import tempfile
from urllib.parse import quote

import requests

ALLOWED_HOST = "huggingface.co"


def main() -> int:
    parser = argparse.ArgumentParser(prog="eos-hf-download")
    parser.add_argument("repo_id")
    parser.add_argument("filename")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--expected-license", default="apache-2.0")
    args = parser.parse_args()
    try:
        if not args.filename.lower().endswith(".gguf"):
            raise ValueError("only GGUF model files are allowed")
        api_url = f"https://{ALLOWED_HOST}/api/models/{quote(args.repo_id, safe='/')}"
        metadata = requests.get(api_url, timeout=30).json()
        revision = metadata.get("sha")
        license_id = metadata.get("cardData", {}).get("license")
        siblings = {item.get("rfilename") for item in metadata.get("siblings", [])}
        if not revision or args.filename not in siblings:
            raise ValueError("file or pinned revision not present in HF metadata")
        if license_id != args.expected_license:
            raise ValueError(f"license mismatch: expected {args.expected_license}, got {license_id}")
        url = f"https://{ALLOWED_HOST}/{args.repo_id}/resolve/{revision}/{quote(args.filename, safe='/')}?download=true"
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=args.output.parent, delete=False) as temp:
            temp_path = Path(temp.name)
            h = hashlib.sha256()
            response = requests.get(url, stream=True, timeout=60)
            response.raise_for_status()
            for block in response.iter_content(chunk_size=1024 * 1024):
                if block:
                    temp.write(block)
                    h.update(block)
        temp_path.replace(args.output)
        result = {
            "repo_id": args.repo_id,
            "filename": args.filename,
            "revision": revision,
            "license": license_id,
            "sha256": h.hexdigest(),
            "size": args.output.stat().st_size,
            "source": url,
            "network": "completed-with-explicit-user-consent",
        }
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        args.manifest.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, KeyError, requests.RequestException, json.JSONDecodeError) as exc:
        print(f"eos-hf-download error: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
