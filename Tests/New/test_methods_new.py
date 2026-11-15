"""Hand-written methods (Methods_new) read by the class generator (PLAN.md Step 5)."""

import re
from pathlib import Path

import pytest

from pyleecan.definitions import MAIN_DIR
from pyleecan.Generator.ClassGenerator.New.bootstrap_methods import bootstrap_methods
from pyleecan.Generator.ClassGenerator.New.class_generator import (
    _bootstrapped_method_dirs,
    method_source_location,
)

ROOT = Path(MAIN_DIR)


def test_bootstrapped_class_read_from_methods_new():
    method_dir, package = method_source_location(
        str(ROOT / "Classes_new"), "Geometry", "Segment"
    )
    assert Path(method_dir) == ROOT / "Methods_new" / "geometry" / "Segment"
    assert package == ["Methods_new", "geometry", "Segment"]


def test_other_class_read_from_legacy_methods():
    method_dir, package = method_source_location(
        str(ROOT / "Classes_new"), "Machine", "LamSlotWind"
    )
    assert Path(method_dir) == ROOT / "Methods" / "Machine" / "LamSlotWind"
    assert package == ["Methods", "Machine", "LamSlotWind"]


@pytest.mark.parametrize("package", ["Classes_new", "Classes_pydantic"])
def test_no_runtime_import_of_method_sources(package):
    """The methods are inlined: no generated class imports Methods or Methods_new"""
    pattern = re.compile(r"^\s*(from|import)\s+[.\w]*\bMethods(_new)?\b", re.M)
    found = [
        str(path.relative_to(ROOT))
        for path in (ROOT / package).rglob("*.py")
        if "__pycache__" not in path.parts and pattern.search(path.read_text("utf-8"))
    ]
    assert not found


def _fake_package(root):
    """Legacy Methods of a class "Segment" (package Geometry) in root."""
    methods = root / "Methods" / "Geometry" / "Segment"
    methods.mkdir(parents=True)
    (methods / "__init__.py").write_text("class SegmentError(Exception):\n    pass\n")
    (methods / "comp_length.py").write_text("def comp_length(self):\n    return 1\n")
    return {
        "Segment": {"package": "Geometry", "mother": "Line", "methods": ["comp_length"]},
        "Line": {"package": "Geometry", "mother": "", "methods": []},
    }


def test_bootstrap_copies_the_method_modules(tmp_path):
    gen_dict = _fake_package(tmp_path)
    assert bootstrap_methods("Geometry", root=tmp_path, gen_dict=gen_dict) == {
        "Segment": 1
    }
    target = tmp_path / "Methods_new" / "geometry" / "Segment"
    assert (target / "comp_length.py").read_text() == (
        "def comp_length(self):\n    return 1\n"
    )
    # The legacy package __init__ (shared errors) is not copied
    assert "SegmentError" not in (target / "__init__.py").read_text()
    _bootstrapped_method_dirs.cache_clear()


def test_bootstrap_never_overwrites(tmp_path):
    gen_dict = _fake_package(tmp_path)
    bootstrap_methods("Geometry", root=tmp_path, gen_dict=gen_dict)
    edited = tmp_path / "Methods_new" / "geometry" / "Segment" / "comp_length.py"
    edited.write_text("def comp_length(self) -> float:\n    return 1.0\n")
    with pytest.raises(FileExistsError):
        bootstrap_methods("Geometry", root=tmp_path, gen_dict=gen_dict)
    assert "-> float" in edited.read_text()
    _bootstrapped_method_dirs.cache_clear()
