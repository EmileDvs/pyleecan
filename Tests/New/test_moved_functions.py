"""Tests of the legacy functions moved to the classes (moved_functions.py)."""

import ast
import warnings

import pytest

from pyleecan.Generator.ClassGenerator.New.moved_functions import (
    MovedFunction,
    add_moved_methods,
    alias_source,
    bound_method_source,
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
    # In another class: called on the class, imported in the function
    result = redirect_moved_calls(source, "pyleecan.Methods_new.output.OutMag", "OutMag", MOVED)
    assert (
        "    from ....Classes.VarSimu import VarSimu\n"
        "    return VarSimu.run_multisim_step(simu, keepers, True)\n"
    ) in result


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
    # Without the mother classes: called on the class
    result = redirect_moved_calls(source, "pyleecan.Methods_new.simulation.VarLoadCurrent", "VarLoadCurrent", MOVED)
    assert "return VarSimu.run_multisim_step(simu, keepers, True)" in result


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


MODULE_TWO = '''"""Winding matrix operations"""

from numpy import zeros


def reverse_wind_mat(wind_mat):
    """Reverse"""
    return wind_mat[::-1]


def reverse_layer(wind_mat):
    """Reverse the layers, through reverse_wind_mat"""
    return reverse_wind_mat(wind_mat) + zeros(1)
'''
TWO = {
    "Winding.reverse_wind_mat": (
        MovedFunction("Winding", "reverse_wind_mat", static=True),
        MovedFunction("Winding", "reverse_layer", static=True),
    )
}


def test_several_functions_in_one_module():
    """Each moved function of a module gets its own method module."""
    package = "pyleecan.Methods_new.machine.Winding"
    first, second = TWO["Winding.reverse_wind_mat"]
    alone = method_source(
        MODULE_TWO, first, "pyleecan.Functions.Winding", package, siblings=("reverse_wind_mat", ["reverse_layer"])
    )
    assert "def reverse_layer" not in alone
    assert "import reverse_layer" not in alone  # Not used
    assert "@staticmethod\ndef reverse_wind_mat(wind_mat):" in alone
    other = method_source(
        MODULE_TWO, second, "pyleecan.Functions.Winding", package, siblings=("reverse_wind_mat", ["reverse_wind_mat"])
    )
    assert "def reverse_wind_mat" not in other
    # The sibling is imported from the legacy module, then called on the class
    assert "from ....Functions.Winding.reverse_wind_mat import reverse_wind_mat" in other
    redirected = redirect_moved_calls(other, package, "Winding", TWO)
    assert "Functions.Winding" not in redirected
    assert "from ....Classes.Winding import Winding" in redirected
    assert "return Winding.reverse_wind_mat(wind_mat) + zeros(1)" in redirected
    ast.parse(redirected)


def test_several_functions_alias_and_calls():
    """One alias per moved function; the callers import the others as before."""
    alias = alias_source("Winding.reverse_wind_mat", TWO["Winding.reverse_wind_mat"])
    assert "def reverse_wind_mat(*args, **kwargs):" in alias
    assert "def reverse_layer(*args, **kwargs):" in alias
    ast.parse(alias)
    caller = (
        "from ...Functions.Winding.reverse_wind_mat import reverse_layer, other\n\n\n"
        "def draw(wind_mat):\n"
        "    return reverse_layer(wind_mat)\n"
    )
    result = redirect_moved_calls(caller, "pyleecan.Functions.FEMM", None, TWO)
    assert "from ...Functions.Winding.reverse_wind_mat import other" in result
    assert (
        "    from ...Classes.Winding import Winding\n"
        "    return Winding.reverse_layer(wind_mat)\n"
    ) in result


PHASE = MovedFunction("Winding", "get_phase_id", bound=("wind_mat", "get_connection_mat"))
BOUND = {"Winding.find_wind_phase_color": (PHASE,)}
PHASE_MODULE = '''def get_phase_id(wind_mat, Nrad, Zs=0):
    """Phase id

    Parameters
    ----------
    wind_mat : numpy.ndarray
        Winding matrix
    Nrad : int
        Radial id

    Returns
    -------
    q_id: int
        Id of the phase
    """
    return wind_mat[Nrad, Zs]
'''


def test_bound_methods():
    """The legacy body is static ("_<method>"), the method reads the object."""
    assert PHASE.methods == ("_get_phase_id", "get_phase_id")
    package = "pyleecan.Methods_new.machine.Winding"
    implementation = method_source(PHASE_MODULE, PHASE, "pyleecan.Functions.Winding", package)
    assert "@staticmethod\ndef _get_phase_id(wind_mat, Nrad, Zs=0):" in implementation
    method = bound_method_source(PHASE_MODULE, PHASE)
    namespace = {}
    exec(method, namespace)

    class Fake:
        _get_phase_id = staticmethod(lambda w, n, z: (w, n, z))

        def get_connection_mat(self):
            return "matrix"

    Fake.get_phase_id = namespace["get_phase_id"]
    assert Fake().get_phase_id(1) == ("matrix", 1, 0)
    assert Fake().get_phase_id(1, 2, wind_mat="given") == ("given", 1, 2)
    assert "    self : Winding\n        A Winding object\n" in method
    assert "(default: self.get_connection_mat())" in method


def test_bound_calls():
    """With x = obj.getter(...) before: obj.method(..., wind_mat=x); else static."""
    source = (
        "from ...Functions.Winding.find_wind_phase_color import get_phase_id\n\n\n"
        "def assign(lam, a, b):\n"
        "    wind_mat = lam.winding.get_connection_mat(lam.get_Zs())\n"
        "    q = get_phase_id(wind_mat, a, b)\n"
        "    r = get_phase_id(wind_mat, a)\n"
        "    return q, r\n\n\n"
        "def other(wind_mat, a):\n"
        "    return get_phase_id(wind_mat, a)\n"
    )
    result = redirect_moved_calls(source, "pyleecan.Functions.FEMM", None, BOUND)
    assert "q = lam.winding.get_phase_id(a, b, wind_mat=wind_mat)" in result
    assert "r = lam.winding.get_phase_id(a, wind_mat=wind_mat)" in result
    assert "    from ...Classes.Winding import Winding\n    return Winding._get_phase_id(wind_mat, a)\n" in result
    ast.parse(result)
    alias = alias_source("Winding.find_wind_phase_color", BOUND["Winding.find_wind_phase_color"])
    assert "return Winding._get_phase_id(*args, **kwargs)" in alias
