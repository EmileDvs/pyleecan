"""Tests for normalizing PyVista imports in generated classes."""

import ast
import os
import sys
from copy import deepcopy
from pathlib import Path
from shutil import copy2

import pytest
import pyvista as pv

from pyleecan.definitions import DOC_DIR, MAIN_DIR
from pyleecan.Generator.ClassGenerator.New.class_generator import (
    _apply_numpy_import_style,
    _apply_pyvista_import_style,
    _normalize_method_package_imports,
    generate_class,
)
from pyleecan.Generator.read_fct import read_all


@pytest.fixture
def generator_environment(monkeypatch):
    monkeypatch.setenv(
        "PATH",
        str(Path(sys.executable).parent) + os.pathsep + os.environ.get("PATH", ""),
    )
    return read_all(DOC_DIR)


def test_pyvista_imports_and_references():
    source = (
        "import pyvista as vista\n"
        "from pyvista import Sphere as sphere\n"
        "from pyvista.core.pointset import UnstructuredGrid as Grid\n"
        "def make(mesh: Grid = None):\n"
        "    return vista, sphere, Grid, mesh\n"
        "def shadow(sphere):\n"
        "    return sphere\n"
    )
    transformed = _apply_pyvista_import_style(source)
    assert transformed.count("import pyvista as pv") == 1
    assert "mesh: pv.core.pointset.UnstructuredGrid" in transformed
    namespace = {}
    exec(transformed, namespace)
    assert namespace["make"]() == (pv, pv.Sphere, pv.UnstructuredGrid, None)
    assert namespace["shadow"]("value") == "value"


def test_pyvista_local_guarded_import_stays_local():
    source = (
        "def make():\n"
        "    try:\n"
        "        from pyvista import Sphere\n"
        "    except ImportError:\n"
        "        return None\n"
        "    return Sphere\n"
    )
    transformed = _apply_pyvista_import_style(source)
    assert transformed.startswith("def make():")
    assert "        import pyvista as pv" in transformed
    namespace = {}
    exec(transformed, namespace)
    assert namespace["make"]() is pv.Sphere


@pytest.mark.parametrize(
    "source",
    [
        "from pyvista import Sphere\ndef f(pv):\n    return Sphere, pv\n",
        "from pyvista import Sphere\npv = 1\ndef f():\n    return Sphere, pv\n",
        "from pyvista import Sphere\nSphere = 1\ndef f():\n    return Sphere\n",
        "from pyvista import *\ndef f():\n    return Sphere\n",
        "import os as pv\nfrom pyvista import Sphere\ndef f():\n    return Sphere, pv\n",
        "from pyvista import Sphere\nf = lambda Sphere: Sphere\n",
        "from pyvista import Sphere\ndef f():\n    return [Sphere for Sphere in ()]\n",
        "from pyvista import Sphere\nclass A:\n    Sphere = 1\n    value = Sphere\n",
        "from .pyvista import Sphere\ndef f():\n    return Sphere\n",
    ],
)
def test_pyvista_alias_conflicts_are_left_unchanged(source):
    assert _apply_pyvista_import_style(source) == source


def test_pyvista_method_imports_normalized_before_conflict_checks():
    method, imports = _normalize_method_package_imports(
        "def make(self) -> Grid:\n    return Grid\n",
        [
            ast.parse(
                "from pyvista.core.pointset import UnstructuredGrid as Grid"
            ).body[0]
        ],
        "pyvista",
        "pv",
    )
    assert [ast.unparse(node) for node in imports] == ["import pyvista as pv"]
    assert "-> pv.core.pointset.UnstructuredGrid" in method
    assert "return pv.core.pointset.UnstructuredGrid" in method


def test_numpy_style_still_works():
    source = "from numpy import zeros as z\n\ndef f():\n    return z(2)\n"
    transformed = _apply_numpy_import_style(source)
    assert "import numpy as np" in transformed
    assert "return np.zeros(2)" in transformed


@pytest.mark.parametrize("is_new", [False, True])
def test_generated_meshmat_pyvista_annotation(generator_environment, tmp_path, is_new):
    gen_dict = generator_environment
    gen_dict["MeshMat"] = deepcopy(gen_dict["MeshMat"])
    gen_dict["MeshMat"]["methods"] = ["get_mesh_pv"]
    output = tmp_path / "Classes"
    output.mkdir()
    methods = tmp_path / "Methods" / "Mesh" / "MeshMat"
    methods.mkdir(parents=True)
    copy2(Path(MAIN_DIR) / "Methods" / "Mesh" / "MeshMat" / "get_mesh_pv.py", methods)
    generate_class(
        gen_dict, "MeshMat", str(output), is_new=is_new, class_import_graph={}
    )
    path = output / ("mesh_mat.py" if is_new else "MeshMat.py")
    source = path.read_text(encoding="utf-8")
    assert "import pyvista as pv" in source
    assert "from pyvista.core.pointset import UnstructuredGrid" not in source
    assert "-> pv.core.pointset.UnstructuredGrid:" in source
    assert "pv.read(" in source
