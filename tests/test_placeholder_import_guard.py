from __future__ import annotations

from pathlib import Path
import subprocess
import sys


def test_placeholder_import_guard_allows_staff_key_gate_dependency() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check-civiccore-placeholder-imports.py"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "PLACEHOLDER-IMPORT-CHECK: PASSED" in result.stdout
    assert "civiccore.auth" not in result.stdout


def test_placeholder_import_guard_still_blocks_forbidden_placeholder(tmp_path: Path) -> None:
    source_root = tmp_path / "civicnotice"
    source_root.mkdir()
    (source_root / "bad.py").write_text("from civiccore.search import SearchClient\n", encoding="utf-8")
    script = Path("scripts/check-civiccore-placeholder-imports.py").resolve()
    result = subprocess.run(
        [sys.executable, str(script)],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "civiccore.search" in result.stdout
