# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Geometry/PolarArc.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Geometry/PolarArc
"""

# Inline fallback report:
# These methods remain imported because their source or imports cannot be safely moved into this class.
# - check: module uses a wildcard import whose names cannot be resolved safely

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
from pyleecan.Methods.Geometry.PolarArc.check import check
from numpy import pi, angle, exp
from pyleecan.Methods.Geometry.PolarArc.discretize import NbPointPolarArcError
from pyleecan.Classes.Arc1 import Arc1
from pyleecan.Classes.Segment import Segment
from pyleecan.Methods.Geometry.PolarArc.get_patches import (
    PATCH_COLOR,
    PATCH_COLOR_ALPHA,
    PATCH_EDGE,
    PATCH_EDGE_ALPHA,
)
from matplotlib.patches import Polygon

from numpy import isnan
from pyleecan.Classes._check import InitUnKnowClassError


class PolarArc(Surface):
    """PolarArc defined by  the center of object(point_ref), the label, the angle and the height"""

    VERSION = 1

    # cf Methods.Geometry.PolarArc.check
    check = check

    # cf Methods.Geometry.PolarArc.comp_length
    # -*-- coding: utf-8 -*
    def comp_length(self):
        """Returns the length of the PolarArc

        Parameters
        ----------
        self : PolarArc
            a PolarArc object


        Returns
        -------
        length : float
            length of the PolarArc [m]
        """
        # check if the PolarArc is correct
        self.check()

        lines = self.get_lines()
        length = 0
        for line in lines:
            length += line.comp_length()
        return length

    # cf Methods.Geometry.PolarArc.comp_point_ref
    def comp_point_ref(self, is_set=False):
        """Compute the point ref of the Surface

        Parameters
        ----------
        self : PolarArc
            A PolarArc object
        is_set: bool
            True to update the point_ref property

        Returns
        -------
        point_ref : complex
            the reference point of the surface
        """

        point_ref = self.point_ref
        if is_set:
            self.point_ref = point_ref
        return point_ref

    # cf Methods.Geometry.PolarArc.comp_surface
    def comp_surface(self):
        """Compute the PolarArc surface

        Parameters
        ----------
        self : PolarArc
            A PolarArc object

        Returns
        -------
        surf: float
            The PolarArc surface [m**2]

        """

        Rint = abs(self.point_ref) - self.height / 2
        Rext = Rint + self.height

        return (pi * Rext**2 - pi * Rint**2) * (self.angle / (2 * pi))

    # cf Methods.Geometry.PolarArc.discretize
    # -*-- coding: utf-8 -*
    def discretize(self, nb_point):
        """Returns the discretize version of the PolarArc

        Parameters
        ----------
        nb_point : int
            number of points wanted per line

        Returns
        -------
        point_list : list
            List of complex coordinate of the points

        """
        # check if the PolarArc is correct
        self.check()

        if not isinstance(nb_point, int):
            raise NbPointPolarArcError("Discretize : the nb_point must be an integer")
        if nb_point < 0:
            raise NbPointPolarArcError("Discretize: nb_point must be >= 0")

        # getting lines that delimit the PolarArc
        lines = self.get_lines()
        point_list = list()
        for line in lines:
            point_list.extend(line.discretize(nb_point))
            # The begin of the next line is the end of the current one
            point_list.pop()
        return point_list

    # cf Methods.Geometry.PolarArc.get_lines
    def get_lines(self):
        """return the list of lines that delimits the PolarArc

        Parameters
        ----------
        self : PolarArc
            a PolarArc object

        Returns
        -------
        line_list: list
            List of line need to draw the slot (2 Segment + 2 Arc1)
        """
        # check if the PolarArc is correct
        self.check()

        Z_ref = self.point_ref
        center = Z_ref * exp(-1j * angle(Z_ref))
        H = self.height
        A = self.angle
        # the points of the PolarArc
        Z2 = (center - (H / 2)) * exp(1j * (-(A / 2))) * exp(1j * angle(Z_ref))
        Z3 = (center + (H / 2)) * exp(1j * (-(A / 2))) * exp(1j * angle(Z_ref))
        Z4 = (center + (H / 2)) * exp(1j * (A / 2)) * exp(1j * angle(Z_ref))
        Z1 = (center - (H / 2)) * exp(1j * (A / 2)) * exp(1j * angle(Z_ref))

        # Lines that delimit the PolarArc
        line1 = Arc1(Z1, Z2, -abs(Z1), is_trigo_direction=False)
        line2 = Segment(Z2, Z3)
        line3 = Arc1(Z3, Z4, abs(Z3))
        line4 = Segment(Z4, Z1)

        return [line1, line2, line3, line4]

    # cf Methods.Geometry.PolarArc.get_patches
    def get_patches(
        self, color=PATCH_COLOR, edgecolor=None, is_edge_only=False, linestyle=None
    ):
        """Returns the PolarArc Patch to be display in matplotlib
        Parameters
        ----------
        self : PolarArc
            a PolarArc object
        color :
            The color of the patch (Default value = PATCH_COLOR)
        edgecolor :
            The color of the edgecolor (Default value = PATCH_EDGE)
        is_edge_only: bool
            To set the transparancy of the face color to 0 and 1 for the edge color
        linestyle : str
            Line style of the edge {'-', '--', '-.', ':', '', (offset, on-off-seq), ...}

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

        # check if the PolarArc is correct
        self.check()

        line_list = self.get_lines()
        Z_list = list()
        # For each  Line discretize
        for line in line_list:
            Z_list.extend(line.discretize())

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
                point_list, facecolor=color, edgecolor=edgecolor, linestyle=linestyle
            )
        ]

    # cf Methods.Geometry.PolarArc.rotate
    def rotate(self, angle):
        """Do the rotation of the PolarArc

        Parameters
        ----------
        self : PolarArc
            a PolarArc
        angle : float
            the angle for rotation [rad]

        Returns
        -------
        None
        """
        if angle == 0:
            return  # Nothing to do
        # check if the PolarArc is correct
        self.check()
        self.point_ref = self.point_ref * exp(1j * angle)

    # cf Methods.Geometry.PolarArc.translate
    def translate(self, Zt):
        """Do the translation of the PolarArc

        Parameters
        ----------
        self : PolarArc
            a PolarArc object

        Zt : complex
            Complex value for translation

        Returns
        -------
        None
        """
        if Zt == 0:
            return  # Nothing to do
        # check if the PolarArc is correct
        self.check()
        self.point_ref += Zt

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self, angle=1, height=1, point_ref=0, label="", init_dict=None, init_str=None
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
            if "angle" in list(init_dict.keys()):
                angle = init_dict["angle"]
            if "height" in list(init_dict.keys()):
                height = init_dict["height"]
            if "point_ref" in list(init_dict.keys()):
                point_ref = init_dict["point_ref"]
            if "label" in list(init_dict.keys()):
                label = init_dict["label"]
        # Set the properties (value check and convertion are done in setter)
        self.angle = angle
        self.height = height
        # Call Surface init
        super(PolarArc, self).__init__(point_ref=point_ref, label=label)
        # The class is frozen (in Surface init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        PolarArc_str = ""
        # Get the properties inherited from Surface
        PolarArc_str += super(PolarArc, self).__str__()
        PolarArc_str += "angle = " + str(self.angle) + linesep
        PolarArc_str += "height = " + str(self.height) + linesep
        return PolarArc_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from Surface
        if not super(PolarArc, self).__eq__(other):
            return False
        if other.angle != self.angle:
            return False
        if other.height != self.height:
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
            super(PolarArc, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
        if (
            other._angle is not None
            and self._angle is not None
            and isnan(other._angle)
            and isnan(self._angle)
        ):
            pass
        elif other._angle != self._angle:
            if is_add_value:
                val_str = (
                    " (self=" + str(self._angle) + ", other=" + str(other._angle) + ")"
                )
                diff_list.append(name + ".angle" + val_str)
            else:
                diff_list.append(name + ".angle")
        if (
            other._height is not None
            and self._height is not None
            and isnan(other._height)
            and isnan(self._height)
        ):
            pass
        elif other._height != self._height:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._height)
                    + ", other="
                    + str(other._height)
                    + ")"
                )
                diff_list.append(name + ".height" + val_str)
            else:
                diff_list.append(name + ".height")
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from Surface
        S += super(PolarArc, self).__sizeof__()
        S += getsizeof(self.angle)
        S += getsizeof(self.height)
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
        PolarArc_dict = super(PolarArc, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        PolarArc_dict["angle"] = self.angle
        PolarArc_dict["height"] = self.height
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        PolarArc_dict["__class__"] = "PolarArc"
        return PolarArc_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        angle_val = self.angle
        height_val = self.height
        point_ref_val = self.point_ref
        label_val = self.label
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(
            angle=angle_val, height=height_val, point_ref=point_ref_val, label=label_val
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.angle = None
        self.height = None
        # Set to None the properties inherited from Surface
        super(PolarArc, self)._set_None()

    def _get_angle(self):
        """getter of angle"""
        return self._angle

    def _set_angle(self, value):
        """setter of angle"""
        check_var("angle", value, "float", Vmin=0)
        self._angle = value

    angle = property(
        fget=_get_angle,
        fset=_set_angle,
        doc="""Polar angle

        :Type: float
        :min: 0
        """,
    )

    def _get_height(self):
        """getter of height"""
        return self._height

    def _set_height(self, value):
        """setter of height"""
        check_var("height", value, "float", Vmin=0)
        self._height = value

    height = property(
        fget=_get_height,
        fset=_set_height,
        doc="""The Heigth of the PolarAngle

        :Type: float
        :min: 0
        """,
    )
