# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Geometry/Arc3.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Geometry/Arc3
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
from pyleecan.Classes.Arc import Arc

# Import all class method
# Try/catch to remove unnecessary dependencies in unused method
from pyleecan.Methods.Geometry.Arc3.check import check
import numpy as np
from pyleecan.Methods.Machine import ARC_NPOINT_D
from pyleecan.Methods.Geometry.Arc3 import (
    NbPointArc3DError,
    AngleRotationArc3Error,
    PointTranslateArc3Error,
)
from pyleecan.Classes.Arc2 import Arc2
from pyleecan.Classes.Arc1 import Arc1


from pyleecan.Classes._check import InitUnKnowClassError


class Arc3(Arc):
    """Half circle define by two points"""

    VERSION = 1

    # cf Methods.Geometry.Arc3.check
    check = check

    # cf Methods.Geometry.Arc3.comp_length
    def comp_length(self):
        """Compute the length of the arc

        Parameters
        ----------
        self : Arc3
            An Arc3 object

        Returns
        -------
        length: float
            length of the arc
        """

        self.check()

        R = self.comp_radius()

        # Half circle
        return float(np.pi * R)

    # cf Methods.Geometry.Arc3.comp_radius
    def comp_radius(self):
        """Compute the radius of the arc

        Parameters
        ----------
        self : Arc3
            An Arc3 object

        Returns
        -------
        radius: float
            radius of the arc

        """

        self.check()

        z1 = self.begin
        z2 = self.end

        return np.abs(z1 - z2) / 2.0  # Radius of the arc

    # cf Methods.Geometry.Arc3.discretize
    def discretize(self, nb_point=ARC_NPOINT_D):
        """Return the discretize version of the Arc.
        Begin and end are always return

        Parameters
        ----------
        self : Arc3
            An Arc3 object
        nb_point : int
            Number of points to add to discretize the arc (Default value = ARC_NPOINT_D)

        Returns
        -------
        list_point: list
            list of complex coordinate of the points

        Raises
        ------
        NbPointArc1DError
            nb_point must be an integer >=0
        """

        # Check that the Arc is correct
        self.check()
        if not isinstance(nb_point, int):
            raise NbPointArc3DError("discretize : nb_point must be an integer")
        if nb_point < 0:
            raise NbPointArc3DError("nb_point must be >=0")

        # We use the complex representation of the point
        z1 = self.begin
        zc = self.get_center()
        R = self.comp_radius()

        # Generation of the point by rotation
        if self.is_trigo_direction:  # Top
            t = np.linspace(0, np.pi, nb_point + 2)
        else:  # Bottom
            t = np.linspace(0, -np.pi, nb_point + 2)
        list_point = R * np.exp(1j * t)

        # Geometric transformation : return to the main axis
        list_point = list_point * np.exp(1j * np.angle(z1 - zc)) + zc

        return list_point

    # cf Methods.Geometry.Arc3.get_angle
    def get_angle(self, is_deg=False):
        """Return the angle of the arc

        Parameters
        ----------
        self : Arc3
            An Arc3 object
        is_deg: bool
            True to convert to degree

        Returns
        -------
        angle: float
            Angle of the arc
        """

        if self.is_trigo_direction:
            sign = 1
        else:
            sign = -1

        if is_deg:
            return sign * 180
        else:
            return sign * np.pi

    # cf Methods.Geometry.Arc3.get_begin
    def get_begin(self):
        """Return the begin point of the arc

        Parameters
        ----------
        self : Arc3
            An Arc3 object

        Returns
        -------
        begin: complex
            Begin point of the Arc3
        """

        return self.begin

    # cf Methods.Geometry.Arc3.get_center
    def get_center(self):
        """Return the center of the arc

        Parameters
        ----------
        self : Arc3
            An Arc3 object

        Returns
        -------
        Zc: complex
            Complex coordinates of the center of the Arc3
        """

        self.check()

        # the center is on the bisection of [begin, end]
        z1 = self.begin
        z2 = self.end

        Zc = (z1 + z2) / 2.0

        # Return (0,0) if the point is too close from 0
        if np.abs(Zc) < 1e-6:
            Zc = 0

        return Zc

    # cf Methods.Geometry.Arc3.get_end
    def get_end(self):
        """Return the end point of the arc

        Parameters
        ----------
        self : Arc3
            An Arc3 object

        Returns
        -------
        end: complex
            Complex coordinates of the end point of the Arc3
        """

        return self.end

    # cf Methods.Geometry.Arc3.get_middle
    def get_middle(self):
        """Return the point at the middle of the arc

        Parameters
        ----------
        self : Arc3
            An Arc3 object

        Returns
        -------
        Zmid: complex
            Complex coordinates of the middle of the Arc3
        """

        # We use the complex representation of the point
        z1 = self.begin
        zc = self.get_center()
        R = self.comp_radius()

        # Generation of the point by rotation
        if self.is_trigo_direction:  # Top
            Zmid = R * np.exp(1j * np.pi / 2.0)
        else:  # Bottom
            Zmid = R * np.exp(-1j * np.pi / 2.0)

        # Geometric transformation : return to the main axis
        Zmid = Zmid * np.exp(1j * np.angle(z1 - zc)) + zc

        # Return (0,0) if the point is too close from 0
        if np.abs(Zmid) < 1e-6:
            Zmid = 0

        return Zmid

    # cf Methods.Geometry.Arc3.reverse
    def reverse(self):
        """Reverse the begin and end point of the Line

        Parameters
        ----------
        self : Arc3
            An Arc3 object

        Returns
        -------
        """

        end = self.end
        self.end = self.begin
        self.begin = end
        self.is_trigo_direction = not self.is_trigo_direction

    # cf Methods.Geometry.Arc3.rotate
    def rotate(self, angle):
        """Rotation of the Arc3 of angle

        Parameters
        ----------
        self : Arc3
            An Arc3 Object

        angle : float
            the angle of rotation [rad]


        Returns
        -------
        None
        """
        if not isinstance(angle, float) and not isinstance(angle, int):
            raise AngleRotationArc3Error("The angle must be a float or int ")

        # check if Arc3 is correct"
        self.check()

        # Modification from the rotation  of the object
        self.begin = self.begin * np.exp(1j * angle)
        self.end = self.end * np.exp(1j * angle)

    # cf Methods.Geometry.Arc3.scale
    def scale(self, scale_factor):
        """Scale the coordinates of the begin/end

        Parameters
        ----------
        self : Arc3
            An Arc3 Object
        scale_factor : float
            the Scale factor [-]

        Returns
        -------
        None
        """

        self.begin = self.begin * scale_factor
        self.end = self.end * scale_factor

    # cf Methods.Geometry.Arc3.split_half
    def split_half(self, is_begin=True):
        """Cut the line in half (modify the object Arc3 => Arc2)

        Parameters
        ----------
        self : Arc3
            An Arc3 object
        is_begin : bool
            True to keep the part begin=>middle, False for the part middle=>end

        Returns
        -------
        """

        if self.is_trigo_direction:
            sign = 1
        else:
            sign = -1

        if is_begin:
            arc = Arc2(
                begin=self.begin, center=self.get_center(), angle=sign * np.pi / 2
            )
        else:
            arc = Arc2(
                begin=self.get_middle(),
                center=self.get_center(),
                angle=sign * np.pi / 2,
            )
        # Change the object type from Arc3 => Arc2
        self.__class__ = Arc2
        self.__dict__.update(arc.__dict__)

    # cf Methods.Geometry.Arc3.split_point
    def split_point(self, Z1, is_begin=True):
        """Cut the Arc according to a point on the arc

        Parameters
        ----------
        self : Arc3
            An Arc3 object
        Z1 : complex
            Cutting point on the line
        is_begin : bool
            True to keep the part begin=>Z1, False for the part Z1=>end

        Returns
        -------
        """

        # Check if the point is on the circle
        Zc = self.get_center()
        R = self.comp_radius()
        if abs(np.abs(Z1 - Zc) - R) > 1e-6:
            raise Exception("Point is not on the line")

        if is_begin:
            arc = Arc1(
                begin=self.begin,
                end=Z1,
                radius=R,
                is_trigo_direction=self.is_trigo_direction,
            )
        else:
            arc = Arc1(
                begin=Z1,
                end=self.end,
                radius=R,
                is_trigo_direction=self.is_trigo_direction,
            )
        # Correct radius sign if needed
        if arc.get_angle() > np.pi:
            arc.radius *= -1

        # Change the object type from Arc3 => Arc1
        self.__class__ = Arc1
        self.__dict__.update(arc.__dict__)

    # cf Methods.Geometry.Arc3.translate
    def translate(self, Zt):
        """Translate the Arc3 object with

        Parameters
        ----------
        self : Arc3
            An Arc3 object

        Zt : complex
            Complex value for translation


        Returns
        -------
        None

        """
        if (
            not isinstance(Zt, complex)
            and not isinstance(Zt, int)
            and not isinstance(Zt, float)
        ):
            raise PointTranslateArc3Error(
                "The point must be a complex number or int or float"
            )

        # check if the Arc3 is correct
        self.check()

        # Modification from the translation of Arc3
        self.begin = self.begin + Zt
        self.end = self.end + Zt

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        begin=0,
        end=0,
        is_trigo_direction=True,
        prop_dict=None,
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
            if "begin" in list(init_dict.keys()):
                begin = init_dict["begin"]
            if "end" in list(init_dict.keys()):
                end = init_dict["end"]
            if "is_trigo_direction" in list(init_dict.keys()):
                is_trigo_direction = init_dict["is_trigo_direction"]
            if "prop_dict" in list(init_dict.keys()):
                prop_dict = init_dict["prop_dict"]
        # Set the properties (value check and convertion are done in setter)
        self.begin = begin
        self.end = end
        self.is_trigo_direction = is_trigo_direction
        # Call Arc init
        super(Arc3, self).__init__(prop_dict=prop_dict)
        # The class is frozen (in Arc init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        Arc3_str = ""
        # Get the properties inherited from Arc
        Arc3_str += super(Arc3, self).__str__()
        Arc3_str += "begin = " + str(self.begin) + linesep
        Arc3_str += "end = " + str(self.end) + linesep
        Arc3_str += "is_trigo_direction = " + str(self.is_trigo_direction) + linesep
        return Arc3_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from Arc
        if not super(Arc3, self).__eq__(other):
            return False
        if other.begin != self.begin:
            return False
        if other.end != self.end:
            return False
        if other.is_trigo_direction != self.is_trigo_direction:
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()

        # Check the properties inherited from Arc
        diff_list.extend(
            super(Arc3, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
        if other._begin != self._begin:
            if is_add_value:
                val_str = (
                    " (self=" + str(self._begin) + ", other=" + str(other._begin) + ")"
                )
                diff_list.append(name + ".begin" + val_str)
            else:
                diff_list.append(name + ".begin")
        if other._end != self._end:
            if is_add_value:
                val_str = (
                    " (self=" + str(self._end) + ", other=" + str(other._end) + ")"
                )
                diff_list.append(name + ".end" + val_str)
            else:
                diff_list.append(name + ".end")
        if other._is_trigo_direction != self._is_trigo_direction:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._is_trigo_direction)
                    + ", other="
                    + str(other._is_trigo_direction)
                    + ")"
                )
                diff_list.append(name + ".is_trigo_direction" + val_str)
            else:
                diff_list.append(name + ".is_trigo_direction")
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from Arc
        S += super(Arc3, self).__sizeof__()
        S += getsizeof(self.begin)
        S += getsizeof(self.end)
        S += getsizeof(self.is_trigo_direction)
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

        # Get the properties inherited from Arc
        Arc3_dict = super(Arc3, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        if self.begin is None:
            Arc3_dict["begin"] = None
        elif isinstance(self.begin, float):
            Arc3_dict["begin"] = self.begin
        else:
            Arc3_dict["begin"] = str(self.begin)
        if self.end is None:
            Arc3_dict["end"] = None
        elif isinstance(self.end, float):
            Arc3_dict["end"] = self.end
        else:
            Arc3_dict["end"] = str(self.end)
        Arc3_dict["is_trigo_direction"] = self.is_trigo_direction
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        Arc3_dict["__class__"] = "Arc3"
        return Arc3_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        begin_val = self.begin
        end_val = self.end
        is_trigo_direction_val = self.is_trigo_direction
        if self.prop_dict is None:
            prop_dict_val = None
        else:
            prop_dict_val = self.prop_dict.copy()
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(
            begin=begin_val,
            end=end_val,
            is_trigo_direction=is_trigo_direction_val,
            prop_dict=prop_dict_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.begin = None
        self.end = None
        self.is_trigo_direction = None
        # Set to None the properties inherited from Arc
        super(Arc3, self)._set_None()

    def _get_begin(self):
        """getter of begin"""
        return self._begin

    def _set_begin(self, value):
        """setter of begin"""
        if isinstance(value, str):
            value = complex(value)
        check_var("begin", value, "complex")
        self._begin = value

    begin = property(
        fget=_get_begin,
        fset=_set_begin,
        doc="""begin point of the arc

        :Type: complex
        """,
    )

    def _get_end(self):
        """getter of end"""
        return self._end

    def _set_end(self, value):
        """setter of end"""
        if isinstance(value, str):
            value = complex(value)
        check_var("end", value, "complex")
        self._end = value

    end = property(
        fget=_get_end,
        fset=_set_end,
        doc="""end of the arc

        :Type: complex
        """,
    )

    def _get_is_trigo_direction(self):
        """getter of is_trigo_direction"""
        return self._is_trigo_direction

    def _set_is_trigo_direction(self, value):
        """setter of is_trigo_direction"""
        check_var("is_trigo_direction", value, "bool")
        self._is_trigo_direction = value

    is_trigo_direction = property(
        fget=_get_is_trigo_direction,
        fset=_set_is_trigo_direction,
        doc="""Rotation direction of the arc

        :Type: bool
        """,
    )
