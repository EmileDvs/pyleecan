"""Tests for dynamic class imports in generated code."""

import ast
import importlib.util
import os
import sys
from copy import deepcopy
from pathlib import Path

import pytest

from pyleecan.Classes.Magnetics import Magnetics
from pyleecan.Classes.Simu1 import Simu1
from pyleecan.definitions import DOC_DIR
from pyleecan.Functions.Load.import_class import import_class
from pyleecan.Generator.ClassGenerator.class_generator import (
    _replace_dynamic_class_imports,
    generate_class,
)
from pyleecan.Generator.ClassGenerator.init_method_generator import (
    generate_set_class_by_dict,
    generate_set_class_by_dict_dict,
    generate_set_class_by_dict_list,
)
from pyleecan.Generator.read_fct import read_all


@pytest.mark.parametrize(
    "expression",
    [
        'module = __import__("pyleecan.Classes.Magnetics", fromlist=["Magnetics"])\n'
        "    cls = module.Magnetics",
        'module = __import__(PACKAGE_NAME + ".Classes.Magnetics", fromlist=["Magnetics"])\n'
        '    cls = getattr(module, "Magnetics")',
        'name = "Magnetics"\n'
        '    module = __import__("pyleecan.Classes." + name, fromlist=[name])\n'
        "    cls = getattr(module, name)",
    ],
)
def test_recognized_imports_return_the_class(expression):
    source = "def method():\n    " + expression + "\n    return cls\n"
    result, changed = _replace_dynamic_class_imports(source, "pyleecan")
    assert changed
    assert "__import__" not in result
    namespace = {"_pyleecan_import_class": import_class, "PACKAGE_NAME": "pyleecan"}
    exec(result, namespace)
    assert namespace["method"]() is Magnetics


@pytest.mark.parametrize(
    "body",
    [
        'module = __import__("os.path", fromlist=["join"])\n    cls = module.join',
        'module = __import__("pyleecan.Classes.Magnetics", fromlist=["Magnetics"])\n'
        "    cls = module.Magnetics\n    return module",
        'module = __import__("pyleecan.Classes.Magnetics", fromlist=["Magnetics"])\n'
        "    cls = module.Magnetics\n    getattr = lambda *args: None",
        'module = __import__("pyleecan.Classes.Magnetics", fromlist=["Magnetics"]) # comment\n'
        "    cls = module.Magnetics",
    ],
)
def test_unrecognized_or_unsafe_import_is_unchanged(body):
    source = "def method():\n    " + body + "\n"
    assert _replace_dynamic_class_imports(source, "pyleecan") == (source, False)


@pytest.mark.parametrize(
    "generator",
    [
        generate_set_class_by_dict,
        generate_set_class_by_dict_list,
        generate_set_class_by_dict_dict,
    ],
)
def test_constructor_class_imports_use_shared_helper(generator):
    source = generator("item", "Magnetics", ["MagFEMM"])
    assert 'import_class("pyleecan.Classes", class_name, "item")' in source
    assert "__import__" not in source


@pytest.mark.parametrize("is_new", [False, True])
def test_generated_method_uses_import_class(tmp_path, monkeypatch, is_new):
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
        "def comp_axes(self):\n"
        '    module = __import__("pyleecan.Classes.Magnetics", fromlist=["Magnetics"])\n'
        "    cls = module.Magnetics\n"
        "    return cls\n",
        encoding="utf-8",
    )
    generate_class(
        gen_dict, "Magnetics", str(output), is_new=is_new, class_import_graph={}
    )
    path = output / ("magnetics.py" if is_new else "Magnetics.py")
    module = ast.parse(path.read_text(encoding="utf-8"))
    cls = next(
        node
        for node in module.body
        if isinstance(node, ast.ClassDef) and node.name == "Magnetics"
    )
    method = next(
        node
        for node in cls.body
        if isinstance(node, ast.FunctionDef) and node.name == "comp_axes"
    )
    body = ast.unparse(method)
    assert "_pyleecan_import_class('pyleecan.Classes', 'Magnetics')" in body
    assert "__import__" not in body
    namespace = {"_pyleecan_import_class": import_class}
    exec(body, namespace)
    assert namespace["comp_axes"](None) is Magnetics
    assert any(
        isinstance(node, ast.ImportFrom)
        and node.module.endswith("Functions.Load.import_class")
        and any(alias.asname == "_pyleecan_import_class" for alias in node.names)
        for node in module.body
        if isinstance(node, ast.ImportFrom) and node.module
    )


def test_generated_legacy_constructor_loads_subclass(tmp_path, monkeypatch):
    monkeypatch.setenv(
        "PATH",
        str(Path(sys.executable).parent) + os.pathsep + os.environ.get("PATH", ""),
    )
    gen_dict = read_all(DOC_DIR)
    gen_dict["Output"] = deepcopy(gen_dict["Output"])
    gen_dict["Output"]["methods"] = []
    generate_class(gen_dict, "Output", str(tmp_path), class_import_graph={})
    path = tmp_path / "Output.py"
    spec = importlib.util.spec_from_file_location(
        "pyleecan.Classes.test_generated_output", path
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    output = module.Output(simu=Simu1().as_dict())
    assert isinstance(output.simu, Simu1)
