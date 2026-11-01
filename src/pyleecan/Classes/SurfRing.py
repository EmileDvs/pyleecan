# File generated according to Generator/ClassesRef/Geometry/SurfRing.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Geometry/SurfRing"""

from os import linesep
from sys import getsizeof

import numpy as np

from pyleecan.Classes.Surface import Surface
from pyleecan.Classes._check import check_var
from pyleecan.definitions import config_dict
from pyleecan.Functions.Load.import_class import import_class
from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.init_fig import init_fig
from pyleecan.Functions.load import load_init_dict
from pyleecan.Functions.save import save


class SurfRing(Surface):
    """SurfRing is a surface between two closed surfaces (lamination surfaces for instance)"""

    VERSION = 1
    PATCH_EDGE = config_dict["PLOT"]["COLOR_DICT"]["PATCH_EDGE"]
    PATCH_COLOR = config_dict["PLOT"]["COLOR_DICT"]["PATCH_COLOR"]
    PATCH_COLOR_ALPHA = config_dict["PLOT"]["COLOR_DICT"]["PATCH_COLOR_ALPHA"]
    PATCH_EDGE_ALPHA = config_dict["PLOT"]["COLOR_DICT"]["PATCH_EDGE_ALPHA"]

    # cf Methods.Geometry.SurfRing.check
    # -*- coding: utf-8 -*-
    def check(self):
        """assert the Surface is correct

        Parameters
        ----------
        self : SurfRing
            A SurfRing object

        Returns
        -------
        None
        """
        self.out_surf.check()
        self.in_surf.check()

    # cf Methods.Geometry.SurfRing.comp_length
    # -*- coding: utf-8 -*-
    def comp_length(self):
        """Compute the length of the SurfRing object (length of both surfaces)

        Parameters
        ----------
        self : SurfRing
            A SurfRing object

        Returns
        -------
        length: float
            Length of the surface [m]


        """
        return self.out_surf.comp_length() + self.in_surf.comp_length()

    # cf Methods.Geometry.SurfRing.comp_point_ref
    def comp_point_ref(self, is_set=False):
        """Compute the point ref of the Surface

        Parameters
        ----------
        self : SurfRing
            A SurfRing object
        is_set: bool
            True to update the point_ref property

        Returns
        -------
        point_ref : complex
            the reference point of the surface
        """

        point_list = list()
        out_lines = self.out_surf.get_lines()
        in_lines = self.in_surf.get_lines()
        # Compute the ref point as the barycenter of half the lines
        for line in out_lines[: len(out_lines) / 2]:
            point_list.append(line.get_middle())
        for line in in_lines[: len(in_lines) / 2]:
            point_list.append(line.get_middle())
        point_ref = np.sum(np.array(point_list)) / len(point_list)

        if is_set:
            self.point_ref = point_ref
        return point_ref

    # cf Methods.Geometry.SurfRing.comp_surface
    def comp_surface(self):
        """Compute the SurfRing surface

        Parameters
        ----------
        self : SurfRing
            A SurfRing object

        Returns
        -------
        surf: float
            The SurfRing surface [m**2]

        """

        Sout = self.out_surf.comp_surface()
        Sin = self.in_surf.comp_surface()

        assert Sout > Sin

        return Sout - Sin

    # cf Methods.Geometry.SurfRing.discretize
    # -*-- coding: utf-8 -*
    def discretize(self, Npoint=-1):
        """Returns the discretize version of the SurfRing

        Parameters
        ----------
        self: SurfRing
            A SurfRing object
        Npoint : int
            Number of point on each line (Default value = -1 => use the line default discretization)

        Returns
        -------
        point_list : list
            List of complex coordinates
        """
        # check if the SurfRing is correct
        self.check()
        # getting lines that delimit the SurfLine

        point_list = self.out_surf.discretize(Npoint=Npoint)
        point_list.extend(self.in_surf.discretize(Npoint=Npoint))
        return point_list

    # cf Methods.Geometry.SurfRing.get_lines
    # -*- coding: utf-8 -*-
    def get_lines(self):
        """The list returned contains all the Line of the SurRing

        Parameters
        ----------
        self : SurfRing
            A SurfRing object


        Returns
        -------
        line_list : list
            list of lines delimiting the surface

        """
        line_list = list()
        line_list.extend(self.out_surf.get_lines())
        line_list.extend(self.in_surf.get_lines())
        return line_list

    # cf Methods.Geometry.SurfRing.get_patches
    def get_patches(
        self, color=None, edgecolor=None, is_edge_only=False, linestyle=None
    ):
        """Returns the PolarArc Patch to be display in matplotlib

        Parameters
        ----------
        self : SurfLine
            a SurfLine object
        color :
            the color of the patch (Default value = PATCH_COLOR)
        edgecolor :
            the edge color of the patch (Default value = PATCH_EDGE)
        is_edge_only: bool
            To set the transparancy of the face color to 0 and 1 for the edge color
        linestyle : str
            Line style of the edge {'-', '--', '-.', ':', '', (offset, on-off-seq), ...}

        Returns
        -------
        patch_list : list of matplotlib.patches.Polygon
            List of patches corresponding to the surface

        """
        patch_list = self.out_surf.get_patches(
            color=color,
            edgecolor=edgecolor,
            is_edge_only=is_edge_only,
            linestyle=linestyle,
        )
        # No color for inner surface
        patch_list.extend(
            self.in_surf.get_patches(
                is_edge_only=is_edge_only, edgecolor=edgecolor, linestyle=linestyle
            )
        )
        return patch_list

    get_patches.__defaults__ = (
        get_patches.__defaults__[:0] + (PATCH_COLOR,) + get_patches.__defaults__[1:]
    )

    # cf Methods.Geometry.SurfRing.plot_lines
    def plot_lines(self, fig=None, ax=None):
        """Plot the SurfRing-Contour in a matplotlib fig
        (For plotting unclosed contour, for Polygon use plot method from Surface object)

        Parameters
        ----------
        self : SurfRing
            A SurfRing object
        fig : Matplotlib.figure.Figure
            existing figure to use if None create a new one
        ax : Matplotlib.axes.Axes object
            Axis on which to plot the data

        Returns
        -------
        fig : Matplotlib.figure.Figure
            Figure containing the plot
        ax : Matplotlib.axes.Axes object
            Axis containing the plot
        """

        (fig, ax, patch_leg, label_leg) = init_fig(fig, ax)
        ax.set_xlabel("[m]")
        ax.set_ylabel("[m]")

        points = self.out_surf.discretize(10)
        for idx in range(len(points) - 1):
            z1 = points[idx]
            z2 = points[idx + 1]
            x1 = np.real(z1)
            y1 = np.imag(z1)
            x2 = np.real(z2)
            y2 = np.imag(z2)
            ax.plot([x1, x2], [y1, y2], "k")

        points = self.in_surf.discretize(10)
        for idx in range(len(points) - 1):
            z1 = points[idx]
            z2 = points[idx + 1]
            x1 = np.real(z1)
            y1 = np.imag(z1)
            x2 = np.real(z2)
            y2 = np.imag(z2)
            ax.plot([x1, x2], [y1, y2], "k")

        # Axis Setup
        ax.axis("equal")

        fig.show()
        return fig, ax

    # cf Methods.Geometry.SurfRing.rotate
    def rotate(self, angle):
        """Rotate the surface

        Parameters
        ----------
        self : SurfRing
            A SurfRing object

        angle : float
            the angle of rotation [rad]

        Returns
        -------
        None
        """
        if angle == 0:
            return  # Nothing to do
        # Check if the Surface is correct
        self.check()
        # rotation of every line in the Surface
        self.out_surf.rotate(angle)
        self.in_surf.rotate(angle)
        if self.point_ref is not None:
            self.point_ref = self.point_ref * np.exp(1j * angle)

    # cf Methods.Geometry.SurfRing.translate
    def translate(self, Zt):
        """Translate the surface

        Parameters
        ----------
        self : SurfRing
            A SurfRing object

        Zt : complex
            Complex value for translation

        Returns
        -------
        None
        """
        if Zt == 0:
            return  # Nothing to do
        # Check if the Surface is correct
        self.check()

        self.out_surf.translate(Zt)
        self.in_surf.translate(Zt)

        if self.point_ref is not None:
            self.point_ref += Zt

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        out_surf=-1,
        in_surf=-1,
        point_ref=0,
        label="",
        init_dict=None,
        init_str=None,
    ):
        """Constructor of the class. Can be use in three ways :
        - __init__ (arg1 = 1, arg3 = 5) every parameters have name and default values
            for pyleecan type, -1 will call the default constructor
        - __init__ (init_dict = d) d must be a dictionary with property names as keys
        - __init__ (init_str = s) s must be a string
        s is the file path to load

        ndarray or list can be given for Vector and Matrix
        object or dict can be given for pyleecan Object"""

        if init_str is not None:  # Load from a file
            init_dict = load_init_dict(init_str)[1]
        if init_dict is not None:  # Initialisation by dict
            assert type(init_dict) is dict
            # Overwrite default value with init_dict content
            if "out_surf" in list(init_dict.keys()):
                out_surf = init_dict["out_surf"]
            if "in_surf" in list(init_dict.keys()):
                in_surf = init_dict["in_surf"]
            if "point_ref" in list(init_dict.keys()):
                point_ref = init_dict["point_ref"]
            if "label" in list(init_dict.keys()):
                label = init_dict["label"]
        # Set the properties (value check and convertion are done in setter)
        self.out_surf = out_surf
        self.in_surf = in_surf
        # Call Surface init
        super(SurfRing, self).__init__(point_ref=point_ref, label=label)
        # The class is frozen (in Surface init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        SurfRing_str = ""
        # Get the properties inherited from Surface
        SurfRing_str += super(SurfRing, self).__str__()
        if self.out_surf is not None:
            tmp = self.out_surf.__str__().replace(linesep, linesep + "\t").rstrip("\t")
            SurfRing_str += "out_surf = " + tmp
        else:
            SurfRing_str += "out_surf = None" + linesep + linesep
        if self.in_surf is not None:
            tmp = self.in_surf.__str__().replace(linesep, linesep + "\t").rstrip("\t")
            SurfRing_str += "in_surf = " + tmp
        else:
            SurfRing_str += "in_surf = None" + linesep + linesep
        return SurfRing_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from Surface
        if not super(SurfRing, self).__eq__(other):
            return False
        if other.out_surf != self.out_surf:
            return False
        if other.in_surf != self.in_surf:
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()

        # Check the properties inherited from Surface
        diff_list.extend(
            super(SurfRing, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
        if (other.out_surf is None and self.out_surf is not None) or (
            other.out_surf is not None and self.out_surf is None
        ):
            diff_list.append(name + ".out_surf None mismatch")
        elif self.out_surf is not None:
            diff_list.extend(
                self.out_surf.compare(
                    other.out_surf,
                    name=name + ".out_surf",
                    ignore_list=ignore_list,
                    is_add_value=is_add_value,
                )
            )
        if (other.in_surf is None and self.in_surf is not None) or (
            other.in_surf is not None and self.in_surf is None
        ):
            diff_list.append(name + ".in_surf None mismatch")
        elif self.in_surf is not None:
            diff_list.extend(
                self.in_surf.compare(
                    other.in_surf,
                    name=name + ".in_surf",
                    ignore_list=ignore_list,
                    is_add_value=is_add_value,
                )
            )
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from Surface
        S += super(SurfRing, self).__sizeof__()
        S += getsizeof(self.out_surf)
        S += getsizeof(self.in_surf)
        return S

    def as_dict(self, type_handle_ndarray=0, keep_function=False, **kwargs):
        """
        Convert this object in a json serializable dict (can be use in __init__).
        type_handle_ndarray: int
            How to handle ndarray (0: tolist, 1: copy, 2: nothing)
        keep_function : bool
            True to keep the function object, else return str
        Optional keyword input parameter is for internal use only
        and may prevent json serializability.
        """

        # Get the properties inherited from Surface
        SurfRing_dict = super(SurfRing, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        if self.out_surf is None:
            SurfRing_dict["out_surf"] = None
        else:
            SurfRing_dict["out_surf"] = self.out_surf.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs
            )
        if self.in_surf is None:
            SurfRing_dict["in_surf"] = None
        else:
            SurfRing_dict["in_surf"] = self.in_surf.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs
            )
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        SurfRing_dict["__class__"] = "SurfRing"
        return SurfRing_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        if self.out_surf is None:
            out_surf_val = None
        else:
            out_surf_val = self.out_surf.copy()
        if self.in_surf is None:
            in_surf_val = None
        else:
            in_surf_val = self.in_surf.copy()
        point_ref_val = self.point_ref
        label_val = self.label
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(
            out_surf=out_surf_val,
            in_surf=in_surf_val,
            point_ref=point_ref_val,
            label=label_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        if self.out_surf is not None:
            self.out_surf._set_None()
        if self.in_surf is not None:
            self.in_surf._set_None()
        # Set to None the properties inherited from Surface
        super(SurfRing, self)._set_None()

    def _get_out_surf(self):
        """getter of out_surf"""
        return self._out_surf

    def _set_out_surf(self, value):
        """setter of out_surf"""
        if isinstance(value, str):  # Load from file
            try:
                value = load_init_dict(value)[1]
            except Exception as e:
                self.get_logger().error(
                    "Error while loading " + value + ", setting None instead"
                )
                value = None
        if isinstance(value, dict) and "__class__" in value:
            class_obj = import_class(
                "pyleecan.Classes", value.get("__class__"), "out_surf"
            )
            value = class_obj(init_dict=value)
        elif type(value) is int and value == -1:  # Default constructor
            Surface = import_class("pyleecan.Classes", "Surface", "out_surf")
            value = Surface()
        check_var("out_surf", value, "Surface")
        self._out_surf = value

        if self._out_surf is not None:
            self._out_surf.parent = self

    out_surf = property(
        fget=_get_out_surf,
        fset=_set_out_surf,
        doc="""Outter surface

        :Type: Surface
        """,
    )

    def _get_in_surf(self):
        """getter of in_surf"""
        return self._in_surf

    def _set_in_surf(self, value):
        """setter of in_surf"""
        if isinstance(value, str):  # Load from file
            try:
                value = load_init_dict(value)[1]
            except Exception as e:
                self.get_logger().error(
                    "Error while loading " + value + ", setting None instead"
                )
                value = None
        if isinstance(value, dict) and "__class__" in value:
            class_obj = import_class(
                "pyleecan.Classes", value.get("__class__"), "in_surf"
            )
            value = class_obj(init_dict=value)
        elif type(value) is int and value == -1:  # Default constructor
            Surface = import_class("pyleecan.Classes", "Surface", "in_surf")
            value = Surface()
        check_var("in_surf", value, "Surface")
        self._in_surf = value

        if self._in_surf is not None:
            self._in_surf.parent = self

    in_surf = property(
        fget=_get_in_surf,
        fset=_set_in_surf,
        doc="""Inner surface

        :Type: Surface
        """,
    )
