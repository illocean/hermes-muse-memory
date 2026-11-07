"""Check shipped-file bytes; trust the Git commit separately from this manifest."""

import hashlib
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    checked = 0
    for line in (root / "SHA256SUMS").read_text(encoding="utf-8").splitlines():
        expected, relative = line.split("  ", 1)
        target = (root / relative).resolve()
        if not target.is_relative_to(root) or not target.is_file():
            raise SystemExit(f"Missing or invalid manifest path: {relative}")
        actual = hashlib.sha256(target.read_bytes()).hexdigest()
        if actual != expected:
            raise SystemExit(f"Checksum mismatch: {relative}")
        checked += 1
    if not checked:
        raise SystemExit("Empty integrity manifest")
    print(f"Integrity check passed: {checked} shipped files")


if __name__ == "__main__":
    main()
