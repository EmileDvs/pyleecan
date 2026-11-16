"""Type hints drafted from the numpydoc docstrings (type_hints.py)."""

from collections import Counter

from pyleecan.Generator.ClassGenerator.New.source_names import name_maps
from pyleecan.Generator.ClassGenerator.New.type_hints import add_type_hints

PACKAGE = "pyleecan.Methods_new.geometry.Segment"


def _hint(source):
    unrecognized = Counter()
    result = add_type_hints(
        source, PACKAGE, name_maps().gen_dict, "Segment", unrecognized
    )
    return result, unrecognized


def test_builtin_hints_and_pep8_default():
    source = '''def f(self, a, n=2, flag=None):
    """Doc

    Parameters
    ----------
    self : Segment
        A Segment object
    a : complex
        A point
    n : int
        A number
    flag : bool
        A flag

    Returns
    -------
    d: float
        A distance
    """
    return 1.0
'''
    result, _ = _hint(source)
    assert (
        "def f(self, a: complex, n: int = 2, flag: bool | None = None) -> float:"
        in result
    )


def test_class_hint_imported_for_type_checking():
    source = '''def f(self, other):
    """Doc

    Parameters
    ----------
    other : Arc1
        An arc
    """
    pass
'''
    result, _ = _hint(source)
    assert result.startswith("from typing import TYPE_CHECKING\n")
    assert (
        "if TYPE_CHECKING:\n    from ....Classes_new.geometry.arc_1 import Arc1\n"
        in result
    )
    assert "def f(self, other: Arc1):" in result


def test_unrecognized_and_contradicting_defaults_are_reported():
    source = '''def f(self, color=None, is_set=0):
    """Doc

    Parameters
    ----------
    color : the color of the patch (Default value = PATCH_COLOR)
        A color
    is_set : bool
        A flag
    """
    pass
'''
    result, unrecognized = _hint(source)
    assert "def f(self, color=None, is_set=0):" in result  # No hint
    assert unrecognized["bool (default 0)"] == 1
    assert unrecognized["the color of the patch (Default value = PATCH_COLOR)"] == 1


def test_idempotent():
    source = '''def f(self, a: complex) -> float:
    """Doc

    Parameters
    ----------
    a : complex
        A point

    Returns
    -------
    d : float
        A distance
    """
    return 1.0
'''
    result, _ = _hint(source)
    assert result == source
    twice = _hint(_hint(source.replace(": complex) -> float", ")"))[0])[0]
    assert twice == source


def test_several_returns_as_tuple():
    source = '''def f(self):
    """Doc

    Returns
    -------
    a : float
        A
    b : int
        B
    """
    return 1.0, 2
'''
    result, _ = _hint(source)
    assert "def f(self) -> tuple[float, int]:" in result


def test_container_hints():
    source = '''def f(self, z_list, surf_dict, patches, other):
    """Doc

    Parameters
    ----------
    z_list : [complex]
        Points
    surf_dict : {Surface}
        Surfaces
    patches : list of matplotlib.patches.Polygon
        Patches
    other : [unknown thing]
        Not recognized
    """
    pass
'''
    result, unrecognized = _hint(source)
    assert "z_list: list[complex]" in result
    assert "surf_dict: dict[str, Surface]" in result
    assert "patches: list[Polygon]" in result
    assert "from matplotlib.patches import Polygon" in result
    assert ", other):" in result  # Unrecognized item type: no hint
    assert unrecognized["[unknown thing]"] == 1


def test_return_override():
    source = '''def plot_schematics(self, is_return_default=False):
    """Doc

    Returns
    -------
    fig : Matplotlib.figure.Figure
        Figure containing the schematics
    ax : Matplotlib.axes.Axes object
        Axis containing the schematics
    """
    pass


def g(self):
    """No Returns section"""
    pass
'''
    result = add_type_hints(
        source, "pyleecan.Methods_new.slot.SlotW10", name_maps().gen_dict, "SlotW10"
    )
    assert "-> tuple[Figure, Axes] | Lamination:" in result
    assert "from ....Classes_new.machine.lamination import Lamination" in result
    assert "def g(self):" in result
    # Other sub-packages keep the documented return
    result, _ = _hint(source)  # geometry
    assert "-> tuple[Figure, Axes]:" in result


def test_container_local_annotated_with_the_field_type():
    source = '''def f(self):
    curve_list = list()
    curve_list.append(Segment())
    surf = SurfLine(line_list=curve_list)
    curve_list = list()
    return surf
'''
    result, _ = _hint(source)
    assert "    curve_list: list[Line] = list()\n" in result
    assert result.count("curve_list: list[Line]") == 1  # First assignment only
    assert "from ...surf_line" not in result  # SurfLine is not a hint
    assert "    from ....Classes_new.geometry.line import Line\n" in result
    assert _hint(result)[0] == result  # Idempotent


def test_container_local_left_unchanged():
    source = '''def f(self, given):
    built = self.build()
    a = SurfLine(line_list=built)
    b = SurfLine(line_list=given)
    c = SurfLine(label=label)

    def g():
        local = []
        return SurfLine(line_list=local)
'''
    result, _ = _hint(source)
    assert result == source  # Not a container, a parameter, a str field, a nested scope


def test_container_local_annotated_in_each_branch():
    source = '''def f(self, a):
    if a:
        curve_list = list()
        for i in a:
            curve_list = []
        s = SurfLine(line_list=curve_list)
    else:
        curve_list = list()
        s = SurfLine(line_list=curve_list)
    return s
'''
    result, _ = _hint(source)
    assert "        curve_list: list[Line] = list()\n" in result
    assert "            curve_list = []\n" in result  # After the declaration
    assert result.count("curve_list: list[Line] = list()") == 2  # if and else
    assert _hint(result)[0] == result


def test_unpacked_kwargs_dict_annotated():
    source = '''def f(self, fig):
    kwargs = dict(fig=fig, color="k", linewidth=2)
    self.plot(label="W0", **kwargs)
    options = self.get_options()
    self.plot(**options)
'''
    result, _ = _hint(source)
    assert "    kwargs: dict[str, Any] = dict(fig=fig" in result
    assert "    options = self.get_options()\n" in result  # Not built here
    assert "    from typing import Any\n" in result  # Under TYPE_CHECKING
    assert _hint(result)[0] == result


def test_parameter_overrides_complete_the_docstring():
    source = '''def BH_func(self, H, Bs, a):
    """Doc

    Returns
    -------
    B: numpy.ndarray
        B(H) values
    """
    return Bs
'''
    result = add_type_hints(
        source, "pyleecan.Methods_new.material.ModelBH_Langevin", name_maps().gen_dict
    )
    assert (
        "def BH_func(self, H: float | np.ndarray, Bs: float, a: float)"
        " -> float | np.ndarray:"
    ) in result
