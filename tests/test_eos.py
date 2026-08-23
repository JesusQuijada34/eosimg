from pathlib import Path
import json
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, *args], cwd=ROOT, text=True, capture_output=True, check=True)


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="eos-tests-") as temp:
        work = Path(temp)
        key = work / "key.pem"
        package = work / "hello.eapp"
        prefix = work / "prefix"
        bytecode = work / "hello.eosbc"
        run("tools/eapp.py", "keygen", str(key))
        run("tools/eapp.py", "pack", "tests/demo-app", str(package), "--name", "com.etternhall.demo", "--version", "0.2.0", "--entrypoint", "bin/demo", "--signing-key", str(key))
        inspection = json.loads(run("tools/eapp.py", "inspect", str(package)).stdout)
        assert inspection["signature_status"] == "ed25519-ok"
        tampered = work / "tampered.eapp"
        raw = bytearray(package.read_bytes())
        raw[-1] ^= 0x01
        tampered.write_bytes(raw)
        rejected = subprocess.run([sys.executable, "tools/eapp.py", "inspect", str(tampered)], cwd=ROOT, text=True, capture_output=True)
        assert rejected.returncode != 0
        run("tools/eapp.py", "install", str(package), "--root", str(prefix))
        assert (prefix / "registry.json").exists()
        run("tools/eoslangc.py", "tests/hello.elang", str(bytecode))
        output = run("tools/eosrun.py", str(bytecode)).stdout
        assert "Hola desde EOS" in output
        assert "Etternhall" in output
    print("EOS_TESTS=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
