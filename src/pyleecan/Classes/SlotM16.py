# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Slot/SlotM16.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Slot/SlotM16
"""

# Inline fallback report:
# These methods remain imported because their source or imports cannot be safely moved into this class.
# - check: module uses a wildcard import whose names cannot be resolved safely
# - plot_schematics: import name 'Segment' refers to different sources (.Segment.Segment and ..Methods.Slot.SlotM16.plot_schematics.Segment)

from os import linesep
from sys import getsizeof
from logging import getLogger
from ._check import check_var, raise_
from ..Functions.get_logger import get_logger
from ..Functions.save import save
from ..Functions.load import load_init_dict
from ..Functions.Load.import_class import import_class
from copy import deepcopy
from .Slot import Slot

# Import all class method
# Try/catch to remove unnecessary dependencies in unused method
from ..Methods.Slot.SlotM16.check import check
from ..Methods.Slot.SlotM16.plot_schematics import plot_schematics
from numpy import arcsin, exp, sin
from .Segment import Segment
from .SurfLine import SurfLine

from numpy import isnan
from ._check import InitUnKnowClassError


class SlotM16(Slot):
    """Rectangular Slot with isthmus for Rectangular magnet"""

    VERSION = 1
    IS_SYMMETRICAL = 1

    # cf Methods.Slot.SlotM16._comp_point_coordinate
    def _comp_point_coordinate(self):
        """Compute the point coordinates needed to plot the Slot.

        Parameters
        ----------
        self : SlotM16
            A SlotM16 object

        Returns
        -------
        point_dict: dict
            A dict of the slot coordinates

        """
        Rbo = self.get_Rbo()

        # alpha is the angle to rotate Z0 so ||Z1,Z12|| = W0
        alpha = arcsin(self.W0 / (2 * Rbo))

        Z0 = Rbo * exp(1j * 0)
        Z1 = Z0 * exp(1j * -alpha)

        if self.is_outwards():
            Z2 = Z1 + self.H0
            Z3 = Z2 - (self.W1 - self.W0) * 1j / 2.0
            Z4 = Z3 + self.H1
        else:
            Z2 = Z1 - self.H0
            Z3 = Z2 - (self.W1 - self.W0) * 1j / 2.0
            Z4 = Z3 - self.H1

        # symetry
        Z5 = Z4.conjugate()
        Z6 = Z3.conjugate()
        Z7 = Z2.conjugate()
        Z8 = Z1.conjugate()

        point_dict = dict()
        point_dict["Z1"] = Z1
        point_dict["Z2"] = Z2
        point_dict["Z3"] = Z3
        point_dict["Z4"] = Z4
        point_dict["Z5"] = Z5
        point_dict["Z6"] = Z6
        point_dict["Z7"] = Z7
        point_dict["Z8"] = Z8

        return point_dict

    # cf Methods.Slot.SlotM16.build_geometry
    def build_geometry(self):
        """Compute the curve (Line) needed to plot the Slot.
        The ending point of a curve is the starting point of the next curve in
        the list

        Parameters
        ----------
        self : SlotM16
            A SlotM16 object

        Returns
        -------
        curve_list: list
            A list of 11 Segment

        """

        point_dict = self._comp_point_coordinate()

        # Creation of curve
        curve_list = list()
        if self.H0 > 0:
            curve_list.append(Segment(point_dict["Z1"], point_dict["Z2"]))
        curve_list.append(Segment(point_dict["Z2"], point_dict["Z3"]))
        if self.H1 > 0:
            curve_list.append(Segment(point_dict["Z3"], point_dict["Z4"]))
        curve_list.append(Segment(point_dict["Z4"], point_dict["Z5"]))
        if self.H1 > 0:
            curve_list.append(Segment(point_dict["Z5"], point_dict["Z6"]))
        curve_list.append(Segment(point_dict["Z6"], point_dict["Z7"]))
        if self.H0 > 0:
            curve_list.append(Segment(point_dict["Z7"], point_dict["Z8"]))

        return curve_list

    # cf Methods.Slot.SlotM16.check
    check = check

    # cf Methods.Slot.SlotM16.comp_angle_opening
    def comp_angle_opening(self):
        """Compute the average opening angle of the Slot

        Parameters
        ----------
        self : SlotM16
            A SlotM16 object

        Returns
        -------
        alpha: float
            Average opening angle of the slot [rad]

        """
        Rbo = self.get_Rbo()

        return float(2 * arcsin(self.W0 / (2 * Rbo)))

    # cf Methods.Slot.SlotM16.comp_height
    def comp_height(self):
        """Compute the height of the Slot.
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotM16
            A SlotM16 object

        Returns
        -------
        Htot: float
            Height of the slot [m]

        """
        point_dict = self._comp_point_coordinate()
        Z4 = point_dict["Z4"]
        Z5 = point_dict["Z5"]

        Rbo = self.get_Rbo()

        if self.is_outwards():
            return abs(Z4) - Rbo
        else:
            return Rbo - abs((Z4 + Z5) / 2)

    # cf Methods.Slot.SlotM16.comp_height_active
    def comp_height_active(self):
        """Compute the height of the winding area

        Parameters
        ----------
        self : SlotM16
            A SlotM16 object

        Returns
        -------
        Hwind: float
            Height of the winding area [m]

        """

        point_dict = self._comp_point_coordinate()
        Z3 = point_dict["Z3"]
        Z4 = point_dict["Z4"]
        Z5 = point_dict["Z5"]
        Z6 = point_dict["Z6"]

        if self.is_outwards():
            R1 = abs((Z3 + Z6) / 2)
            R2 = abs(Z4)
        else:
            R1 = abs((Z4 + Z5) / 2)
            R2 = abs(Z3)
        return R2 - R1

    # cf Methods.Slot.SlotM16.comp_surface
    def comp_surface(self):
        """Compute the Slot total surface (by analytical computation).
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotM16
            A SlotM16 object

        Returns
        -------
        S: float
            Slot total surface [m**2]

        """
        Rbo = self.get_Rbo()

        S0 = self.H0 * self.W0
        S1 = self.H1 * self.W1

        # The bottom is an arc
        alpha = self.comp_angle_opening()
        Sarc = (Rbo**2.0) / 2.0 * (alpha - sin(alpha))

        # Because Slamination = S - Zs * Sslot
        if self.is_outwards():
            return S0 + S1 - Sarc
        else:
            return S0 + S1 + Sarc

    # cf Methods.Slot.SlotM16.comp_surface_active
    def comp_surface_active(self):
        """Compute the Slot inner surface for winding (by analytical computation)

        Parameters
        ----------
        self : SlotM16
            A SlotM16 object

        Returns
        -------
        Swind: float
            Slot inner surface for winding [m**2]

        """

        return self.W1 * self.H1

    # cf Methods.Slot.SlotM16.get_surface_active
    def get_surface_active(self, alpha=0, delta=0):
        """Return the full winding surface

        Parameters
        ----------
        self : SlotM16
            A SlotM16 object
        alpha : float
            float number for rotation (Default value = 0) [rad]
        delta : complex
            complex number for translation (Default value = 0)

        Returns
        -------
        surf_wind: Surface
            Surface corresponding to the Winding Area
        """

        # get the name of the lamination
        st = self.get_name_lam()

        # Create curve list
        curve_list = self.build_geometry()[1:-1]
        curve_list.append(
            Segment(begin=curve_list[-1].get_end(), end=curve_list[0].get_begin())
        )

        # Create surface
        if self.is_outwards():
            Zmid = self.get_Rbo() + self.H0 + self.H1 / 2
        else:
            Zmid = self.get_Rbo() - self.H0 - self.H1 / 2
        surface = SurfLine(
            line_list=curve_list, label="Wind_" + st + "_R0_T0_S0", point_ref=Zmid
        )

        # Apply transformation
        surface.rotate(alpha)
        surface.translate(delta)

        return surface

    # cf Methods.Slot.SlotM16.plot_schematics
    plot_schematics = plot_schematics
    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        W0=0.0122,
        H0=0.001,
        W1=0.0122,
        H1=0.001,
        Zs=36,
        wedge_mat=None,
        is_bore=True,
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
            if "W0" in list(init_dict.keys()):
                W0 = init_dict["W0"]
            if "H0" in list(init_dict.keys()):
                H0 = init_dict["H0"]
            if "W1" in list(init_dict.keys()):
                W1 = init_dict["W1"]
            if "H1" in list(init_dict.keys()):
                H1 = init_dict["H1"]
            if "Zs" in list(init_dict.keys()):
                Zs = init_dict["Zs"]
            if "wedge_mat" in list(init_dict.keys()):
                wedge_mat = init_dict["wedge_mat"]
            if "is_bore" in list(init_dict.keys()):
                is_bore = init_dict["is_bore"]
        # Set the properties (value check and convertion are done in setter)
        self.W0 = W0
        self.H0 = H0
        self.W1 = W1
        self.H1 = H1
        # Call Slot init
        super(SlotM16, self).__init__(Zs=Zs, wedge_mat=wedge_mat, is_bore=is_bore)
        # The class is frozen (in Slot init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        SlotM16_str = ""
        # Get the properties inherited from Slot
        SlotM16_str += super(SlotM16, self).__str__()
        SlotM16_str += "W0 = " + str(self.W0) + linesep
        SlotM16_str += "H0 = " + str(self.H0) + linesep
        SlotM16_str += "W1 = " + str(self.W1) + linesep
        SlotM16_str += "H1 = " + str(self.H1) + linesep
        return SlotM16_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from Slot
        if not super(SlotM16, self).__eq__(other):
            return False
        if other.W0 != self.W0:
            return False
        if other.H0 != self.H0:
            return False
        if other.W1 != self.W1:
            return False
        if other.H1 != self.H1:
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()

        # Check the properties inherited from Slot
        diff_list.extend(
            super(SlotM16, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
        if (
            other._W0 is not None
            and self._W0 is not None
            and isnan(other._W0)
            and isnan(self._W0)
        ):
            pass
        elif other._W0 != self._W0:
            if is_add_value:
                val_str = " (self=" + str(self._W0) + ", other=" + str(other._W0) + ")"
                diff_list.append(name + ".W0" + val_str)
            else:
                diff_list.append(name + ".W0")
        if (
            other._H0 is not None
            and self._H0 is not None
            and isnan(other._H0)
            and isnan(self._H0)
        ):
            pass
        elif other._H0 != self._H0:
            if is_add_value:
                val_str = " (self=" + str(self._H0) + ", other=" + str(other._H0) + ")"
                diff_list.append(name + ".H0" + val_str)
            else:
                diff_list.append(name + ".H0")
        if (
            other._W1 is not None
            and self._W1 is not None
            and isnan(other._W1)
            and isnan(self._W1)
        ):
            pass
        elif other._W1 != self._W1:
            if is_add_value:
                val_str = " (self=" + str(self._W1) + ", other=" + str(other._W1) + ")"
                diff_list.append(name + ".W1" + val_str)
            else:
                diff_list.append(name + ".W1")
        if (
            other._H1 is not None
            and self._H1 is not None
            and isnan(other._H1)
            and isnan(self._H1)
        ):
            pass
        elif other._H1 != self._H1:
            if is_add_value:
                val_str = " (self=" + str(self._H1) + ", other=" + str(other._H1) + ")"
                diff_list.append(name + ".H1" + val_str)
            else:
                diff_list.append(name + ".H1")
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from Slot
        S += super(SlotM16, self).__sizeof__()
        S += getsizeof(self.W0)
        S += getsizeof(self.H0)
        S += getsizeof(self.W1)
        S += getsizeof(self.H1)
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

        # Get the properties inherited from Slot
        SlotM16_dict = super(SlotM16, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        SlotM16_dict["W0"] = self.W0
        SlotM16_dict["H0"] = self.H0
        SlotM16_dict["W1"] = self.W1
        SlotM16_dict["H1"] = self.H1
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        SlotM16_dict["__class__"] = "SlotM16"
        return SlotM16_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        W0_val = self.W0
        H0_val = self.H0
        W1_val = self.W1
        H1_val = self.H1
        Zs_val = self.Zs
        if self.wedge_mat is None:
            wedge_mat_val = None
        else:
            wedge_mat_val = self.wedge_mat.copy()
        is_bore_val = self.is_bore
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(
            W0=W0_val,
            H0=H0_val,
            W1=W1_val,
            H1=H1_val,
            Zs=Zs_val,
            wedge_mat=wedge_mat_val,
            is_bore=is_bore_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.W0 = None
        self.H0 = None
        self.W1 = None
        self.H1 = None
        # Set to None the properties inherited from Slot
        super(SlotM16, self)._set_None()

    def _get_W0(self):
        """getter of W0"""
        return self._W0

    def _set_W0(self, value):
        """setter of W0"""
        check_var("W0", value, "float", Vmin=0)
        self._W0 = value

    W0 = property(
        fget=_get_W0,
        fset=_set_W0,
        doc="""Slot isthmus width.

        :Type: float
        :min: 0
        """,
    )

    def _get_H0(self):
        """getter of H0"""
        return self._H0

    def _set_H0(self, value):
        """setter of H0"""
        check_var("H0", value, "float", Vmin=0)
        self._H0 = value

    H0 = property(
        fget=_get_H0,
        fset=_set_H0,
        doc="""Slot isthmus height.

        :Type: float
        :min: 0
        """,
    )

    def _get_W1(self):
        """getter of W1"""
        return self._W1

    def _set_W1(self, value):
        """setter of W1"""
        check_var("W1", value, "float", Vmin=0)
        self._W1 = value

    W1 = property(
        fget=_get_W1,
        fset=_set_W1,
        doc="""Slot Width

        :Type: float
        :min: 0
        """,
    )

    def _get_H1(self):
        """getter of H1"""
        return self._H1

    def _set_H1(self, value):
        """setter of H1"""
        check_var("H1", value, "float", Vmin=0)
        self._H1 = value

    H1 = property(
        fget=_get_H1,
        fset=_set_H1,
        doc="""Slot Height

        :Type: float
        :min: 0
        """,
    )
