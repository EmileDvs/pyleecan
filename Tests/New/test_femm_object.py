"""Tests of the FEMM interface object generator (femm_object.py)."""

import ast
import warnings

from pyleecan.Generator.ClassGenerator.New.femm_object import (
    femm_alias_source,
    femm_object_source,
    femm_signatures,
    redirect_femm_calls,
)

MODULES = {
    "draw": '''from ...Functions.FEMM.mesh import mesh


class FEMMError(Exception):
    pass


def draw(femm, surf, size=1):
    """Draw

    Parameters
    ----------
    femm : FEMMHandler
        client to send command to a FEMM instance
    surf : Surface
        a surface
    """
    femm.mi_addnode(0, 0)
    surf.draw_FEMM(femm=femm)
    return set_prop(femm, mesh(size))


def set_prop(femm, value):
    femm.mi_setprop(value)
    return value
''',
    "mesh": '''def mesh(size):
    """Mesh size (no handler)"""
    return 2 * size
''',
}


class Handler:
    def __init__(self):
        self.calls = []

    def __getattr__(self, name):
        return lambda *args: self.calls.append((name, args))


class Surf:
    def draw_FEMM(self, femm):
        self.femm = femm


def make_class():
    source = femm_object_source(MODULES, {"draw": {"FEMMError"}})
    ast.parse(source)
    assert "from ...classes_common.errors import FEMMError" in source
    assert "Functions.FEMM.mesh" not in source
    source = source.replace("from ...classes_common.errors import FEMMError", "")
    namespace = {}
    exec(source, namespace)
    return namespace["femm_pyleecan"], source


def test_femm_object_methods():
    """Handler functions become methods, the others static methods."""
    femm_pyleecan, source = make_class()
    assert "    def draw(self, surf, size=1):" in source
    assert "    @staticmethod\n    def mesh(size):" in source
    assert "        self : femm_pyleecan\n" in source
    handler = Handler()
    femm = femm_pyleecan(handler)
    surf = Surf()
    assert femm.draw(surf, size=3) == 6
    assert handler.calls == [("mi_addnode", (0, 0)), ("mi_setprop", (6,))]
    assert surf.femm is femm  # The object is passed, not the handler
    assert femm_pyleecan.mesh(2) == 4


def test_femm_aliases():
    """The aliases accept a handler or a femm_pyleecan object."""
    signatures = femm_signatures(MODULES)
    assert signatures == {"draw": 0, "set_prop": 0, "mesh": None}
    alias = femm_alias_source("draw", MODULES["draw"], MODULES, {"draw": {"FEMMError"}})
    ast.parse(alias)
    assert "from ...classes_common.errors import FEMMError  # noqa: F401" in alias
    femm_pyleecan, _ = make_class()
    namespace = {}
    exec(alias.replace("from ...classes_common.errors import FEMMError  # noqa: F401", "").replace(
        "from .femm_pyleecan import femm_pyleecan", "femm_pyleecan = FEMM_CLASS"
    ), namespace)
    namespace["FEMM_CLASS"] = femm_pyleecan
    handler = Handler()
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        assert namespace["set_prop"](handler, 5) == 5  # A handler
        assert namespace["set_prop"](femm_pyleecan(handler), value=7) == 7  # An object
    assert handler.calls == [("mi_setprop", (5,)), ("mi_setprop", (7,))]
    assert all(issubclass(w.category, DeprecationWarning) for w in caught)


def test_object_without_handler():
    """GMSH: static methods only, calls between them on the class."""
    from pyleecan.Generator.ClassGenerator.New.femm_object import GMSH

    modules = {
        "draw_GMSH": (
            "from ...Functions.GMSH.get_box import get_box\n\n\n"
            'def draw_GMSH(machine, size=1):\n    """Draw"""\n    return get_box(size) + _helper()\n\n\n'
            "def _helper():\n    return 1\n"
        ),
        "get_box": "def get_box(size):\n    return 10 * size\n",
    }
    source = femm_object_source(modules, spec=GMSH)
    assert "def __init__" not in source
    assert "return gmsh_pyleecan.get_box(size) + gmsh_pyleecan._helper()" in source
    namespace = {}
    exec(source, namespace)
    assert namespace["gmsh_pyleecan"].draw_GMSH(None, size=2) == 21
    caller = (
        "from ....Functions.GMSH.draw_GMSH import draw_GMSH\n\n\n"
        "def gen_mesh(self, output):\n    return draw_GMSH(output.machine, size=2)\n"
    )
    result = redirect_femm_calls(
        caller, "pyleecan.Methods_new.structural.StructElmer", femm_signatures(modules, GMSH), GMSH
    )
    assert "return gmsh_pyleecan.draw_GMSH(output.machine, size=2)" in result
    assert "from ....Functions.GMSH.gmsh_pyleecan import gmsh_pyleecan" in result


def test_redirect_femm_calls():
    """Callers use the object: methods, handler commands, construction."""
    source = (
        "from ....Classes._FEMMHandler import _FEMMHandler\n"
        "from ....Functions.FEMM.draw import draw, FEMMError\n"
        "from ....Functions.FEMM.mesh import mesh\n\n\n"
        "def solve(self, output):\n"
        "    femm = _FEMMHandler()\n"
        "    femm.openfemm(1)\n"
        "    return draw(femm, output.surf, size=mesh(2)), FEMMError\n\n\n"
        "def other(femm):\n"
        "    femm.mi_close()\n"
    )
    result = redirect_femm_calls(source, "pyleecan.Methods_new.magnetics.MagFEMM", femm_signatures(MODULES))
    ast.parse(result)
    assert "    femm = femm_pyleecan()\n" in result
    assert "    femm.handler.openfemm(1)\n" in result
    assert "return femm.draw(output.surf, size=femm_pyleecan.mesh(2)), FEMMError" in result
    assert "    femm.handler.mi_close()\n" in result
    assert "from ....Functions.FEMM.femm_pyleecan import FEMMError" in result
    assert "    # Local import: circular import with the class module\n" in result
    assert "Functions.FEMM.draw import" not in result and "Functions.FEMM.mesh" not in result


def test_redirect_calls_in_class_methods():
    """GUI widgets: calls in methods; a try-guarded import keeps its name bound."""
    source = (
        "from ...Functions.FEMM.mesh import mesh\n"
        "try:\n"
        "    from ...Functions.FEMM.draw import draw\n"
        "except Exception as e:\n"
        "    draw = e\n\n\n"
        "class Widget:\n"
        "    def run(self, femm, output):\n"
        "        if isinstance(draw, Exception):\n"
        "            return None\n"
        "        return draw(femm, output.surf, size=mesh(2))\n"
    )
    package = "pyleecan.GUI_new.Dialog"
    result = redirect_femm_calls(source, package, femm_signatures(MODULES))
    ast.parse(result)
    assert (
        "try:\n"
        "    from ...Functions.FEMM.femm_pyleecan import femm_pyleecan\n"
        "    draw = femm_pyleecan.draw\n"
        "except Exception as e:\n"
    ) in result
    assert "        return femm.draw(output.surf, size=femm_pyleecan.mesh(2))\n" in result
