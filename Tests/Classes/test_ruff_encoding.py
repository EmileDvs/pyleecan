"""Verify Ruff receives generated Unicode source as UTF-8."""

import os
import subprocess
import sys
from pathlib import Path


def test_ruff_formats_unicode_with_non_utf8_default(tmp_path):
    source = (
        "import locale\n"
        "from pyleecan.Generator.ClassGenerator.New.class_generator "
        "import _format_source_with_ruff\n"
        'print("DEFAULT_ENCODING", locale.getencoding(), flush=True)\n'
        'result = _format_source_with_ruff("value = \'\\uff1a\'\\n", "sample.py")\n'
        'assert "\\uff1a" in result\n'
        'print("FORMAT_COMPLETE", flush=True)\n'
    )
    env = os.environ.copy()
    env["PYTHONUTF8"] = "0"
    env["PYTHONIOENCODING"] = "utf-8"
    env["PATH"] = str(Path(sys.executable).parent) + os.pathsep + env.get("PATH", "")
    result = subprocess.run(
        [sys.executable, "-c", source],
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
        timeout=20,
        check=True,
    )
    assert "FORMAT_COMPLETE" in result.stdout
