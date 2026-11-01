# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Geometry/Circle.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Geometry/Circle
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
from pyleecan.Methods.Geometry.Circle import RadiusCircleError
import numpy as np
from pyleecan.Classes.Arc3 import Arc3
from matplotlib.patches import Circle
from pyleecan.definitions import config_dict
from pyleecan.Methods.Geometry.Circle import (
    AngleRotationCircleError,
    PointTranslateCircleError,
)


from pyleecan.Classes._check import InitUnKnowClassError


class Circle(Surface):
    """Circle define by  the center of circle(point_ref), the label and the radius"""

    VERSION = 1
    PATCH_EDGE = config_dict["PLOT"]["COLOR_DICT"]["PATCH_EDGE"]
    PATCH_COLOR = config_dict["PLOT"]["COLOR_DICT"]["PATCH_COLOR"]
    PATCH_COLOR_ALPHA = config_dict["PLOT"]["COLOR_DICT"]["PATCH_COLOR_ALPHA"]
    PATCH_EDGE_ALPHA = config_dict["PLOT"]["COLOR_DICT"]["PATCH_EDGE_ALPHA"]

    # cf Methods.Geometry.Circle.check
    def check(self):
        """assert the Circle is correct (the radius > 0)

        Parameters
        ----------
        self : Circle
            A Circle object

        Returns
        -------
        None

        Raises
        ------
        RadiusCircleError
            The radius of a circle must be >=  0

        """
        if self.radius < 0:
            raise RadiusCircleError("The radius of a circle must be >= 0")

    # cf Methods.Geometry.Circle.comp_length
    def comp_length(self):
        """Compute the length of the circle

        Parameters
        ----------
        self : Circle
            A Circle object

        Returns
        -------
        length : float
            the length of the circle [m]

        """
        # Check if the circle is correct
        self.check()

        length = self.radius * 2 * np.pi

        return length

    # cf Methods.Geometry.Circle.comp_point_ref
    def comp_point_ref(self, is_set=False):
        """Compute the point ref of the Surface

        Parameters
        ----------
        self : Circle
            A Circle object
        is_set: bool
            True to update the point_ref property

        Returns
        -------
        point_ref : complex
            the reference point of the surface
        """

        point_ref = self.center
        if is_set:
            self.point_ref = point_ref
        return point_ref

    # cf Methods.Geometry.Circle.comp_surface
    def comp_surface(self):
        """Compute the circle surface

        Parameters
        ----------
        self : Circle
            A Circle object

        Returns
        -------
        surf: float
            The circle surface [m**2]

        """

        return np.pi * self.radius**2

    # cf Methods.Geometry.Circle.discretize
    def discretize(self):
        """Return the discretize version of the Circle.

        Parameters
        ----------
        self : Circle
            A Circle Object

        nb_point : int
            Number of point on the circle

        Returns
        -------
        point_list : list
            List of complex coordinate of the points

        """

        # check if the Circle is correct
        self.check()

        # getting Arc which delimit the Circle
        lines = self.get_lines()
        point_list = list()
        for line in lines:
            point_list.extend(line.discretize())
            point_list.pop()
        return point_list

    # cf Methods.Geometry.Circle.get_lines
    def get_lines(self):
        """Get the lines needed to draw the surface (2 Arc3)

        Parameters
        ----------
        self : Circle
            A circle Object

        Returns
        -------
        line_list: list
            Two arcs to draw the circle

        """
        # check if the circle is correct
        self.check()
        begin = self.center + self.radius
        end = self.center - self.radius
        # first half-circle
        line1 = Arc3(begin, end, True, prop_dict=self.prop_dict)
        # second half-circle
        line2 = Arc3(end, begin, True, prop_dict=self.prop_dict)
        return [line1, line2]

    # cf Methods.Geometry.Circle.get_patches
    def get_patches(
        self, color=None, edgecolor=None, is_edge_only=False, linestyle=None
    ):
        """Returns the Circle Patch to be display in matplotlib

        Parameters
        ----------
        self : Circle
            a Circle object
        color :
            the color of the Patch (Default value = PATCH_COLOR)
        edgecolor :
            edgecolor of the Patch (Default value = PATCH_EDGE)
        is_edge_only: bool
            To set the transparancy of the face color to 0 and 1 for the edge color
        linestyle : str
            Line style of the edge {'-', '--', '-.', ':', '', (offset, on-off-seq), ...}

        Returns
        -------
        patch_list : list of matplotlib.patches.Circle
            List of patches corresponding to the surface
        """

        # Set default color
        if edgecolor is None and not is_edge_only:
            edgecolor = self.PATCH_EDGE
        elif edgecolor is None and is_edge_only:
            edgecolor = self.PATCH_EDGE_ALPHA
        if is_edge_only:
            color = self.PATCH_COLOR_ALPHA
        if "--" in edgecolor:
            edgecolor = edgecolor.replace("-", "")
            linestyle = "--"

        # check if the Circle is correct
        self.check()
        # the coordinates of the center of the circle
        Zr = self.center.real
        Zi = self.center.imag

        return [
            Circle(
                xy=(Zr, Zi),
                radius=self.radius,
                facecolor=color,
                edgecolor=edgecolor,
                linestyle=linestyle,
            )
        ]

    get_patches.__defaults__ = (
        get_patches.__defaults__[:0] + (PATCH_COLOR,) + get_patches.__defaults__[1:]
    )

    # cf Methods.Geometry.Circle.rotate
    def rotate(self, angle):
        """Rotation of the Circle of angle

        Parameters
        ----------
        self : Circle
            An Circle Object

        angle : float
            the angle of rotation [rad]

        Returns
        -------
        None

        Raises
        -------
        AngleRotationCircleError
            The angle must be a float or int
        """
        if not isinstance(angle, float) and not isinstance(angle, int):
            raise AngleRotationCircleError("The angle must be a float or int ")

        if angle == 0:
            return  # Nothing to do
        # check if Circle is correct"
        self.check()

        # Modification of the object from the rotation
        self.center = self.center * np.exp(1j * angle)
        if self.point_ref is not None:
            self.point_ref = self.point_ref * np.exp(1j * angle)

    # cf Methods.Geometry.Circle.translate
    def translate(self, Zt):
        """Translate the Circle object

        Parameters
        ----------
        self : Circle
            An Circle object

        Zt : complex
            Complex value for translation


        Returns
        -------
        None

        Raises
        -------
        PointTranslateCircleError
            The point must be a complex number or int or float

        """
        if (
            not isinstance(Zt, complex)
            and not isinstance(Zt, int)
            and not isinstance(Zt, float)
        ):
            raise PointTranslateCircleError(
                "The point must be a complex number or int or float"
            )

        if Zt == 0:
            return  # Nothing to do

        # check if the Circle is correct
        self.check()

        # Modification from the translation of Circle
        if self.point_ref is not None:
            self.point_ref = self.point_ref + Zt
        self.center = self.center + Zt

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        radius=1,
        center=0,
        prop_dict=-1,
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
            if "radius" in list(init_dict.keys()):
                radius = init_dict["radius"]
            if "center" in list(init_dict.keys()):
                center = init_dict["center"]
            if "prop_dict" in list(init_dict.keys()):
                prop_dict = init_dict["prop_dict"]
            if "point_ref" in list(init_dict.keys()):
                point_ref = init_dict["point_ref"]
            if "label" in list(init_dict.keys()):
                label = init_dict["label"]
        # Set the properties (value check and convertion are done in setter)
        self.radius = radius
        self.center = center
        self.prop_dict = prop_dict
        # Call Surface init
        super(Circle, self).__init__(point_ref=point_ref, label=label)
        # The class is frozen (in Surface init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        Circle_str = ""
        # Get the properties inherited from Surface
        Circle_str += super(Circle, self).__str__()
        Circle_str += "radius = " + str(self.radius) + linesep
        Circle_str += "center = " + str(self.center) + linesep
        Circle_str += "prop_dict = " + str(self.prop_dict) + linesep
        return Circle_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from Surface
        if not super(Circle, self).__eq__(other):
            return False
        if other.radius != self.radius:
            return False
        if other.center != self.center:
            return False
        if other.prop_dict != self.prop_dict:
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
            super(Circle, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
        if (
            other._radius is not None
            and self._radius is not None
            and np.isnan(other._radius)
            and np.isnan(self._radius)
        ):
            pass
        elif other._radius != self._radius:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._radius)
                    + ", other="
                    + str(other._radius)
                    + ")"
                )
                diff_list.append(name + ".radius" + val_str)
            else:
                diff_list.append(name + ".radius")
        if other._center != self._center:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._center)
                    + ", other="
                    + str(other._center)
                    + ")"
                )
                diff_list.append(name + ".center" + val_str)
            else:
                diff_list.append(name + ".center")
        if other._prop_dict != self._prop_dict:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._prop_dict)
                    + ", other="
                    + str(other._prop_dict)
                    + ")"
                )
                diff_list.append(name + ".prop_dict" + val_str)
            else:
                diff_list.append(name + ".prop_dict")
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from Surface
        S += super(Circle, self).__sizeof__()
        S += getsizeof(self.radius)
        S += getsizeof(self.center)
        if self.prop_dict is not None:
            for key, value in self.prop_dict.items():
                S += getsizeof(value) + getsizeof(key)
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
        Circle_dict = super(Circle, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        Circle_dict["radius"] = self.radius
        if self.center is None:
            Circle_dict["center"] = None
        elif isinstance(self.center, float):
            Circle_dict["center"] = self.center
        else:
            Circle_dict["center"] = str(self.center)
        Circle_dict["prop_dict"] = (
            self.prop_dict.copy() if self.prop_dict is not None else None
        )
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        Circle_dict["__class__"] = "Circle"
        return Circle_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        radius_val = self.radius
        center_val = self.center
        if self.prop_dict is None:
            prop_dict_val = None
        else:
            prop_dict_val = self.prop_dict.copy()
        point_ref_val = self.point_ref
        label_val = self.label
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(
            radius=radius_val,
            center=center_val,
            prop_dict=prop_dict_val,
            point_ref=point_ref_val,
            label=label_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.radius = None
        self.center = None
        self.prop_dict = None
        # Set to None the properties inherited from Surface
        super(Circle, self)._set_None()

    def _get_radius(self):
        """getter of radius"""
        return self._radius

    def _set_radius(self, value):
        """setter of radius"""
        check_var("radius", value, "float", Vmin=0)
        self._radius = value

    radius = property(
        fget=_get_radius,
        fset=_set_radius,
        doc="""Radius of the circle

        :Type: float
        :min: 0
        """,
    )

    def _get_center(self):
        """getter of center"""
        return self._center

    def _set_center(self, value):
        """setter of center"""
        if isinstance(value, str):
            value = complex(value)
        check_var("center", value, "complex")
        self._center = value

    center = property(
        fget=_get_center,
        fset=_set_center,
        doc="""center of the Circle

        :Type: complex
        """,
    )

    def _get_prop_dict(self):
        """getter of prop_dict"""
        return self._prop_dict

    def _set_prop_dict(self, value):
        """setter of prop_dict"""
        if type(value) is int and value == -1:
            value = dict()
        check_var("prop_dict", value, "dict")
        self._prop_dict = value

    prop_dict = property(
        fget=_get_prop_dict,
        fset=_set_prop_dict,
        doc="""Property dict to apply on the lines

        :Type: dict
        """,
    )
