"""Tests of the legacy functions moved to the classes (moved_functions.py)."""

import ast
import warnings

import pytest

from pyleecan.Generator.ClassGenerator.New.moved_functions import (
    MovedFunction,
    add_moved_methods,
    alias_source,
    method_source,
    redirect_moved_calls,
)

AREA = MovedFunction("MeshSolution", "get_area")
STEP = MovedFunction("VarSimu", "run_multisim_step", static=True)
MOVED = {"MeshSolution.get_area": AREA, "Simulation.VarSimu.run_multisim_step": STEP}

FUNCTION = '''from ..Geometry.tool import tool


def get_area(meshsolution, group_names=None):
    """Area

    Parameters
    ----------
    meshsolution : MeshSolution
        a MeshSolution object
    """
    return tool(meshsolution.get_group(group_names), meshsolution)
'''


def test_add_moved_methods():
    gen_dict = {"MeshSolution": {"methods": ["get_group"]}, "VarSimu": {"methods": []}}
    add_moved_methods(gen_dict, MOVED)
    add_moved_methods(gen_dict, MOVED)  # Idempotent
    assert gen_dict["MeshSolution"]["methods"] == ["get_group", "get_area"]
    assert gen_dict["VarSimu"]["methods"] == ["run_multisim_step"]


def test_method_source_self():
    source = method_source(
        FUNCTION,
        AREA,
        "pyleecan.Functions.MeshSolution",
        "pyleecan.Methods_new.mesh.MeshSolution",
    )
    assert "def get_area(self, group_names=None):" in source
    assert "    self : MeshSolution\n" in source
    assert "return tool(self.get_group(group_names), self)" in source
    # The relative import still targets pyleecan.Functions.Geometry.tool
    assert "from ....Functions.Geometry.tool import tool" in source


def test_method_source_static():
    source = method_source(
        FUNCTION,
        MovedFunction("MeshSolution", "get_area", static=True),
        "pyleecan.Functions.MeshSolution",
        "pyleecan.Methods_new.mesh.MeshSolution",
    )
    assert "@staticmethod\ndef get_area(meshsolution, group_names=None):" in source


def test_redirect_moved_calls_regular():
    source = (
        "import numpy as np\n"
        "from ....Functions.MeshSolution.get_area import get_area\n\n\n"
        "def f(self, g):\n"
        "    a = get_area(self.meshsolution, group_names=g)\n"
        "    b = get_area(self.ms[0])\n"
        "    return get_area(x or y, *g)\n"
    )
    result = redirect_moved_calls(source, "pyleecan.Methods_new.output.OutMag", "OutMag", MOVED)
    assert "get_area import" not in result
    assert "a = self.meshsolution.get_area(group_names=g)" in result
    assert "b = self.ms[0].get_area()" in result
    assert "return (x or y).get_area(*g)" in result
    ast.parse(result)


def test_redirect_moved_calls_static():
    source = (
        "from ....Functions.Simulation.VarSimu.run_multisim_step import run_multisim_step\n\n\n"
        "def run(self):\n"
        "    return run_multisim_step(simu, keepers, True)\n"
    )
    result = redirect_moved_calls(source, "pyleecan.Methods_new.simulation.VarSimu", "VarSimu", MOVED)
    assert "return self.run_multisim_step(simu, keepers, True)" in result
    assert "import" not in result
    with pytest.raises(ValueError, match="outside of its class"):
        redirect_moved_calls(source, "pyleecan.Methods_new.output.OutMag", "OutMag", MOVED)


def test_redirect_moved_calls_static_in_daughter_class():
    """A daughter class calls the static method of its mother class on self."""
    source = (
        "from ....Functions.Simulation.VarSimu.run_multisim_step import run_multisim_step\n\n\n"
        "def get(self):\n"
        "    return run_multisim_step(simu, keepers, True)\n"
    )
    gen_dict = {"VarLoadCurrent": {"mother": "VarLoad"}, "VarLoad": {"mother": "VarSimu"}, "VarSimu": {"mother": ""}}
    result = redirect_moved_calls(
        source, "pyleecan.Methods_new.simulation.VarLoadCurrent", "VarLoadCurrent", MOVED, gen_dict=gen_dict
    )
    assert "return self.run_multisim_step(simu, keepers, True)" in result
    # Without the mother classes, the call is refused
    with pytest.raises(ValueError, match="outside of its class"):
        redirect_moved_calls(source, "pyleecan.Methods_new.simulation.VarLoadCurrent", "VarLoadCurrent", MOVED)


def test_redirect_moved_calls_static_in_static_method():
    """A static method calls a static method on the class, imported in its body."""
    source = (
        "from ....Functions.Simulation.VarSimu.run_multisim_step import run_multisim_step\n\n\n"
        "@staticmethod\n"
        "def helper(simulation):\n"
        '    """Doc"""\n'
        "    value = 1\n"
        "    return run_multisim_step(simulation, value)\n"
    )
    result = redirect_moved_calls(source, "pyleecan.Methods_new.simulation.VarSimu", "VarSimu", MOVED)
    assert (
        '    """Doc"""\n'
        "    from ....Classes.VarSimu import VarSimu\n"
        "    value = 1\n"
        "    return VarSimu.run_multisim_step(simulation, value)\n"
    ) in result
    ast.parse(result)


def test_redirect_moved_calls_unrelated():
    source = "from .get_area import get_area\n\nget_area(x)\n"
    assert redirect_moved_calls(source, "pyleecan.Methods_new.mesh.Mesh", "Mesh", MOVED) == source


def test_alias_regular_warns():
    namespace = {}
    exec(alias_source("MeshSolution.get_area", AREA), namespace)

    class Obj:
        def get_area(self, group_names=None):
            return group_names

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        assert namespace["get_area"](Obj(), group_names="g") == "g"
    assert caught[0].category is DeprecationWarning
    assert "MeshSolution.get_area" in str(caught[0].message)


def test_alias_static_imports_class():
    source = alias_source("Simulation.VarSimu.run_multisim_step", STEP)
    assert "from ....Classes.VarSimu import VarSimu" in source
    assert "return VarSimu.run_multisim_step(*args, **kwargs)" in source
