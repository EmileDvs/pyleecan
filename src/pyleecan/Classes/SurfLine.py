# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Geometry/SurfLine.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Geometry/SurfLine
"""

from os import linesep
from sys import getsizeof
from logging import getLogger
from pyleecan.Classes._check import check_var, raise_
from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.save import save
from pyleecan.Functions.load import load_init_dict
from pyleecan.Functions.Load.import_class import import_class
from copy import deepcopy
from pyleecan.Classes.Surface import Surface

# Import all class method
# Try/catch to remove unnecessary dependencies in unused method
from numpy import array, sum, exp, angle, min as np_min, max as np_max, argmin
from pyleecan.Functions.Geometry.comp_surface_num import comp_surface_num
from pyleecan.Methods.Geometry.SurfLine.get_patches import (
    PATCH_COLOR,
    PATCH_COLOR_ALPHA,
    PATCH_EDGE,
    PATCH_EDGE_ALPHA,
)
from matplotlib.patches import Polygon
from pyleecan.Functions.init_fig import init_fig

from numpy import isnan
from pyleecan.Classes._check import InitUnKnowClassError


class SurfLine(Surface):
    """SurfLine defined by list of lines that delimit it, label and point reference."""

    VERSION = 1

    # cf Methods.Geometry.SurfLine.check
    # -*- coding: utf-8 -*-
    def check(self):
        """assert the Surface is correct

        Parameters
        ----------
        self : SurfLine
            A SurfLine object

        Returns
        -------
        None
        """
        if self.line_list != []:
            for line in self.line_list:
                line.check()

    # cf Methods.Geometry.SurfLine.comp_length
    # -*- coding: utf-8 -*-
    def comp_length(self):
        """Compute the length of the SurfLine object

        Parameters
        ----------
        self : SurfLine
            A SurfLine object

        Returns
        -------
        length: float
            Length of the surface [m]


        """
        # check if the SurfLine is correct
        self.check()
        length = 0
        for line in self.line_list:
            length += line.comp_length()

        return length

    # cf Methods.Geometry.SurfLine.comp_point_ref
    def comp_point_ref(self, is_set=False):
        """Compute the point ref of the Surface

        Parameters
        ----------
        self : SurfLine
            A SurfLine object
        is_set: bool
            True to update the point_ref property

        Returns
        -------
        point_ref : complex
            the reference point of the surface
        """

        middle_array = array([line.get_middle() for line in self.get_lines()])
        point_ref = sum(middle_array) / middle_array.size

        # Use another method if the point is not is the surface
        if not self.is_inside(Z=point_ref, if_online=False):
            middle_array_abs = abs(middle_array)
            # Find "min abs" middle
            mid_id = argmin(middle_array_abs)
            Zmid = middle_array[mid_id]
            H = np_max(middle_array_abs) - np_min(middle_array_abs)

            point_ref = (abs(Zmid) + H / 100) * exp(1j * angle(Zmid))

        if is_set:
            self.point_ref = point_ref
        return point_ref

    # cf Methods.Geometry.SurfLine.comp_surface
    def comp_surface(self, Ndisc=200):
        """Compute the SurfLine surface

        Parameters
        ----------
        self : SurfLine
            A SurfLine object
        Ndisc : int
            Number of point to discretize the lines

        Returns
        -------
        surf: float
            The SurfLine surface [m**2]

        """

        # Discretize the surface with lots of points to compute the surface numerically
        point_list = self.discretize(Ndisc)

        return comp_surface_num(point_list)

    # cf Methods.Geometry.SurfLine.discretize
    # -*-- coding: utf-8 -*
    def discretize(self, Npoint=-1):
        """Returns the discretize version of the SurfLine

        Parameters
        ----------
        self: SurfLine
            A SurfLine object
        Npoint : int
            Number of point on each line (Default value = -1 => use the line default discretization)

        Returns
        -------
        point_list : list
            List of complex coordinates
        """
        # check if the SurfLine is correct
        self.check()
        # getting lines that delimit the SurfLine
        lines = self.get_lines()
        if lines[0].get_begin() == lines[-1].get_end():
            closed = True
        else:
            closed = False

        point_list = list()
        for line in lines:
            if Npoint == -1:
                point_list.extend(line.discretize())
            else:
                point_list.extend(line.discretize(Npoint))
            if line != lines[-1]:
                point_list.pop()
            else:
                if closed:  # if the SurfLine is closed
                    point_list.pop()
        return point_list

    # cf Methods.Geometry.SurfLine.get_lines
    # -*- coding: utf-8 -*-
    def get_lines(self):
        """The list returned contains all the Line of the SurfLine

        Parameters
        ----------
        self : SurfLine
            A SurfLine object


        Returns
        -------
        line_list : list
            list of lines delimiting the surface

        """
        # Check if the surface is correct
        self.check()
        return self.line_list

    # cf Methods.Geometry.SurfLine.get_patches
    def get_patches(
        self,
        color=PATCH_COLOR,
        edgecolor=None,
        is_edge_only=False,
        linestyle=None,
        hatch=None,
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
        hatch : str
            Set the hatching pattern: {'/', '\', '|', '-', '+', 'x', 'o', 'O', '.', '*'}

        Returns
        -------
        patch_list : list of matplotlib.patches.Polygon
            List of patches corresponding to the surface

        """

        # Set default color
        if edgecolor is None and not is_edge_only:
            edgecolor = PATCH_EDGE
        elif edgecolor is None and is_edge_only:
            edgecolor = PATCH_EDGE_ALPHA
        if is_edge_only:
            color = PATCH_COLOR_ALPHA
        if "--" in edgecolor:
            edgecolor = edgecolor.replace("-", "")
            linestyle = "--"

        # check if the SurfLine is correct
        self.check()
        line_list = self.get_lines()

        if len(line_list) == 0:
            return Polygon([], facecolor=color, edgecolor=edgecolor, hatch=hatch)

        Z_list = list()
        # For each Line discretize
        for line in line_list:
            Z_list += list(line.discretize())

        # abscissa coordinate
        Zr_list = list()
        # ordinate coordinate
        Zi_list = list()

        for ii in range(len(Z_list)):
            Zr_list.append(Z_list[ii].real)
            Zi_list.append(Z_list[ii].imag)
        point_list = list(zip(Zr_list, Zi_list))
        return [
            Polygon(
                point_list,
                facecolor=color,
                edgecolor=edgecolor,
                linestyle=linestyle,
                hatch=hatch,
            )
        ]

    # cf Methods.Geometry.SurfLine.plot_lines
    def plot_lines(self, fig=None, ax=None, is_show_fig=True):
        """Plot the SurfLine-Contour in a matplotlib fig
        (For plotting unclosed contour, for Polygon use plot method from Surface object)

        Parameters
        ----------
        self : SurfLine
            A SurfLine object
        fig : Matplotlib.figure.Figure
            existing figure to use if None create a new one
        ax : Matplotlib.axes.Axes object
            Axis on which to plot the data
        is_show_fig : bool
            To call show at the end of the method

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

        for line in self.line_list:
            line.plot(fig=fig, ax=ax)

        # Axis Setup
        ax.axis("equal")

        if is_show_fig:
            fig.show()
        return fig, ax

    # cf Methods.Geometry.SurfLine.rotate
    def rotate(self, angle):
        """Rotate the surface

        Parameters
        ----------
        self : SurfLine
            A SurfLine object

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
        for line in self.line_list:
            line.rotate(angle)
        if self.point_ref is not None:
            self.point_ref = self.point_ref * exp(1j * angle)

    # cf Methods.Geometry.SurfLine.scale
    def scale(self, scale_factor):
        """Scale the coordinates of the lines

        Parameters
        ----------
        self : SurfLine
            A SurfLine Object
        scale_factor : float
            the Scale factor [-]

        Returns
        -------
        None
        """

        for line in self.line_list:
            line.scale(scale_factor)
        self.point_ref = self.point_ref * scale_factor

    # cf Methods.Geometry.SurfLine.translate
    def translate(self, Zt):
        """Translate the surface

        Parameters
        ----------
        self : SurfLine
            A SurfLine object

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

        # Translation  of every line in the Surface
        for line in self.line_list:
            line.translate(Zt)

        if self.point_ref is not None:
            self.point_ref += Zt

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self, line_list=-1, point_ref=0, label="", init_dict=None, init_str=None
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
            if "line_list" in list(init_dict.keys()):
                line_list = init_dict["line_list"]
            if "point_ref" in list(init_dict.keys()):
                point_ref = init_dict["point_ref"]
            if "label" in list(init_dict.keys()):
                label = init_dict["label"]
        # Set the properties (value check and convertion are done in setter)
        self.line_list = line_list
        # Call Surface init
        super(SurfLine, self).__init__(point_ref=point_ref, label=label)
        # The class is frozen (in Surface init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        SurfLine_str = ""
        # Get the properties inherited from Surface
        SurfLine_str += super(SurfLine, self).__str__()
        if len(self.line_list) == 0:
            SurfLine_str += "line_list = []" + linesep
        for ii in range(len(self.line_list)):
            tmp = (
                self.line_list[ii].__str__().replace(linesep, linesep + "\t") + linesep
            )
            SurfLine_str += "line_list[" + str(ii) + "] =" + tmp + linesep + linesep
        return SurfLine_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from Surface
        if not super(SurfLine, self).__eq__(other):
            return False
        if other.line_list != self.line_list:
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
            super(SurfLine, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
        if (other.line_list is None and self.line_list is not None) or (
            other.line_list is not None and self.line_list is None
        ):
            diff_list.append(name + ".line_list None mismatch")
        elif self.line_list is None:
            pass
        elif len(other.line_list) != len(self.line_list):
            diff_list.append("len(" + name + ".line_list)")
        else:
            for ii in range(len(other.line_list)):
                diff_list.extend(
                    self.line_list[ii].compare(
                        other.line_list[ii],
                        name=name + ".line_list[" + str(ii) + "]",
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
        S += super(SurfLine, self).__sizeof__()
        if self.line_list is not None:
            for value in self.line_list:
                S += getsizeof(value)
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
        SurfLine_dict = super(SurfLine, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        if self.line_list is None:
            SurfLine_dict["line_list"] = None
        else:
            SurfLine_dict["line_list"] = list()
            for obj in self.line_list:
                if obj is not None:
                    SurfLine_dict["line_list"].append(
                        obj.as_dict(
                            type_handle_ndarray=type_handle_ndarray,
                            keep_function=keep_function,
                            **kwargs
                        )
                    )
                else:
                    SurfLine_dict["line_list"].append(None)
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        SurfLine_dict["__class__"] = "SurfLine"
        return SurfLine_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        if self.line_list is None:
            line_list_val = None
        else:
            line_list_val = list()
            for obj in self.line_list:
                line_list_val.append(obj.copy())
        point_ref_val = self.point_ref
        label_val = self.label
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(
            line_list=line_list_val, point_ref=point_ref_val, label=label_val
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.line_list = None
        # Set to None the properties inherited from Surface
        super(SurfLine, self)._set_None()

    def _get_line_list(self):
        """getter of line_list"""
        if self._line_list is not None:
            for obj in self._line_list:
                if obj is not None:
                    obj.parent = self
        return self._line_list

    def _set_line_list(self, value):
        """setter of line_list"""
        if type(value) is list:
            for ii, obj in enumerate(value):
                if isinstance(obj, str):  # Load from file
                    try:
                        obj = load_init_dict(obj)[1]
                    except Exception as e:
                        self.get_logger().error(
                            "Error while loading " + obj + ", setting None instead"
                        )
                        obj = None
                        value[ii] = None
                if type(obj) is dict:
                    class_obj = import_class(
                        "pyleecan.Classes", obj.get("__class__"), "line_list"
                    )
                    value[ii] = class_obj(init_dict=obj)
                if value[ii] is not None:
                    value[ii].parent = self
        if value == -1:
            value = list()
        check_var("line_list", value, "[Line]")
        self._line_list = value

    line_list = property(
        fget=_get_line_list,
        fset=_set_line_list,
        doc="""List of Lines 

        :Type: [Line]
        """,
    )
