"""Tests of the fixes of the legacy method bugs (legacy_fixes.py)."""

import ast
import tokenize
from pathlib import Path

import pytest

from pyleecan.definitions import DOC_DIR, MAIN_DIR
from pyleecan.Generator.ClassGenerator.New.legacy_fixes import (
    LEGACY_FIXES,
    LegacyFix,
    LegacyFixError,
    apply_fixes,
    apply_legacy_fixes,
)
from pyleecan.Generator.read_fct import read_all

SOURCE = """def f(x):
    raise ()  # TODO
    return g(x, n=2)
"""


def test_apply_fixes():
    fixes = (
        LegacyFix("g(x, n=2)", "g(x)"),
        LegacyFix("raise ()  # TODO", "raise ValueError()"),
    )
    assert (
        apply_fixes(SOURCE, fixes)
        == "def f(x):\n    raise ValueError()\n    return g(x)\n"
    )


def test_apply_fixes_count():
    source = SOURCE + SOURCE.replace("def f", "def h")
    fixed = apply_fixes(source, (LegacyFix("n=2", "n=3", count=2),))
    assert fixed.count("n=3") == 2
    with pytest.raises(LegacyFixError, match="found 2 times instead of 1"):
        apply_fixes(source, (LegacyFix("n=2", "n=3"),))


def test_apply_fixes_legacy_changed():
    """A legacy change on a fixed line stops the generation"""
    with pytest.raises(LegacyFixError, match="mod: legacy text found 0 times"):
        apply_fixes(SOURCE, (LegacyFix("g(x, n=3)", "g(x)"),), "mod")


def test_apply_legacy_fixes(tmp_path):
    module = tmp_path / "geometry" / "Segment" / "sub" / "f.py"
    module.parent.mkdir(parents=True)
    module.write_bytes(SOURCE.replace("\n", "\r\n").encode("utf-8"))
    fixes = {
        ("Segment", "sub/f.py"): (LegacyFix("g(x, n=2)", "g(x)"),),
        ("Arc1", "f.py"): (LegacyFix("x", "y"),),  # Class not generated
    }
    fixed = apply_legacy_fixes(tmp_path, {"Segment": "geometry"}, fixes)
    assert fixed == [module]
    assert module.read_bytes() == SOURCE.replace("g(x, n=2)", "g(x)").encode("utf-8")


@pytest.mark.parametrize("key", sorted(LEGACY_FIXES), ids="/".join)
def test_legacy_fixes_apply(key):
    """Each fix applies to the current legacy module and gives valid Python"""
    class_name, module = key
    gen_dict = _gen_dict()
    path = Path(MAIN_DIR, "Methods", *gen_dict[class_name]["package"].split(".")) / class_name / module
    if not path.exists():  # Function moved to the class (moved_functions.py)
        from pyleecan.Generator.ClassGenerator.New.moved_functions import all_moved_targets

        legacy_module = next(
            legacy
            for legacy, target in all_moved_targets()
            if target.class_name == class_name and module == target.implementation + ".py"
        )
        path = Path(MAIN_DIR, "Functions", *legacy_module.split(".")).with_suffix(".py")
    with tokenize.open(path) as source_file:
        source = source_file.read()
    fixed = apply_fixes(source, LEGACY_FIXES[key], "/".join(key))
    assert fixed != source
    ast.parse(fixed)


_GEN_DICT = {}


def _gen_dict():
    if not _GEN_DICT:
        _GEN_DICT.update(read_all(DOC_DIR))
    return _GEN_DICT
