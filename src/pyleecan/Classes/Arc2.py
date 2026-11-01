# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Geometry/Arc2.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Geometry/Arc2
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
import numpy as np
from pyleecan.Methods.Geometry.Arc2 import AngleArc2Error, PointArc2Error
from pyleecan.Methods.Machine import ARC_NPOINT_D
from pyleecan.Methods.Geometry.Arc2 import (
    NbPointArc2DError,
    AngleRotationArc2Error,
    PointTranslateArc2Error,
)


from pyleecan.Classes._check import InitUnKnowClassError


class Arc2(Arc):
    """An arc between two points (defined by the begin  point and a center and angle)"""

    VERSION = 1

    # cf Methods.Geometry.Arc2.check
    def check(self):
        """assert that the arc is correct (begin != center)

        Parameters
        ----------
        self : Arc2
            An Arc2 object

        Returns
        -------
        None

        Raises
        ------
        PointArc2Error
            The beginning point and the ending point of an Arc2
            can't be the same
        AngleArc2Error
            An Arc2 can't have a null opening angle
        """

        if self.begin == self.center or (
            abs(self.begin) == 0 and abs(self.center) == 0
        ):
            raise PointArc2Error
            ("The beginning point and the center of an Arc2 can't be the same")
        if self.angle == 0:
            raise AngleArc2Error("An arc can't have a null opening angle")
        if self.angle == 2 * np.pi:
            raise AngleArc2Error("You can't draw a circle with an Arc2")

    # cf Methods.Geometry.Arc2.comp_length
    def comp_length(self):
        """Compute the length of the arc

        Parameters
        ----------
        self : Arc2
            An Arc2 object

        Returns
        -------
        length: float
            length of the arc
        """

        R = abs(self.comp_radius())  # Radius of the arc
        angle = self.angle

        # 2*pi*R is the length of the total circle
        # The arc is an alpha / 2pi portion of the cercle
        return float(2 * np.pi * R * (abs(angle) / (2 * np.pi)))

    # cf Methods.Geometry.Arc2.comp_radius
    def comp_radius(self):
        """Compute the radius of the arc

        Parameters
        ----------
        self : Arc2
            An Arc2 object

        Returns
        -------
        radius: float
            radius of the arc
        """

        self.check()

        z1 = self.begin
        zc = self.center
        return float(np.abs(z1 - zc))  # Radius of the arc

    # cf Methods.Geometry.Arc2.discretize
    def discretize(self, nb_point=ARC_NPOINT_D):
        """Return the discretize version of the Arc.
        Begin and end are always returned

        Parameters
        ----------
        self : Arc2
            An Arc2 object
        nb_point : int
            Number of points to add to discretize the arc (Default value = ARC_NPOINT_D)

        Returns
        -------
        list_point: list
            list of complex coordinate of the points

        Raises
        ------
        NbPointArc2DError
            nb_point must be an integer >=0
        """

        self.check()
        if not isinstance(nb_point, int):
            raise NbPointArc2DError("discretize : nb_point must be an integer")
        if nb_point < 0:
            raise NbPointArc2DError("nb_point must be >=0")

        # We use the complex representation of the point
        z1 = self.begin
        zc = self.center

        # Geometric transformation : center is the origine, angle(begin) = 0
        Zstart = (z1 - zc) * np.exp(-1j * np.angle(z1 - zc))

        # Generation of the point by rotation
        t = np.linspace(0, self.angle, nb_point + 2)
        list_point = Zstart * np.exp(1j * t)

        # Geometric transformation : return to the main axis
        list_point = list_point * np.exp(1j * np.angle(z1 - zc)) + zc

        return list_point

    # cf Methods.Geometry.Arc2.get_angle
    def get_angle(self, is_deg=False):
        """Return the angle of the arc

        Parameters
        ----------
        self : Arc2
            An Arc2 object
        is_deg: bool
            True to convert to degree

        Returns
        -------
        angle: float
            Angle of the arc
        """

        if is_deg:
            return self.angle * 180 / np.pi
        else:
            return self.angle

    # cf Methods.Geometry.Arc2.get_begin
    def get_begin(self):
        """Return the begin point of the arc

        Parameters
        ----------
        self : Arc2
            An Arc2 object

        Returns
        -------
        begin: complex
            begin point of the Arc2
        """

        return self.begin

    # cf Methods.Geometry.Arc2.get_center
    def get_center(self):
        """Return the center point of the arc

        Parameters
        ----------
        self : Arc2
            An Arc2 object

        Returns
        -------
        center: complex
            center point of the Arc2
        """

        return self.center

    # cf Methods.Geometry.Arc2.get_end
    def get_end(self):
        """Return the end of the arc

        Parameters
        ----------
        self : Arc2
            An Arc2 object

        Returns
        -------
        end: complex
            Complex coordinates of the end of the Arc2
        """

        self.check()

        # the center is on the bisection of [begin, end]
        z1 = self.begin
        zc = self.center
        angle = self.angle

        # Geometric transformation : center is the origine (-zc)
        # Then rotation of begin of the correct angle (*exp(i*pi*angle))
        # Then return to the main axis (+zc)
        z2 = (z1 - zc) * np.exp(1j * angle) + zc

        # Return (0,0) if the point is too close from 0
        if np.abs(z2) < 1e-6:
            z2 = 0
        return z2

    # cf Methods.Geometry.Arc2.get_middle
    def get_middle(self):
        """Return the point at the middle of the arc

        Parameters
        ----------
        self : Arc2
            An Arc2 object

        Returns
        -------
        Zmid: complex
            Complex coordinates of the middle of the Arc2
        """

        self.check()

        # We use the complex representation of the point
        z1 = self.begin
        zc = self.center

        # Geometric transformation : center is the origine, angle(begin) = 0
        Zstart = (z1 - zc) * np.exp(-1j * np.angle(z1 - zc))

        # Generation of the point by rotation
        Zmid = Zstart * np.exp(1j * self.angle / 2.0)

        # Geometric transformation : return to the main axis
        Zmid = Zmid * np.exp(1j * np.angle(z1 - zc)) + zc

        # Return (0,0) if the point is too close from 0
        if np.abs(Zmid) < 1e-6:
            Zmid = 0

        return Zmid

    # cf Methods.Geometry.Arc2.reverse
    def reverse(self):
        """Reverse the begin and end point of the Line

        Parameters
        ----------
        self : Arc2
            An Arc2 object

        Returns
        -------
        """

        self.begin = self.get_end()
        self.angle = -self.angle

    # cf Methods.Geometry.Arc2.rotate
    def rotate(self, angle):
        """Rotation of the Arc2 of angle

        Parameters
        ----------
        self : Arc2
            An Arc2 Object

        angle : float
            the angle of rotation [rad]

        Returns
        -------
        None
        """
        if not isinstance(angle, float) and not isinstance(angle, int):
            raise AngleRotationArc2Error("The angle must be a float or int")

        # check if Arc2 is correct"
        self.check()

        # Modification from the rotation  of the object
        self.begin = self.begin * np.exp(1j * angle)
        self.center = self.center * np.exp(1j * angle)

    # cf Methods.Geometry.Arc2.scale
    def scale(self, scale_factor):
        """Scale the coordinates of the begin/end

        Parameters
        ----------
        self : Arc2
            An Arc2 Object
        scale_factor : float
            the Scale factor [-]

        Returns
        -------
        None
        """

        self.begin = self.begin * scale_factor
        self.center = self.center * scale_factor

    # cf Methods.Geometry.Arc2.split_half
    def split_half(self, is_begin=True):
        """Cut the line in half (modify the object)

        Parameters
        ----------
        self : Arc2
            An Arc2 object
        is_begin : bool
            True to keep the part begin=>middle, False for the part middle=>end

        Returns
        -------
        """

        if not is_begin:
            self.begin = self.get_middle()
        self.angle = self.angle / 2

    # cf Methods.Geometry.Arc2.split_point
    def split_point(self, Z1, is_begin=True):
        """Cut the Arc according to a point on the arc

        Parameters
        ----------
        self : Arc2
            An Arc2 object
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
            self.angle = np.angle((Z1 - Zc) * np.exp(-1j * np.angle(self.begin)))
        else:
            self.angle = np.angle((self.get_end() - Zc) * np.exp(-1j * np.angle(Z1)))
            self.begin = Z1

    # cf Methods.Geometry.Arc2.translate
    def translate(self, Zt):
        """Translate the Arc2 object with

        Parameters
        ----------
        self : Arc2
            An Arc2 object

        Zt : complex
            Complex coordinates value for translation

        Returns
        -------
        None
        """
        if (
            not isinstance(Zt, complex)
            and not isinstance(Zt, int)
            and not isinstance(Zt, float)
        ):
            raise PointTranslateArc2Error(
                "The point must be a complex number or int or float"
            )

        # check if the Arc2 is correct
        self.check()

        # Modification from the translation of Arc2
        self.begin = self.begin + Zt
        self.center = self.center + Zt

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        begin=0,
        center=0,
        angle=1.57079633,
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
            if "center" in list(init_dict.keys()):
                center = init_dict["center"]
            if "angle" in list(init_dict.keys()):
                angle = init_dict["angle"]
            if "prop_dict" in list(init_dict.keys()):
                prop_dict = init_dict["prop_dict"]
        # Set the properties (value check and convertion are done in setter)
        self.begin = begin
        self.center = center
        self.angle = angle
        # Call Arc init
        super(Arc2, self).__init__(prop_dict=prop_dict)
        # The class is frozen (in Arc init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        Arc2_str = ""
        # Get the properties inherited from Arc
        Arc2_str += super(Arc2, self).__str__()
        Arc2_str += "begin = " + str(self.begin) + linesep
        Arc2_str += "center = " + str(self.center) + linesep
        Arc2_str += "angle = " + str(self.angle) + linesep
        return Arc2_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from Arc
        if not super(Arc2, self).__eq__(other):
            return False
        if other.begin != self.begin:
            return False
        if other.center != self.center:
            return False
        if other.angle != self.angle:
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
            super(Arc2, self).compare(
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
        if (
            other._angle is not None
            and self._angle is not None
            and np.isnan(other._angle)
            and np.isnan(self._angle)
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
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from Arc
        S += super(Arc2, self).__sizeof__()
        S += getsizeof(self.begin)
        S += getsizeof(self.center)
        S += getsizeof(self.angle)
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
        Arc2_dict = super(Arc2, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        if self.begin is None:
            Arc2_dict["begin"] = None
        elif isinstance(self.begin, float):
            Arc2_dict["begin"] = self.begin
        else:
            Arc2_dict["begin"] = str(self.begin)
        if self.center is None:
            Arc2_dict["center"] = None
        elif isinstance(self.center, float):
            Arc2_dict["center"] = self.center
        else:
            Arc2_dict["center"] = str(self.center)
        Arc2_dict["angle"] = self.angle
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        Arc2_dict["__class__"] = "Arc2"
        return Arc2_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        begin_val = self.begin
        center_val = self.center
        angle_val = self.angle
        if self.prop_dict is None:
            prop_dict_val = None
        else:
            prop_dict_val = self.prop_dict.copy()
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(
            begin=begin_val, center=center_val, angle=angle_val, prop_dict=prop_dict_val
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.begin = None
        self.center = None
        self.angle = None
        # Set to None the properties inherited from Arc
        super(Arc2, self)._set_None()

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
        doc="""center of the arc

        :Type: complex
        """,
    )

    def _get_angle(self):
        """getter of angle"""
        return self._angle

    def _set_angle(self, value):
        """setter of angle"""
        check_var("angle", value, "float", Vmin=-6.283185308, Vmax=6.283185308)
        self._angle = value

    angle = property(
        fget=_get_angle,
        fset=_set_angle,
        doc="""opening angle of the arc

        :Type: float
        :min: -6.283185308
        :max: 6.283185308
        """,
    )
