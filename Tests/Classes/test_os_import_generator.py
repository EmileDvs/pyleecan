"""Tests for normalizing os imports in generated classes."""

import ast
import os
import sys
from copy import deepcopy
from pathlib import Path
from shutil import copy2

import pytest

from pyleecan.definitions import DOC_DIR, MAIN_DIR
from pyleecan.Generator.ClassGenerator.class_generator import (
    _apply_os_import_style,
    _normalize_method_package_imports,
    generate_class,
)
from pyleecan.Generator.read_fct import read_all


def test_os_imports_and_references():
    source = (
        "import os as operating_system\n"
        "from os import remove as delete\n"
        "from os.path import join as combine, isdir\n"
        "def make(path=combine('a', 'b')):\n"
        "    return operating_system, delete, combine, isdir, path\n"
        "def shadow(combine):\n"
        "    return combine\n"
    )
    transformed = _apply_os_import_style(source)
    assert transformed.count("import os") == 1
    assert "os.path.join('a', 'b')" in transformed
    namespace = {}
    exec(transformed, namespace)
    assert namespace["make"]() == (
        os,
        os.remove,
        os.path.join,
        os.path.isdir,
        os.path.join("a", "b"),
    )
    assert namespace["shadow"]("value") == "value"


def test_os_guarded_import_stays_local():
    source = (
        "def get_join():\n"
        "    try:\n"
        "        from os.path import join\n"
        "    except ImportError:\n"
        "        return None\n"
        "    return join\n"
    )
    transformed = _apply_os_import_style(source)
    assert transformed.startswith("def get_join():")
    assert "        import os" in transformed
    namespace = {}
    exec(transformed, namespace)
    assert namespace["get_join"]() is os.path.join


@pytest.mark.parametrize(
    "source",
    [
        "from os.path import join\ndef f(os):\n    return join, os\n",
        "from os.path import join\nos = 1\ndef f():\n    return join, os\n",
        "from os.path import join\njoin = 1\ndef f():\n    return join\n",
        "from os import *\ndef f():\n    return getcwd\n",
        "import sys as os\nfrom os.path import join\ndef f():\n    return join, os\n",
        "from os.path import join\nf = lambda join: join\n",
        "from os.path import join\ndef f():\n    return [join for join in ()]\n",
        "from os.path import join\nclass A:\n    join = 1\n    value = join\n",
        "from .os import path\ndef f():\n    return path\n",
        "import os.path as path\ndef f():\n    return path.join('a', 'b')\n",
        "from os.path import join; result = join('a', 'b')\n",
    ],
)
def test_os_alias_conflicts_are_left_unchanged(source):
    assert _apply_os_import_style(source) == source


def test_os_method_imports_normalized_before_conflict_checks():
    method, imports = _normalize_method_package_imports(
        "def make(self):\n    return combine('a', 'b')\n",
        [ast.parse("from os.path import join as combine").body[0]],
        "os",
        "os",
    )
    assert [ast.unparse(node) for node in imports] == ["import os"]
    assert "return os.path.join('a', 'b')" in method


@pytest.mark.parametrize("is_new", [False, True])
def test_generated_meshmat_os_imports(tmp_path, monkeypatch, is_new):
    monkeypatch.setenv(
        "PATH",
        str(Path(sys.executable).parent) + os.pathsep + os.environ.get("PATH", ""),
    )
    gen_dict = read_all(DOC_DIR)
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
    assert "import os\n" in source
    assert "from os import " not in source
    assert "from os.path import " not in source
    assert "os.path.isdir(os.path.dirname(path))" in source
    assert "os.makedirs(os.path.dirname(path))" in source
    assert "os.remove(path)" in source


@pytest.mark.parametrize("is_new", [False, True])
def test_hoisted_os_assignment_keeps_its_binding(tmp_path, monkeypatch, is_new):
    monkeypatch.setenv(
        "PATH",
        str(Path(sys.executable).parent) + os.pathsep + os.environ.get("PATH", ""),
    )
    gen_dict = read_all(DOC_DIR)
    gen_dict["Magnetics"] = deepcopy(gen_dict["Magnetics"])
    gen_dict["Magnetics"]["methods"] = ["comp_axes"]
    output = tmp_path / "Classes"
    output.mkdir()
    methods = tmp_path / "Methods" / "Simulation" / "Magnetics"
    methods.mkdir(parents=True)
    (methods / "comp_axes.py").write_text(
        "from os.path import join\n"
        "LOCATION = join('a', 'b')\n"
        "def comp_axes(self, path=LOCATION):\n"
        "    return path\n",
        encoding="utf-8",
    )
    generate_class(
        gen_dict,
        "Magnetics",
        str(output),
        is_new=is_new,
        class_import_graph={},
    )
    path = output / ("magnetics.py" if is_new else "Magnetics.py")
    source = path.read_text(encoding="utf-8")
    assert "import os" in source
    assert "LOCATION = os.path.join(" in source
    assert "from os.path import join" not in source


@pytest.mark.parametrize("is_new", [False, True])
def test_hoisted_os_assignment_with_another_method(tmp_path, monkeypatch, is_new):
    monkeypatch.setenv(
        "PATH",
        str(Path(sys.executable).parent) + os.pathsep + os.environ.get("PATH", ""),
    )
    gen_dict = read_all(DOC_DIR)
    gen_dict["Magnetics"] = deepcopy(gen_dict["Magnetics"])
    gen_dict["Magnetics"]["methods"] = ["comp_axes", "comp_I_mag"]
    output = tmp_path / "Classes"
    output.mkdir()
    methods = tmp_path / "Methods" / "Simulation" / "Magnetics"
    methods.mkdir(parents=True)
    (methods / "comp_axes.py").write_text(
        "from os.path import join\n"
        "LOCATION = join('a', 'b')\n"
        "def comp_axes(self, path=LOCATION):\n"
        "    return path\n",
        encoding="utf-8",
    )
    (methods / "comp_I_mag.py").write_text(
        "from os.path import join\ndef comp_I_mag(self):\n    return join('c', 'd')\n",
        encoding="utf-8",
    )
    generate_class(
        gen_dict,
        "Magnetics",
        str(output),
        is_new=is_new,
        class_import_graph={},
    )
    source = (output / ("magnetics.py" if is_new else "Magnetics.py")).read_text(
        encoding="utf-8"
    )
    assert "LOCATION = os.path.join(" in source
    assert "return os.path.join(" in source
