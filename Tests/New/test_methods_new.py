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


@pytest.mark.parametrize(
    "source, expected",
    [
        (  # Python 3 branch kept
            "import sys\n\nif sys.version_info > (3, 0):\n    from io import StringIO\nelse:\n"
            "    from StringIO import StringIO\n\nx = 1\n",
            "import sys\n\nfrom io import StringIO\n\nx = 1\n",
        ),
        (  # Python 2 test: the else branch is kept
            "if sys.version_info < (3,):\n    a = 2\nelse:\n    a = 3\n    b = [\n        1,\n    ]\n",
            "a = 3\nb = [\n    1,\n]\n",
        ),
        (  # No else: nothing left
            "if sys.version_info < (3, 0):\n    a = 2\nx = 1\n",
            "x = 1\n",
        ),
        (  # Recent version tests are kept
            "if sys.version_info >= (3, 11):\n    import tomllib\n",
            "if sys.version_info >= (3, 11):\n    import tomllib\n",
        ),
    ],
)
def test_remove_python2_branches(source, expected):
    from pyleecan.Generator.ClassGenerator.New.modernize import remove_python2_branches

    assert remove_python2_branches(source) == expected
    assert remove_python2_branches(expected) == expected  # Idempotent


def test_remove_sibling_helper_imports(tmp_path):
    """A helper imported from another method module of the class is not imported."""
    from pyleecan.Generator.ClassGenerator.New.class_generator import _remove_sibling_helper_imports

    (tmp_path / "comp_coeff.py").write_text(
        "@staticmethod\ndef comp_loss_val(x):\n    return x\n\n\n"
        "def other(x):\n    return x\n\n\n"
        "def comp_coeff(self):\n    return comp_loss_val(1)\n",
        encoding="utf-8",
    )
    source = (
        "import numpy as np\n"
        "from .comp_coeff import comp_loss_val, other, comp_coeff\n\n\n"
        "def plot_fitting(self):\n    return comp_loss_val(2)\n"
    )
    result, names = _remove_sibling_helper_imports(source, ast.parse(source), str(tmp_path), "plot_fitting")
    assert names == {"comp_loss_val", "other"}
    # The method of the sibling module is not a helper: its import is kept
    assert "from .comp_coeff import comp_coeff\n" in result
    assert "comp_loss_val, other" not in result
    # Unknown module: unchanged
    unknown = "from .missing import helper\n"
    assert _remove_sibling_helper_imports(unknown, ast.parse(unknown), str(tmp_path), "plot_fitting") == (unknown, set())


@pytest.mark.parametrize("package", ["Classes_new", "Classes_pydantic"])
def test_static_method_calls_its_helpers_on_the_class(package):
    """A helper of a static method module is called on the class (no self)."""
    import importlib

    module = importlib.import_module(f"pyleecan.{package}.optimization.opti_gen_alg_nsga_2_deap")
    tree = ast.parse(Path(module.__file__).read_text(encoding="utf-8"))
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "OptiGenAlgNsga2Deap")
    method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "tournamentDCD")
    source = ast.unparse(method)
    assert "OptiGenAlgNsga2Deap.choseDCD(" in source
    assert "self." not in source


@pytest.mark.parametrize("package", ["Classes_new", "Classes_pydantic"])
def test_static_method_reads_hoisted_constants_on_the_class(package):
    """A module constant of a static method module is read on the class."""
    import importlib

    module = importlib.import_module(f"pyleecan.{package}.machine.winding")
    tree = ast.parse(Path(module.__file__).read_text(encoding="utf-8"))
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "Winding")
    method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "find_wind_phase_color")
    source = ast.unparse(method)
    assert "Winding.PHASE_COLORS[" in source
    assert "label.PHASE_COLORS" not in source
    color, sign = module.Winding.find_wind_phase_color(label="Stator-0_Winding_R0-T0-S0", wind_mat=None)
    assert color == module.Winding.PHASE_COLORS[0] and sign is None


def test_local_package_import_removed_with_module_import():
    """A local numpy import would make np local to the whole function
    (UnboundLocalError before it): removed when the module imports numpy."""
    from pyleecan.Generator.ClassGenerator.New.modernize import apply_import_styles

    source = '''from numpy import abs as np_abs, pi


def f(x, is_plot=False):
    y = np_abs(x) * pi
    if is_plot:
        from numpy import squeeze, argmax
        z = argmax(squeeze(y))
    if x:
        from numpy import cos
    return y
'''
    result = apply_import_styles(source)
    assert result.count("import numpy as np") == 1
    assert "        z = np.argmax(np.squeeze(y))\n" in result
    assert "    if x:\n        pass\n" in result
    namespace = {}
    exec(compile(result, "<test>", "exec"), namespace)
    assert namespace["f"](-2.0, is_plot=True) > 0  # No UnboundLocalError
