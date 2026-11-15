"""Sub-packages of the generated classes (see PLAN.md, "Class sub-packages")."""

from collections import Counter
from keyword import iskeyword
from pathlib import Path

import pytest

from pyleecan.Classes_new._import import class_module_name, import_class, module_path
from pyleecan.definitions import DOC_DIR, MAIN_DIR
from pyleecan.Generator.ClassGenerator.New.class_generator import (
    _apply_import_style,
    class_module_paths,
    class_subpackage,
    generated_module_paths,
    relocate_class_imports,
)
from pyleecan.Generator.read_fct import read_all

GEN_DICT = read_all(DOC_DIR)
CLASS_DIR = Path(MAIN_DIR) / "Classes_new"


def test_subpackage_class_counts():
    """Classes per sub-package, as documented in PLAN.md"""
    counts = Counter(class_subpackage(name, GEN_DICT) for name in GEN_DICT)
    assert counts == {
        "converter": 6,
        "electrical": 8,
        "elmer": 5,
        "force": 3,
        "geometry": 12,
        "gui_option": 2,
        "import_data": 14,
        "loss": 10,
        "machine": 49,
        "magnetics": 3,
        "material": 11,
        "mesh": 22,
        "optimization": 11,
        "output": 17,
        "post": 5,
        "scidatatool": 16,
        "simulation": 25,
        "slot": 59,
        "structural": 3,
    }


@pytest.mark.parametrize(
    "class_name, subpackage",
    [
        ("Segment", "geometry"),
        ("ImportMatrix", "import_data"),  # import is a Python keyword
        ("GUIOption", "gui_option"),  # package "GUIOption" in its CSV
        ("Unit", "gui_option"),  # package "GUI_Option" in its CSV
        ("Electrical", "electrical"),
        ("EEC_PMSM", "electrical"),  # child of EEC
        ("ElecLUTdq", "electrical"),  # child of Electrical
        ("DriveWave", "electrical"),  # child of Drive
        ("MagFEMM", "magnetics"),
        ("ForceMT", "force"),
        ("StructElmer", "structural"),
        ("Mode", "structural"),  # mother SolutionMat is in mesh
        ("SolutionMat", "mesh"),
        ("OutMag", "output"),  # outputs stay in output
        ("Simu1", "simulation"),
        ("InputCurrent", "simulation"),
    ],
)
def test_class_subpackage(class_name, subpackage):
    assert class_subpackage(class_name, GEN_DICT) == subpackage


def test_subpackage_names():
    """Lowercase identifiers, not keywords, not private"""
    for name in {class_subpackage(name, GEN_DICT) for name in GEN_DICT}:
        assert name.isidentifier() and name == name.lower()
        assert not iskeyword(name) and not name.startswith("_")


def test_relocate_class_imports():
    module_paths = {"arc_1": "geometry.arc_1", "lam_slot": "machine.lam_slot"}
    source = (
        "from pyleecan.Classes_new.arc_1 import Arc1\n"
        "from pyleecan.Classes_new._error import CheckTypeError\n"
        "from pyleecan.Classes_new._swat_em import datamodel\n"
        "from pyleecan.Functions_new.init_fig import init_fig\n"
        "from pyleecan.Classes_new.arc_10 import Arc10\n"  # unknown module
        "import pyleecan.Classes_new.lam_slot as lam_slot\n"
        "\n"
        "\n"
        "def f():\n"
        "    from pyleecan.Classes_new.lam_slot import LamSlot\n"
        "\n"
        "    return import_module('pyleecan.Classes_new.arc_1')\n"
    )
    expected = (
        "from pyleecan.Classes_new.geometry.arc_1 import Arc1\n"
        "from pyleecan.Classes_new._error import CheckTypeError\n"
        "from pyleecan.Classes_new._swat_em import datamodel\n"
        "from pyleecan.Functions_new.init_fig import init_fig\n"
        "from pyleecan.Classes_new.arc_10 import Arc10\n"
        "import pyleecan.Classes_new.machine.lam_slot as lam_slot\n"
        "\n"
        "\n"
        "def f():\n"
        "    from pyleecan.Classes_new.machine.lam_slot import LamSlot\n"
        "\n"
        "    return import_module('pyleecan.Classes_new.geometry.arc_1')\n"
    )
    assert (
        relocate_class_imports(source, "pyleecan", "Classes_new", module_paths)
        == expected
    )
    # Relative imports are kept (apply the absolute style first)
    assert relocate_class_imports(
        "from .arc_1 import Arc1\n", "pyleecan", "Classes_new", module_paths
    ) == ("from .arc_1 import Arc1\n")


def test_relocate_unaliased_import_raises():
    with pytest.raises(ValueError):
        relocate_class_imports(
            "import pyleecan.Classes_new.arc_1\n",
            "pyleecan",
            "Classes_new",
            {"arc_1": "geometry.arc_1"},
        )


def test_relative_style_in_subpackage():
    """Relative imports from a sub-package module"""
    source = (
        "from pyleecan.Classes_new.geometry.line import Line\n"
        "from pyleecan.Classes_new.machine.lam_slot import LamSlot\n"
        "from pyleecan.Classes_new._error import CheckTypeError\n"
        "from pyleecan.Functions_new.init_fig import init_fig\n"
        "from pyleecan.definitions import config_dict\n"
    )
    expected = (
        "from .line import Line\n"
        "from ..machine.lam_slot import LamSlot\n"
        "from .._error import CheckTypeError\n"
        "from ...Functions_new.init_fig import init_fig\n"
        "from ...definitions import config_dict\n"
    )
    styled = _apply_import_style(
        source, "pyleecan", "relative", "Classes_new.geometry"
    )
    assert styled == expected
    # And back to absolute
    assert (
        _apply_import_style(styled, "pyleecan", "absolute", "Classes_new.geometry")
        == source
    )


def test_generated_module_paths(tmp_path):
    (tmp_path / "geometry").mkdir()
    (tmp_path / "geometry" / "__init__.py").write_text("")
    (tmp_path / "geometry" / "arc_1.py").write_text("")
    (tmp_path / "geometry" / "_private.py").write_text("")
    (tmp_path / "_swat_em").mkdir()  # vendored: not a class sub-package
    (tmp_path / "_swat_em" / "__init__.py").write_text("")
    (tmp_path / "_swat_em" / "datamodel.py").write_text("")
    (tmp_path / "no_init").mkdir()  # not a package
    (tmp_path / "no_init" / "x.py").write_text("")
    (tmp_path / "_error.py").write_text("")
    assert generated_module_paths(tmp_path) == {"arc_1": "geometry.arc_1"}


def test_generated_tree_matches_rule():
    """Classes_new holds every class in the sub-package given by the rule"""
    generated_module_paths.cache_clear()
    assert generated_module_paths(CLASS_DIR) == class_module_paths(GEN_DICT)
    # No class module left at the root of Classes_new
    assert not [
        path.name
        for path in CLASS_DIR.glob("*.py")
        if not path.name.startswith("_")
    ]


@pytest.mark.parametrize("class_name", sorted(GEN_DICT))
def test_runtime_lookup(class_name):
    """import_class finds every class in its sub-package"""
    cls = import_class(class_name)
    expected = class_module_paths(GEN_DICT)[class_module_name(class_name)]
    assert module_path(class_module_name(class_name)) == expected
    assert cls.__module__ == f"pyleecan.Classes_new.{expected}"
