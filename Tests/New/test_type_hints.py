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

    return a, b, c, g
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


def test_return_none_when_nothing_is_returned():
    source = '''def check(self):
    """Doc"""
    if self.a < 0:
        raise ValueError("a")


def stub(self):
    """Doc"""
    pass


def values(self):
    """Doc"""
    return 1
'''
    result, _ = _hint(source)
    assert "def check(self) -> None:" in result
    assert "def stub(self):" in result  # May be overridden with a value
    assert "def values(self):" in result  # Undocumented value


def test_undocumented_conventional_and_flag_parameters():
    source = '''def plot(self, fig=None, edgecolor=None, is_add_arrow=False, other=None):
    """Doc"""
    pass
'''
    result, _ = _hint(source)
    assert (
        "def plot(self, fig: Figure | None = None, edgecolor: str | None = None, "
        "is_add_arrow: bool = False, other=None):"
    ) in result
    assert "    from matplotlib.figure import Figure\n" in result


def test_union_and_plural_documented_types():
    source = '''def f(self, a, b):
    """Doc

    Parameters
    ----------
    a : float or ndarray
        A value
    b : list of floats
        Values
    """
    pass
'''
    result, _ = _hint(source)
    assert "def f(self, a: float | np.ndarray, b: list[float]):" in result


def test_returns_with_or_alternatives_and_explicit_none():
    source = '''def plot(self, is_display=True):
    """Doc

    Returns
    -------
    patches : list
        List of Patches

    or

    fig : Matplotlib.figure.Figure
        Figure
    ax : Matplotlib.axes.Axes
        Axes
    """
    if is_display:
        return 1, 2
    return []


def get_p(self):
    """Doc

    Returns
    -------
    p : int
        Number of pole pairs
    """
    if self.x:
        return None
    return 2
'''
    result, _ = _hint(source)
    assert "-> list | tuple[Figure, Axes]:" in result
    assert "def get_p(self) -> int | None:" in result


def test_class_imported_in_the_body_is_imported_for_type_checking():
    source = '''def f(self):
    """Doc

    Returns
    -------
    other : Arc1
        An arc
    """
    from ....Classes_new.geometry.arc_1 import Arc1

    return Arc1()
'''
    result, _ = _hint(source)
    assert "def f(self) -> Arc1:" in result
    assert "if TYPE_CHECKING:\n    from ....Classes_new.geometry.arc_1 import Arc1\n" in result


def test_special_methods_boolean_slice_and_class_paths():
    source = '''def __len__(self):
    """Doc"""
    return len(self.items)


def f(self, flag, idx, out):
    """Doc

    Parameters
    ----------
    flag : boolean
        A flag
    idx : slice
        Indices
    out : ....Classes.Output
        An output
    """
    pass
'''
    result, _ = _hint(source)
    assert "def __len__(self) -> int:" in result
    assert "def f(self, flag: bool, idx: slice, out: Output):" in result


def test_return_hint_after_a_commented_signature():
    source = '''def f(self):  # conversion: to MotorCAD
    """Doc

    Returns
    -------
    n : int
        A number
    """
    return 1


def g(
    self, a=(1, 2)  # a: tuple
):
    """Doc

    Returns
    -------
    n : int
        A number
    """
    return 1
'''
    result, _ = _hint(source)
    assert "def f(self) -> int:  # conversion: to MotorCAD" in result
    assert "\n) -> int:\n" in result


def test_documented_return_of_a_function_returning_nothing():
    source = '''def f(self):
    """Doc

    Returns
    -------
    n : int
        Documented but never returned
    """
    self.n = 1
'''
    result, _ = _hint(source)
    assert "def f(self) -> None:" in result
