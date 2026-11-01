# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Geometry/Arc1.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Geometry/Arc1
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
from pyleecan.Classes.Arc import Arc

# Import all class method
# Try/catch to remove unnecessary dependencies in unused method
from pyleecan.Methods.Geometry.Arc1 import RadiusArc1Error, PointArc1Error
import numpy as np
from pyleecan.Methods.Machine import ARC_NPOINT_D
from pyleecan.Methods.Geometry.Arc1 import (
    NbPointArc1DError,
    AngleRotationArc1Error,
    PointTranslateArc1Error,
)


from pyleecan.Classes._check import InitUnKnowClassError


class Arc1(Arc):
    """An arc between two points (defined by a radius)"""

    VERSION = 1

    # cf Methods.Geometry.Arc1.check
    def check(self):
        """assert that the arc is correct (begin != end; radius !=0)

        Parameters
        ----------
        self : Arc1
            An Arc1 object

        Returns
        -------
        None

        Raises
        ------
        PointArc1Error
            The beginning point and the ending point of an Arc1
            can't be the same
        RadiusArc1Error
            An Arc1 can't have a null radius

        """

        if self.begin == self.end or (abs(self.begin) == 0 and abs(self.end) == 0):
            raise PointArc1Error(
                "The beginning point and the ending "
                + "point of an Arc1 can't be "
                + "the same"
            )
        if self.radius == 0:
            raise RadiusArc1Error("An Arc1 can't have a null radius")

    # cf Methods.Geometry.Arc1.comp_length
    def comp_length(self):
        """Compute the length of the arc

        Parameters
        ----------
        self : Arc1
            An Arc1 object

        Returns
        -------
        length: float
            length of the arc
        """

        self.check()

        R = abs(self.radius)

        # alpha is the opening angle
        alpha = abs(self.get_angle())

        # 2*pi*R is the length of the total circle
        # The arc is an alpha / 2pi portion of the cercle
        return float(2 * np.pi * R * (alpha / (2 * np.pi)))

    # cf Methods.Geometry.Arc1.comp_radius
    def comp_radius(self):
        """Compute the Radius of the Arc1 (for unification with other arc objects)

        Parameters
        ----------
        self : Arc1
            An Arc1 object

        Returns
        -------
        radius: float
            radius of the arc
        """

        self.check()

        return abs(self.radius)  # Radius of the arc

    # cf Methods.Geometry.Arc1.discretize
    def discretize(self, nb_point=ARC_NPOINT_D):
        """Return the discretize version of the Arc.
        Begin and end are always returned

        Parameters
        ----------
        self : Arc1
            The Arc1 object to discretize
        nb_point :
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
            raise NbPointArc1DError("discretize : nb_point must be an integer")
        if nb_point < 0:
            raise NbPointArc1DError("nb_point must be >=0")

        # We use the complex representation of the point
        z1 = self.begin
        z2 = self.end
        zc = self.get_center()

        # Geometric transformation : center is the origin, angle(begin) = 0
        Zstart = (z1 - zc) * np.exp(-1j * np.angle(z1 - zc))
        Zend = (z2 - zc) * np.exp(-1j * np.angle(z1 - zc))

        # Generation of the point by rotation
        if self.is_trigo_direction:
            sign = 1
        else:
            sign = -1
        t = np.linspace(0, self.get_angle(), nb_point + 2)
        list_point = Zstart * np.exp(1j * t)

        # Geometric transformation : return to the main axis
        list_point = list_point * np.exp(1j * np.angle(z1 - zc)) + zc

        return list_point

    # cf Methods.Geometry.Arc1.get_angle
    def get_angle(self, is_deg=False):
        """Return the angle of the arc

        Parameters
        ----------
        self : Arc1
            An Arc1 object
        is_deg: bool
            True to convert to degree

        Returns
        -------
        angle: float
            Angle of the arc
        """
        # Go to center ref with begin on the X > 0 axis
        Zc = self.get_center()
        Z2 = (self.end - Zc) * np.exp(-1j * np.angle(self.begin - Zc))

        if Z2.imag > 0 and self.is_trigo_direction:
            alpha = np.angle(Z2)
        elif Z2.imag > 0 and not self.is_trigo_direction:
            alpha = -(2 * np.pi - np.angle(Z2))
        elif Z2.imag < 0 and self.is_trigo_direction:
            alpha = 2 * np.pi - abs(np.angle(Z2))
        elif Z2.imag < 0 and not self.is_trigo_direction:
            alpha = np.angle(Z2)
        elif Z2.imag == 0 and self.is_trigo_direction:
            alpha = abs(np.angle(Z2))
        elif Z2.imag == 0 and not self.is_trigo_direction:
            alpha = -abs(np.angle(Z2))
        else:
            alpha = 0

        if is_deg:
            return alpha * 180 / np.pi
        else:
            return alpha

    # cf Methods.Geometry.Arc1.get_begin
    def get_begin(self):
        """Return the begin point of the arc

        Parameters
        ----------
        self : Arc1
            An Arc1 object

        Returns
        -------
        begin: complex
            Complex coordinates of the begin point of the Arc1
        """

        return self.begin

    # cf Methods.Geometry.Arc1.get_center
    def get_center(self):
        """Return the center of the arc

        Parameters
        ----------
        self : Arc1
            An Arc1 object

        Returns
        -------
        Zc: complex
            Complex coordinates of the center of the Arc1
        """

        self.check()

        # The center is on the bisection of [begin, end]
        z1 = self.begin
        z2 = self.end
        R = self.radius
        D12 = np.abs(z2 - z1)  # length of segment [begin,end]

        # Centre at the middle of begin and end (distance(Z1, Z2) = diameter )
        if np.abs(D12 - np.abs(2 * R)) < 1e-6:
            Zc = (z2 + z1) / 2.0
        else:
            # In the coordinate system begin on center and end on X > 0 axis
            if R > 0:  # Center is above the segment
                Zc = D12 / 2 + 1j * np.sqrt(R**2 - (D12 / 2) ** 2)
            else:
                Zc = D12 / 2 - 1j * np.sqrt(R**2 - (D12 / 2) ** 2)
            # Go back to the original coordinate system
            Zc = Zc * np.exp(1j * np.angle(z2 - z1)) + z1

        # Return (0,0) if the point is too close from 0
        if np.abs(Zc) < 1e-6:
            Zc = 0

        return Zc

    # cf Methods.Geometry.Arc1.get_end
    def get_end(self):
        """Return the end point of the arc

        Parameters
        ----------
        self : Arc1
            An Arc1 object

        Returns
        -------
        end: complex
            Complex coordinates of the end point of the Arc1
        """

        return self.end

    # cf Methods.Geometry.Arc1.get_middle
    def get_middle(self):
        """Return the point at the middle of the arc

        Parameters
        ----------
        self : Arc1
            An Arc1 object

        Returns
        -------
        Zmid: complex
            Complex coordinates of the middle of the Arc1
        """

        # We use the complex representation of the point
        z1 = self.begin
        z2 = self.end
        zc = self.get_center()

        # Geometric transformation : center is the origine, angle(begin) = 0
        Zstart = (z1 - zc) * np.exp(-1j * np.angle(z1 - zc))

        # Generation of the point by rotation
        alpha = self.get_angle()
        Zmid = Zstart * np.exp(1j * alpha / 2)

        # Geometric transformation : return to the main axis
        Zmid = Zmid * np.exp(1j * np.angle(z1 - zc)) + zc

        # Return (0,0) if the point is too close from 0
        if np.abs(Zmid) < 1e-6:
            Zmid = 0

        return Zmid

    # cf Methods.Geometry.Arc1.reverse
    def reverse(self):
        """Reverse the begin and end point of the Line

        Parameters
        ----------
        self : Arc1
            An Arc1 object

        Returns
        -------
        """

        end = self.end
        self.end = self.begin
        self.begin = end
        self.radius = -self.radius
        self.is_trigo_direction = not self.is_trigo_direction

    # cf Methods.Geometry.Arc1.rotate
    def rotate(self, angle):
        """Rotation of the Arc1 of <angle> rad with 0 as the center

        Parameters
        ----------
        self : Arc1
            An Arc1 Object

        angle : float
            the angle of rotation [rad]

        Returns
        -------
        None
        """
        if not isinstance(angle, float) and not isinstance(angle, int):
            raise AngleRotationArc1Error("The angle must be a float or int ")

        # check if Arc1 is correct"
        self.check()

        # Modification from the rotation  of the object
        self.begin = self.begin * np.exp(1j * angle)
        self.end = self.end * np.exp(1j * angle)

    # cf Methods.Geometry.Arc1.scale
    def scale(self, scale_factor):
        """Scale the coordinates of the begin/end

        Parameters
        ----------
        self : Arc1
            An Arc1 Object
        scale_factor : float
            the Scale factor [-]

        Returns
        -------
        None
        """

        self.begin = self.begin * scale_factor
        self.end = self.end * scale_factor
        self.radius = self.radius * scale_factor

    # cf Methods.Geometry.Arc1.split_half
    def split_half(self, is_begin=True):
        """Cut the line in half (modify the object)

        Parameters
        ----------
        self : Arc1
            An Arc1 object
        is_begin : bool
            True to keep the part begin=>middle, False for the part middle=>end

        Returns
        -------
        """

        # Check that the center is the same
        Zc = self.get_center()

        if is_begin:
            self.end = self.get_middle()
        else:
            self.begin = self.get_middle()

        # Correct center if needed
        if abs(Zc - self.get_center()) > 1e-6:
            self.radius = -1 * self.radius

    # cf Methods.Geometry.Arc1.split_point
    def split_point(self, Z1, is_begin=True):
        """Cut the Arc according to a point on the arc

        Parameters
        ----------
        self : Arc1
            An Arc1 object
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

        # Check that the center is the same
        if is_begin:
            self.end = Z1
        else:
            self.begin = Z1

        # Correct center if needed
        if abs(Zc - self.get_center()) > 1e-6:
            self.radius = -1 * self.radius

    # cf Methods.Geometry.Arc1.translate
    def translate(self, Zt):
        """Translate the Arc1 object

        Parameters
        ----------
        self : Arc1
            An Arc1 object

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
            raise PointTranslateArc1Error(
                "The point must be a complex number or int or float"
            )

        # check if the Arc1 is correct
        self.check()

        # Modification from the translation of Arc1
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
        radius=0,
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
            if "radius" in list(init_dict.keys()):
                radius = init_dict["radius"]
            if "is_trigo_direction" in list(init_dict.keys()):
                is_trigo_direction = init_dict["is_trigo_direction"]
            if "prop_dict" in list(init_dict.keys()):
                prop_dict = init_dict["prop_dict"]
        # Set the properties (value check and convertion are done in setter)
        self.begin = begin
        self.end = end
        self.radius = radius
        self.is_trigo_direction = is_trigo_direction
        # Call Arc init
        super(Arc1, self).__init__(prop_dict=prop_dict)
        # The class is frozen (in Arc init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        Arc1_str = ""
        # Get the properties inherited from Arc
        Arc1_str += super(Arc1, self).__str__()
        Arc1_str += "begin = " + str(self.begin) + linesep
        Arc1_str += "end = " + str(self.end) + linesep
        Arc1_str += "radius = " + str(self.radius) + linesep
        Arc1_str += "is_trigo_direction = " + str(self.is_trigo_direction) + linesep
        return Arc1_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from Arc
        if not super(Arc1, self).__eq__(other):
            return False
        if other.begin != self.begin:
            return False
        if other.end != self.end:
            return False
        if other.radius != self.radius:
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
            super(Arc1, self).compare(
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
        S += super(Arc1, self).__sizeof__()
        S += getsizeof(self.begin)
        S += getsizeof(self.end)
        S += getsizeof(self.radius)
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
        Arc1_dict = super(Arc1, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        if self.begin is None:
            Arc1_dict["begin"] = None
        elif isinstance(self.begin, float):
            Arc1_dict["begin"] = self.begin
        else:
            Arc1_dict["begin"] = str(self.begin)
        if self.end is None:
            Arc1_dict["end"] = None
        elif isinstance(self.end, float):
            Arc1_dict["end"] = self.end
        else:
            Arc1_dict["end"] = str(self.end)
        Arc1_dict["radius"] = self.radius
        Arc1_dict["is_trigo_direction"] = self.is_trigo_direction
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        Arc1_dict["__class__"] = "Arc1"
        return Arc1_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        begin_val = self.begin
        end_val = self.end
        radius_val = self.radius
        is_trigo_direction_val = self.is_trigo_direction
        if self.prop_dict is None:
            prop_dict_val = None
        else:
            prop_dict_val = self.prop_dict.copy()
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(
            begin=begin_val,
            end=end_val,
            radius=radius_val,
            is_trigo_direction=is_trigo_direction_val,
            prop_dict=prop_dict_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.begin = None
        self.end = None
        self.radius = None
        self.is_trigo_direction = None
        # Set to None the properties inherited from Arc
        super(Arc1, self)._set_None()

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
        doc="""end point of the arc

        :Type: complex
        """,
    )

    def _get_radius(self):
        """getter of radius"""
        return self._radius

    def _set_radius(self, value):
        """setter of radius"""
        check_var("radius", value, "float")
        self._radius = value

    radius = property(
        fget=_get_radius,
        fset=_set_radius,
        doc="""Radius of the arc (can be + or -)

        :Type: float
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
