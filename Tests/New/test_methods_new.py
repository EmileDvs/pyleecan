"""Methods_new: written by the method generator, read by the class generator."""

import ast
import re
from pathlib import Path

import pytest

from pyleecan.definitions import DOC_DIR, MAIN_DIR
from pyleecan.Generator.ClassGenerator.New.class_generator import (
    _bootstrapped_method_dirs,
    _legacy_methods_module,
    _methods_new_maps,
    method_source_location,
)
from pyleecan.Generator.ClassGenerator.New.generate_methods_new import (
    generate_methods,
    modernize_method_source,
)
from pyleecan.Generator.read_fct import read_all

ROOT = Path(MAIN_DIR)


def test_classes_read_from_methods_new():
    method_dir, package = method_source_location(
        str(ROOT / "Classes_new"), "Simulation", "MagFEMM"
    )
    assert Path(method_dir) == ROOT / "Methods_new" / "magnetics" / "MagFEMM"
    assert package == ["Methods_new", "magnetics", "MagFEMM"]


def test_every_class_with_methods_is_in_methods_new():
    gen_dict = read_all(DOC_DIR)
    for name, info in gen_dict.items():
        legacy = ROOT.joinpath("Methods", *info["package"].split("."), name)
        if legacy.is_dir():
            assert name in _bootstrapped_method_dirs(str(ROOT)), name


def test_methods_new_is_self_contained():
    """No module of Methods_new imports the legacy Methods"""
    pattern = re.compile(r"^\s*from\s+(\.+|pyleecan\.)Methods\.", re.M)
    found = [
        str(path.relative_to(ROOT))
        for path in (ROOT / "Methods_new").rglob("*.py")
        if pattern.search(path.read_text("utf-8"))
    ]
    assert not found


def test_legacy_names_for_the_tables():
    assert _legacy_methods_module("Methods_new.machine") == "Methods.Machine"
    assert (
        _legacy_methods_module("Methods_new.magnetics.MagFEMM.comp_flux")
        == "Methods.Simulation.MagFEMM.comp_flux"
    )
    assert _legacy_methods_module("Functions_new.x") == "Functions_new.x"


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


def _fake_tree(root):
    """Legacy Methods of two classes of the Geometry package in root."""
    for name in ("Segment", "Circle"):
        folder = root / "Methods" / "Geometry" / name
        folder.mkdir(parents=True)
        (folder / "__init__.py").write_text(f"class {name}Error(Exception):\n    pass\n")
    (root / "Methods" / "Geometry" / "__init__.py").write_text("NB = 2\n")
    (root / "Methods" / "Geometry" / "Segment" / "comp_length.py").write_text(
        "from ....Methods.Geometry.Circle import CircleError\n"
        "from ....Methods.Geometry import NB\n"
        "from . import SegmentError\n"
        "\n\ndef comp_length(self):\n    return NB\n"
    )
    (root / "Classes_new").mkdir()
    return {
        "Segment": {
            "package": "Geometry",
            "mother": "",
            "methods": ["comp_length"],
            "properties": [],
            "constants": [],
        },
        "Circle": {
            "package": "Geometry",
            "mother": "",
            "methods": [],
            "properties": [],
            "constants": [],
        },
    }


def test_generate_methods(tmp_path):
    gen_dict = _fake_tree(tmp_path)
    try:
        assert generate_methods(root=tmp_path, gen_dict=gen_dict) == {
            "Circle": 0,
            "Segment": 1,
        }
        target = tmp_path / "Methods_new" / "geometry"
        # Package and class __init__ (errors, constants) copied
        assert (target / "__init__.py").read_text() == "NB = 2\n"
        assert "SegmentError" in (target / "Segment" / "__init__.py").read_text()
        # Imports of the legacy Methods redirected to Methods_new
        assert (target / "Segment" / "comp_length.py").read_text().startswith(
            "from ..Circle import CircleError\n"
            "from .. import NB\n"
            "from . import SegmentError\n"
        )
    finally:
        _bootstrapped_method_dirs.cache_clear()
        _methods_new_maps.cache_clear()


def test_frozen_package_is_kept(tmp_path):
    gen_dict = _fake_tree(tmp_path)
    try:
        generate_methods(root=tmp_path, gen_dict=gen_dict)
        edited = tmp_path / "Methods_new" / "geometry" / "Segment" / "comp_length.py"
        edited.write_text("def comp_length(self) -> int:\n    return 2\n")
        generate_methods(root=tmp_path, gen_dict=gen_dict, frozen={"geometry"})
        assert "-> int" in edited.read_text()
        generate_methods(root=tmp_path, gen_dict=gen_dict)
        assert "-> int" not in edited.read_text()
    finally:
        _bootstrapped_method_dirs.cache_clear()
        _methods_new_maps.cache_clear()


def test_modernize_is_idempotent():
    path = ROOT / "Methods_new" / "geometry" / "Segment" / "translate.py"
    source = path.read_text(encoding="utf-8")
    package = "pyleecan.Methods_new.geometry.Segment"
    assert modernize_method_source(source, package, str(ROOT / "Classes_new")) == source


def test_new_names():
    from pyleecan.Generator.ClassGenerator.New.modernize import modernize_names
    from pyleecan.Generator.ClassGenerator.New.source_names import (
        name_maps,
        to_legacy_names,
    )

    package = "pyleecan.Methods_new.geometry.Segment"
    legacy = (
        "from ....Classes.Segment import Segment\n"
        "from ....Classes.Norm_ref import Norm_ref\n"
        "from ....Classes._check import check_var\n"
        "from ....Functions.FEMM.comp_FEMM_dict import comp_FEMM_dict\n"
        "from ....Functions.FEMM import comp_FEMM_dict as femm\n"
        "from pyleecan.Functions.init_fig import init_fig\n"
    )
    new = (
        "from ....Classes_new.geometry.segment import Segment\n"
        "from ....Classes_new.scidatatool.norm_ref import NormRef as Norm_ref\n"
        "from ....classes_common.check import check_var\n"  # Shared support
        "from ....Functions_new.FEMM.comp_femm_dict import comp_FEMM_dict\n"
        "from ....Functions_new.FEMM import comp_femm_dict as femm\n"
        "from ....Functions_new.init_fig import init_fig\n"  # Made relative
    )
    modernized = modernize_names(legacy, package, name_maps().gen_dict, "Segment")
    assert ast.dump(ast.parse(modernized)) == ast.dump(ast.parse(new))
    # Back to the legacy names (the relative form is kept)
    back = to_legacy_names(modernized, package).splitlines()
    expected = legacy.splitlines()
    expected[2] = "from ....classes_common.check import check_var"  # Not legacy
    expected[5] = "from ....Functions.init_fig import init_fig"
    assert back == expected


def test_methods_new_imports():
    """Every module of Methods_new can be imported (and type-checked)"""
    import importlib

    for path in sorted((ROOT / "Methods_new").rglob("*.py")):
        parts = list(path.relative_to(ROOT / "Methods_new").with_suffix("").parts)
        if parts[-1] == "__init__":
            parts = parts[:-1]
        importlib.import_module(".".join(["pyleecan", "Methods_new", *parts]))


@pytest.mark.parametrize(
    "source, expected",
    [
        ("# -*- coding: utf-8 -*-\n\nimport os\n", "import os\n"),
        ("#!/usr/bin/env python\n# -*-- coding: utf-8 -*\nx = 1\n", "#!/usr/bin/env python\nx = 1\n"),
        ("# -*- coding: latin-1 -*-\nx = 1\n", "# -*- coding: latin-1 -*-\nx = 1\n"),
        ("x = 1\n\n# coding: utf-8\n", "x = 1\n\n# coding: utf-8\n"),  # Not a declaration
    ],
)
def test_remove_coding_declaration(source, expected):
    from pyleecan.Generator.ClassGenerator.New.modernize import remove_coding_declaration

    assert remove_coding_declaration(source) == expected
