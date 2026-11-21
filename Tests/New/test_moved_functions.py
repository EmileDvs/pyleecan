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


TIME_MODULE = '''import numpy as np

from ...Classes.DataTime import DataTime


def n2dqh_DataTime(data, phase_dir=None):
    """To the dqh frame"""
    if phase_dir is None:
        phase_dir = get_dir(data)
    else:
        # Check the data
        _check(data)
    return DataTime(values=convert(data.values, phase_dir))


def convert(values, phase_dir):
    return values * phase_dir


def get_dir(data):
    _check(data)
    from ...Functions.Electrical.freq import get_dir as get_dir_freq

    return get_dir_freq(data.values)


def _check(data):
    if data is None:
        raise ValueError("no data")
'''
FREQ_MODULE = '''from ...Functions.Electrical.time import _check, convert


def get_dir(values):
    return 1
'''
MERGED = {
    "SciDataTool.dqh": {
        "sources": (("Electrical.time", {}), ("Electrical.freq", {"get_dir": "get_dir_freq"})),
        "dropped": ("_check",),
    }
}
TIME_MOVED = {"Electrical.time": MovedFunction("DataTime", "n2dqh", function="n2dqh_DataTime")}


@pytest.fixture
def merged(monkeypatch):
    from pyleecan.Generator.ClassGenerator.New import moved_functions

    monkeypatch.setattr(moved_functions, "MERGED_MODULES", MERGED)
    monkeypatch.setattr(moved_functions, "MOVED_FUNCTIONS", TIME_MOVED)
    return moved_functions


def test_merged_module_source(merged):
    """Functions of both modules, renamed, without the moved and dropped ones."""
    sources = {"Electrical.time": TIME_MODULE, "Electrical.freq": FREQ_MODULE}
    source = merged.merged_module_source("SciDataTool.dqh", sources.__getitem__)
    tree = ast.parse(source)
    names = [node.name for node in tree.body if isinstance(node, ast.FunctionDef)]
    assert names == ["convert", "get_dir", "get_dir_freq"]
    assert "_check" not in source and "n2dqh_DataTime" not in source
    assert "Functions.Electrical" not in source  # Imports between the merged modules removed
    assert "return get_dir_freq(data.values)" in source
    # Class imports in the functions, the other imports kept at the top
    assert "import numpy as np" in source
    assert "\nfrom ...Classes.DataTime import DataTime" not in source


def test_merged_method_and_aliases(merged):
    """The moved function: checks dropped, siblings from the merged module."""
    module_source = merged.drop_merged_calls(TIME_MODULE, "Electrical.time")
    assert "        _check(data)" not in module_source and "    _check(data)\n" not in module_source
    assert "else" not in module_source and "# Check the data" not in module_source
    method = merged.method_source(
        module_source,
        TIME_MOVED["Electrical.time"],
        "pyleecan.Functions.Electrical",
        "pyleecan.Methods_new.scidatatool.DataTime",
        siblings=("..SciDataTool.dqh", ["convert", "get_dir", "_check"], {}),
    )
    assert "def n2dqh(self, phase_dir=None):" in method
    assert "    from ....Functions.SciDataTool.dqh import convert, get_dir\n" in method
    aliases = merged.merged_alias_source("Electrical.time", TIME_MODULE)
    assert "return DataTime.n2dqh(obj, *args, **kwargs)" in aliases
    assert "from ...Functions.SciDataTool.dqh import convert as function" in aliases
    assert "def _check" not in aliases
    ast.parse(aliases)
    freq_aliases = merged.merged_alias_source("Electrical.freq", FREQ_MODULE)
    assert "from ...Functions.SciDataTool.dqh import get_dir_freq as function" in freq_aliases


def test_merged_function_with_the_method_name(merged):
    """A merged function named as the method is imported as <name>_fct."""
    source = (
        "def n2dqh_DataTime(data):\n    return n2dqh(data.values)\n\n\n"
        "def n2dqh(values):\n    return values\n"
    )
    target = MovedFunction("DataTime", "n2dqh", function="n2dqh_DataTime")
    method = merged.method_source(
        source, target, "pyleecan.Functions.Electrical", "pyleecan.Methods_new.scidatatool.DataTime",
        siblings=("..SciDataTool.dqh", ["n2dqh"], {}),
    )
    assert "    from ....Functions.SciDataTool.dqh import n2dqh as n2dqh_fct\n" in method
    assert "return n2dqh_fct(self.values)" in method
    renamed = merged.method_source(
        source, target, "pyleecan.Functions.Electrical", "pyleecan.Methods_new.scidatatool.DataFreq",
        siblings=("..SciDataTool.dqh", ["n2dqh"], {"n2dqh": "n2dqh_freq"}),
    )
    assert "import n2dqh_freq as n2dqh_fct\n" in renamed


def test_merged_module_callers(merged):
    """Callers import from the merged module (renamed with as) or call the method."""
    caller = (
        "from ....Functions.Electrical.time import n2dqh_DataTime, convert\n"
        "from ....Functions.Electrical.freq import get_dir\n\n\n"
        "def run(self, data):\n"
        "    return n2dqh_DataTime(data, phase_dir=get_dir(data.values)), convert\n"
    )
    result = merged.redirect_moved_calls(caller, "pyleecan.Methods_new.output.OutElec", "OutElec")
    assert "from ....Functions.SciDataTool.dqh import convert" in result
    assert "from ....Functions.SciDataTool.dqh import get_dir_freq as get_dir" in result
    assert "return data.n2dqh(phase_dir=get_dir(data.values)), convert" in result


def test_merge_into_a_source(monkeypatch):
    """A module merged into another legacy module: identical, renamed, errors."""
    from pyleecan.Generator.ClassGenerator.New import moved_functions

    spec = {
        "SciDataTool.conv": {
            "sources": (("SciDataTool.conv", {}), ("Structural.conv", {"f": "f_points"})),
            "dropped": (),
            "identical": ("same",),
            "errors": ("DimError",),
        }
    }
    monkeypatch.setattr(moved_functions, "MERGED_MODULES", spec)
    monkeypatch.setattr(moved_functions, "MOVED_FUNCTIONS", {})
    sources = {
        "SciDataTool.conv": "UNITS = 1\n\n\ndef same(x):\n    return x\n\n\ndef f(a, b, c):\n    return a\n",
        "Structural.conv": (
            "class DimError(Exception):\n    pass\n\n\n"
            "def same(x):\n    return x\n\n\ndef f(values, points):\n    return same(values)\n"
        ),
    }
    merged = moved_functions.merged_module_source("SciDataTool.conv", sources.__getitem__)
    tree = ast.parse(merged)
    assert [n.name for n in tree.body if isinstance(n, ast.FunctionDef)] == ["same", "f", "f_points"]
    assert "UNITS = 1" in merged and "from ...classes_common.errors import DimError" in merged
    alias = moved_functions.merged_alias_source("Structural.conv", sources["Structural.conv"])
    assert "from ...classes_common.errors import DimError  # noqa: F401" in alias
    assert "import f_points as function" in alias
    caller = "from ....Functions.Structural.conv import DimError, f\n"
    result = moved_functions.redirect_moved_calls(caller, "pyleecan.Methods_new.mesh.MeshSolution")
    assert "from ....Functions.SciDataTool.conv import f_points as f" in result
    assert "from ....classes_common.errors import DimError" in result
    # The merge target itself: imports unchanged
    same = "from ....Functions.SciDataTool.conv import f\n"
    assert moved_functions.redirect_moved_calls(same, "pyleecan.Methods_new.mesh.MeshSolution") == same


def test_new_methods_added_to_the_classes():
    from pyleecan.Generator.ClassGenerator.New.moved_functions import NEW_METHODS, all_moved_targets

    gen_dict = {target.class_name: {"methods": []} for _, target in all_moved_targets()}
    gen_dict["DataDual"] = {"methods": ["get_along"]}
    add_moved_methods(gen_dict)
    assert set(NEW_METHODS["DataDual"]) <= set(gen_dict["DataDual"]["methods"])
    assert "n2dqh" in gen_dict["DataTime"]["methods"]


def test_method_source_local_class_imports():
    """local_imports: the class imports go in the method body, marked circular."""
    source = (
        "from glob import glob\n\nfrom ...Classes.VectorField import VectorField\n\n\n"
        'def animate(func, data):\n    """Doc"""\n    return isinstance(data, VectorField)\n'
    )
    target = MovedFunction("Data", "animate", static=True, local_imports=True)
    result = method_source(source, target, "pyleecan.Functions.Plot", "pyleecan.Methods_new.scidatatool.Data")
    assert "\nfrom ....Classes.VectorField" not in result
    assert (
        '    """Doc"""\n'
        "    # Local import: circular import with the class module\n"
        "    from ....Classes.VectorField import VectorField\n"
    ) in result
    assert "from glob import glob" in result
    ast.parse(result)


def test_self_parameter():
    """The second parameter becomes self; the alias keeps the legacy signature."""
    source = (
        'def comp_MTPA(machine, LUT, N0, is_plot=False):\n'
        '    """MTPA\n\n    Parameters\n    ----------\n    machine : Machine\n        a machine\n'
        '    LUT : LUTdq\n        a LUT\n    """\n'
        "    return LUT.get(machine, N0), is_plot\n"
    )
    target = MovedFunction("LUTdq", "comp_MTPA", self_parameter="LUT")
    method = method_source(source, target, "pyleecan.Functions.Electrical", "pyleecan.Methods_new.output.LUTdq")
    assert "def comp_MTPA(self, machine, N0, is_plot=False):" in method
    assert "return self.get(machine, N0), is_plot" in method
    assert "    self : LUTdq\n" in method
    alias = alias_source("Electrical.comp_MTPA", target, source)
    namespace = {}
    exec(alias, namespace)

    class FakeLUT:
        def comp_MTPA(self, machine, N0, is_plot=False):
            return machine, N0, is_plot

    with warnings.catch_warnings(record=True):
        warnings.simplefilter("always")
        assert namespace["comp_MTPA"]("m", FakeLUT(), 3, is_plot=True) == ("m", 3, True)


def test_deprecate_source():
    """The public functions of a deprecated module warn; the private ones do not."""
    from pyleecan.Generator.ClassGenerator.New.moved_functions import deprecate_source

    source = (
        '"""Module"""\n\nimport numpy as np\n\n\n'
        'def plot(data):\n    """Doc"""\n    return data\n\n\n'
        "def _helper():\n    return 1\n"
    )
    result = deprecate_source(source, "use Data.plot")
    namespace = {}
    exec(result, namespace)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        assert namespace["plot"](3) == 3
        assert namespace["_helper"]() == 1
    assert len(caught) == 1 and caught[0].category is DeprecationWarning
    assert "plot is deprecated, use Data.plot (removed in Phase 2)" in str(caught[0].message)
    assert result.startswith('"""Module"""\nfrom warnings import warn\n')


def test_moved_modules():
    """Whole modules moved: imports redirected, deprecated module at the old path."""
    from pyleecan.Generator.ClassGenerator.New.moved_functions import (
        moved_module_alias_source,
        redirect_moved_modules,
    )

    source = (
        "from ....Functions.labels import WIND_LAB\n"
        "from ....Functions_new.path_tools import abs_file_path\n"
        "from ....Functions.GUI.log_error import log_error\n"
        "from ....Functions.labelsX import y\n"
    )
    package = "pyleecan.Methods_new.machine.Lamination"
    assert redirect_moved_modules(source, package) == (
        "from ....Functions_new.utils.labels import WIND_LAB\n"
        "from ....Functions_new.utils.path_tools import abs_file_path\n"
        "from ....GUI_new.Tools.log_error import log_error\n"
        "from ....Functions.labelsX import y\n"
    )
    legacy = "import re\nA_LAB = 'A'\n\n\ndef f():\n    pass\n\n\nclass FileError(Exception):\n    pass\n"
    alias = moved_module_alias_source("path_tools", legacy, {"FileError": "FileError"})
    compile(alias, "path_tools.py", "exec")
    assert "from .utils.path_tools import (  # noqa: F401\n    A_LAB,\n    f,\n)\n" in alias
    assert "from ..classes_common.errors import FileError  # noqa: F401\n" in alias
    assert "DeprecationWarning" in alias
    gui = moved_module_alias_source("GUI.log_error", "def log_error():\n    pass\n")
    assert "from ...GUI_new.Tools.log_error import (  # noqa: F401\n    log_error,\n)\n" in gui
