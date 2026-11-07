"""Tests for empty container literals in inlined methods."""

import os
import sys
from copy import deepcopy
from pathlib import Path

import pytest

from pyleecan.definitions import DOC_DIR
from pyleecan.Generator.ClassGenerator.class_generator import (
    _replace_empty_containers,
    generate_class,
)
from pyleecan.Generator.read_fct import read_all


def test_empty_calls_are_replaced_without_altering_other_text():
    source = (
        "def method(self):\n"
        "    text = 'dict() list()'\n"
        "    values = list()  # dict() list()\n"
        "    data = dict(\n"
        "    )\n"
        "    return text, values, data, list((1,)), dict(a=1)\n"
    )
    transformed = _replace_empty_containers(source)
    assert "values = []  # dict() list()" in transformed
    assert "data = {}" in transformed
    assert "'dict() list()'" in transformed
    assert "list((1,)), dict(a=1)" in transformed
    namespace = {}
    exec(transformed, namespace)
    assert namespace["method"](None) == ("dict() list()", [], {}, [1], {"a": 1})


@pytest.mark.parametrize(
    "source",
    [
        "def method(self, list):\n    return list()\n",
        "def method(self):\n    list = lambda: 7\n    return list()\n",
        "def method(self):\n    from custom import dict\n    return dict()\n",
        "def method(self):\n    try:\n        pass\n    except Exception as list:\n        return list()\n",
        "def method(self):\n    return list( # keep\n    )\n",
    ],
)
def test_shadowed_or_commented_calls_are_preserved(source):
    assert _replace_empty_containers(source) == source


def test_module_binding_blocks_rewrite():
    source = "def method(self):\n    return list(), dict()\n"
    assert _replace_empty_containers(source, {"list"}) == (
        "def method(self):\n    return list(), {}\n"
    )


@pytest.mark.parametrize("is_new", [False, True])
def test_generator_rewrites_inlined_methods_only(tmp_path, monkeypatch, is_new):
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
        "    values = list()\n"
        "    data = dict()\n"
        "    return values, data, list((1,))\n",
        encoding="utf-8",
    )
    generate_class(
        gen_dict, "Magnetics", str(output), is_new=is_new, class_import_graph={}
    )
    source = (output / ("magnetics.py" if is_new else "Magnetics.py")).read_text(
        encoding="utf-8"
    )
    assert "values = []" in source
    assert "data = {}" in source
    assert "list((1,))" in source
    if not is_new:
        assert "Magnetics_dict = dict()" in source


@pytest.mark.parametrize("is_new", [False, True])
def test_generator_preserves_shadowed_builtin(tmp_path, monkeypatch, is_new):
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
        "from collections import defaultdict as dict\n"
        "def comp_axes(self):\n"
        "    return dict()\n",
        encoding="utf-8",
    )
    generate_class(
        gen_dict, "Magnetics", str(output), is_new=is_new, class_import_graph={}
    )
    source = (output / ("magnetics.py" if is_new else "Magnetics.py")).read_text(
        encoding="utf-8"
    )
    assert "from collections import defaultdict as dict" in source
    assert "return dict()" in source
