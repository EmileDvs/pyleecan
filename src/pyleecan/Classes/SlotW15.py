# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Slot/SlotW15.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Slot/SlotW15
"""

# Inline fallback report:
# These methods remain imported because their source or imports cannot be safely moved into this class.
# - plot_schematics: import name 'Arc1' refers to different sources (.Arc1.Arc1 and ..Methods.Slot.SlotW15.plot_schematics.Arc1)

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
from ..Methods.Slot.SlotW15.plot_schematics import plot_schematics
from .Arc1 import Arc1
from .Segment import Segment
from numpy import angle, arcsin, arctan, cos, exp, pi, sin, sqrt
from ..Methods.Slot.SlotW15 import S15InnerError
from ..Functions.labels import WIND_LAB, DRAW_PROP_LAB, SOP_LAB
from .SurfLine import SurfLine

from numpy import isnan
from ._check import InitUnKnowClassError


class SlotW15(Slot):

    VERSION = 1
    IS_SYMMETRICAL = 1

    # cf Methods.Slot.SlotW15._comp_line_dict
    def _comp_line_dict(self):
        """Define a dictionnary of the lines to draw the slot
        If a line has begin==end, it is replaced by "None" (dict has always the same number of keys)

        Parameters
        ----------
        self : SlotW15
            A SlotW15 object

        Returns
        -------
        line_dict: dict
            Dictionnary of the slot lines (key: line name, value: line object)
        """

        point_dict = self._comp_point_coordinate()
        Z1 = point_dict["Z1"]
        Z2 = point_dict["Z2"]
        Z3 = point_dict["Z3"]
        Z4 = point_dict["Z4"]
        Z5 = point_dict["Z5"]
        Z6 = point_dict["Z6"]
        Z7 = point_dict["Z7"]
        Z8 = point_dict["Z8"]
        Z9 = point_dict["Z9"]
        Z10 = point_dict["Z10"]
        Z11 = point_dict["Z11"]
        Z12 = point_dict["Z12"]
        Z13 = point_dict["Z13"]

        # Creation of curve
        line_dict = dict()
        line_dict["1-2"] = Segment(Z1, Z2)
        line_dict["2-3"] = Segment(Z2, Z3)
        line_dict["3-4"] = Arc1(Z3, Z4, self.R1)
        line_dict["4-5"] = Segment(Z4, Z5)
        line_dict["5-6"] = Arc1(Z5, Z6, self.R2)
        line_dict["6-8"] = Arc1(Z6, Z8, abs(Z7))
        line_dict["8-9"] = Arc1(Z8, Z9, self.R2)
        line_dict["9-10"] = Segment(Z9, Z10)
        line_dict["10-11"] = Arc1(Z10, Z11, self.R1)
        line_dict["11-12"] = Segment(Z11, Z12)
        line_dict["12-13"] = Segment(Z12, Z13)

        # Closing Arc (Rbo)
        line_dict["13-1"] = Arc1(Z13, Z1, -self.get_Rbo(), is_trigo_direction=False)

        # Closing Active part
        line_dict["2-12"] = Segment(Z2, Z12)
        line_dict["12-2"] = Segment(Z12, Z2)

        return line_dict

    # cf Methods.Slot.SlotW15._comp_point_coordinate
    def _comp_point_coordinate(self):
        """Compute the point coordinates needed to plot the Slot.

        Parameters
        ----------
        self : SlotW15
            A SlotW15 object

        Returns
        -------
        point_dict: dict
            A dict of the slot point coordinates
        """
        Rbo = self.get_Rbo()

        # alpha is the angle to rotate Z0 so ||Z1,Z13|| = W0
        alpha = arcsin(self.W0 / (2 * Rbo))
        hsp = pi / self.Zs  # Half slot pitch

        Z0 = Rbo * exp(1j * 0)
        Z13 = Z0 * exp(1j * alpha)
        if self.is_outwards():
            Z12 = Z0 + self.H0 + 1j * Z13.imag
            Z7 = Z0 + self.H0 + self.H1 + self.H2

            # Zc3, Z8 and (0,0) are align (tangent) => abs(Zc3)=Rbo+H0+H1+H2-R2
            # In tooth ref: Im(Zc3') = -W3/2 - R2
            A = Rbo + self.H0 + self.H1 + self.H2 - self.R2
            B = -self.W3 / 2 - self.R2
            xc2 = B * sin(-hsp) + sqrt(-(B**2) + A**2) * cos(-hsp)
            yc2 = B * cos(-hsp) - sqrt(-(B**2) + A**2) * sin(-hsp)
            Zc3 = xc2 + 1j * yc2
            Z9 = (Zc3 * exp(1j * -hsp) + self.R2 * 1j) * exp(1j * hsp)

            # Zc3, Z8 and (0,0) are align, |Zc3, Z8| = R2
            Z8 = (Zc3 * exp(1j * -angle(Zc3)) + self.R2) * exp(1j * angle(Zc3))

            # Real(Zc4) = Rbo+H0+H1
            # In tooth ref: Im(Zc4') = -W3/2 - R1
            xc1 = Rbo + self.H0 + self.H1
            yc1 = (-self.W3 / 2 - self.R1 - xc1 * sin(-hsp)) / cos(-hsp)
            Zc4 = xc1 + 1j * yc1
            Z10 = (Zc4 * exp(1j * -hsp) + self.R1 * 1j) * exp(1j * hsp)

            # Ref center at Zc4, (Z11,Z12) and (Z11,Zc4) are orthogonal
            # Z11 = R1*exp(1i*theta)
            # (R1*cos(theta)-x2)*R1*cos(theta)+(R1*sin(theta)-y2)*R1*sin(theta) = 0
            R1 = self.R1
            y2 = (Z12 - Zc4).imag
            x2 = (Z12 - Zc4).real
            theta = 2 * arctan((y2 - sqrt(-(R1**2) + x2**2 + y2**2)) / (R1 + x2))
            Z11 = R1 * exp(1j * theta) + Zc4
        else:
            raise S15InnerError("Slot Type 15 can't be used on inner lamination")

        point_dict = dict()
        # symetry
        point_dict["Z13"] = Z13
        point_dict["Z12"] = Z12
        point_dict["Z11"] = Z11
        point_dict["Z10"] = Z10
        point_dict["Z9"] = Z9
        point_dict["Z8"] = Z8
        point_dict["Z7"] = Z7
        point_dict["Z6"] = Z8.conjugate()
        point_dict["Z5"] = Z9.conjugate()
        point_dict["Z4"] = Z10.conjugate()
        point_dict["Z3"] = Z11.conjugate()
        point_dict["Z2"] = Z12.conjugate()
        point_dict["Z1"] = Z13.conjugate()
        point_dict["Zc4"] = Zc4
        point_dict["Zc3"] = Zc3
        point_dict["Zc2"] = Zc3.conjugate()
        point_dict["Zc1"] = Zc4.conjugate()
        return point_dict

    # cf Methods.Slot.SlotW15.build_geometry
    def build_geometry(self):
        """Compute the curve (Line) needed to plot the Slot.
        The ending point of a curve is the starting point of the next curve in
        the list

        Parameters
        ----------
        self : SlotW15
            A SlotW15 object

        Returns
        -------
        curve_list: list
            A list of 6 Segment and 5 Arc

        """

        line_dict = self._comp_line_dict()

        curve_list = [
            line_dict["1-2"],
            line_dict["2-3"],
            line_dict["3-4"],
            line_dict["4-5"],
            line_dict["5-6"],
            line_dict["6-8"],
            line_dict["8-9"],
            line_dict["9-10"],
            line_dict["10-11"],
            line_dict["11-12"],
            line_dict["12-13"],
        ]
        return [line for line in curve_list if line is not None]

    # cf Methods.Slot.SlotW15.check
    def check(self):
        """Check that the SlotW15 object is correct

        Parameters
        ----------
        self : SlotW15
            A SlotW15 object

        Returns
        -------
        None

        Raises
        -------
        S15InnerError
            Slot Type 15 can't be used on inner lamination
        """

        if not self.is_outwards():
            raise S15InnerError("Slot Type 15 can't be used on inner lamination")

    # cf Methods.Slot.SlotW15.comp_angle_opening
    def comp_angle_opening(self):
        """Compute the average opening angle of the Slot

        Parameters
        ----------
        self : SlotW15
            A SlotW15 object

        Returns
        -------
        alpha: float
            Average opening angle of the slot [rad]

        """

        Rbo = self.get_Rbo()

        return float(2 * arcsin(self.W0 / (2 * Rbo)))

    # cf Methods.Slot.SlotW15.comp_height
    def comp_height(self):
        """Compute the height of the Slot.
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotW15
            A SlotW15 object

        Returns
        -------
        Htot: float
            Height of the slot [m]

        """

        return self.H0 + self.H1 + self.H2

    # cf Methods.Slot.SlotW15.comp_height_active
    def comp_height_active(self):
        """Compute the height of the winding area

        Parameters
        ----------
        self : SlotW15
            A SlotW15 object

        Returns
        -------
        Hwind: float
            Height of the winding area [m]

        """
        return self.H1 + self.H2

    # cf Methods.Slot.SlotW15.comp_surface
    def comp_surface(self):
        """Compute the Slot total surface (by analytical computation).
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotW15
            A SlotW15 object

        Returns
        -------
        S: float
            Slot total surface [m**2]

        """
        return self.comp_surface_active() + self.comp_surface_opening()

    # cf Methods.Slot.SlotW15.comp_surface_opening
    def comp_surface_opening(self):
        """Compute the Slot opening surface (by analytical computation).
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotW15
            A SlotW15 object

        Returns
        -------
        S: float
            Slot opening surface [m**2]

        """

        Rbo = self.get_Rbo()

        # The bottom is an arc
        alpha = self.comp_angle_opening()
        Sarc = (Rbo**2.0) / 2.0 * (alpha - sin(alpha))
        Harc = float(Rbo * (1 - cos(alpha / 2)))
        S1 = (self.H0 + Harc) * self.W0

        # Because Slamination = S - Zs * Sslot
        if self.is_outwards():
            return S1 - Sarc

    # cf Methods.Slot.SlotW15.get_surface_active
    def get_surface_active(self, alpha=0, delta=0):
        """Return the full winding surface

        Parameters
        ----------
        self : SlotW15
            A SlotW15 object
        alpha : float
            float number for rotation (Default value = 0) [rad]
        delta : complex
            complex number for translation (Default value = 0)

        Returns
        -------
        surf_wind: Surface
            Surface corresponding to the Winding Area
        """

        # Create curve list
        line_dict = self._comp_line_dict()
        curve_list = [
            line_dict["2-3"],
            line_dict["3-4"],
            line_dict["4-5"],
            line_dict["5-6"],
            line_dict["6-8"],
            line_dict["8-9"],
            line_dict["9-10"],
            line_dict["10-11"],
            line_dict["11-12"],
            line_dict["12-2"],
        ]
        curve_list = [line for line in curve_list if line is not None]

        # Only the closing arc (12-2) needs to be drawn (in FEMM)
        for curve in curve_list[:-1]:
            if curve.prop_dict is None:
                curve.prop_dict = dict()
            curve.prop_dict.update({DRAW_PROP_LAB: False})

        # Creating surface
        label = self.parent.get_label() + "_" + WIND_LAB + "_R0-T0-S0"
        if self.is_outwards():
            Zmid = self.get_Rbo() + self.H0 + self.H1 + self.H2 / 2
        else:
            Zmid = self.get_Rbo() - self.H0 - self.H1 - self.H2 / 2
        surface = SurfLine(line_list=curve_list, label=label, point_ref=Zmid)

        # Apply transformation
        surface.rotate(alpha)
        surface.translate(delta)

        return surface

    # cf Methods.Slot.SlotW15.get_surface_opening
    def get_surface_opening(self, alpha=0, delta=0):
        """Return the list of surfaces defining the opening area of the Slot

        Parameters
        ----------
        self : SlotW15
            A SlotW15 object
        alpha : float
            float number for rotation (Default value = 0) [rad]
        delta : complex
            complex number for translation (Default value = 0)

        Returns
        -------
        surf_list : list
            list of surfaces objects
        """

        # H0=0 no opening
        if self.H0 == 0:
            return []

        # Create curve list
        line_dict = self._comp_line_dict()
        curve_list = [
            line_dict["1-2"],
            line_dict["2-12"],
            line_dict["12-13"],
            line_dict["13-1"],
        ]
        curve_list = [line for line in curve_list if line is not None]

        # Only the closing arc (13-1) needs to be drawn (in FEMM)
        for curve in curve_list[:-1]:
            if curve.prop_dict is None:
                curve.prop_dict = dict()
            curve.prop_dict.update({DRAW_PROP_LAB: False})

        # Create surface
        if self.is_outwards():
            Zmid = self.get_Rbo() + self.H0 / 2
        else:
            Zmid = self.get_Rbo() - self.H0 / 2
        label = self.parent.get_label() + "_" + SOP_LAB + "_R0-T0-S0"
        surface = SurfLine(line_list=curve_list, label=label, point_ref=Zmid)

        # Apply transformation
        surface.rotate(alpha)
        surface.translate(delta)

        return [surface]

    # cf Methods.Slot.SlotW15.plot_schematics
    plot_schematics = plot_schematics
    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        W0=0.0122,
        W3=0.0122,
        H0=0.001,
        H1=0.0015,
        H2=0.0122,
        R1=0.001,
        R2=0.001,
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
            if "W3" in list(init_dict.keys()):
                W3 = init_dict["W3"]
            if "H0" in list(init_dict.keys()):
                H0 = init_dict["H0"]
            if "H1" in list(init_dict.keys()):
                H1 = init_dict["H1"]
            if "H2" in list(init_dict.keys()):
                H2 = init_dict["H2"]
            if "R1" in list(init_dict.keys()):
                R1 = init_dict["R1"]
            if "R2" in list(init_dict.keys()):
                R2 = init_dict["R2"]
            if "Zs" in list(init_dict.keys()):
                Zs = init_dict["Zs"]
            if "wedge_mat" in list(init_dict.keys()):
                wedge_mat = init_dict["wedge_mat"]
            if "is_bore" in list(init_dict.keys()):
                is_bore = init_dict["is_bore"]
        # Set the properties (value check and convertion are done in setter)
        self.W0 = W0
        self.W3 = W3
        self.H0 = H0
        self.H1 = H1
        self.H2 = H2
        self.R1 = R1
        self.R2 = R2
        # Call Slot init
        super(SlotW15, self).__init__(Zs=Zs, wedge_mat=wedge_mat, is_bore=is_bore)
        # The class is frozen (in Slot init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        SlotW15_str = ""
        # Get the properties inherited from Slot
        SlotW15_str += super(SlotW15, self).__str__()
        SlotW15_str += "W0 = " + str(self.W0) + linesep
        SlotW15_str += "W3 = " + str(self.W3) + linesep
        SlotW15_str += "H0 = " + str(self.H0) + linesep
        SlotW15_str += "H1 = " + str(self.H1) + linesep
        SlotW15_str += "H2 = " + str(self.H2) + linesep
        SlotW15_str += "R1 = " + str(self.R1) + linesep
        SlotW15_str += "R2 = " + str(self.R2) + linesep
        return SlotW15_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from Slot
        if not super(SlotW15, self).__eq__(other):
            return False
        if other.W0 != self.W0:
            return False
        if other.W3 != self.W3:
            return False
        if other.H0 != self.H0:
            return False
        if other.H1 != self.H1:
            return False
        if other.H2 != self.H2:
            return False
        if other.R1 != self.R1:
            return False
        if other.R2 != self.R2:
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
            super(SlotW15, self).compare(
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
            other._W3 is not None
            and self._W3 is not None
            and isnan(other._W3)
            and isnan(self._W3)
        ):
            pass
        elif other._W3 != self._W3:
            if is_add_value:
                val_str = " (self=" + str(self._W3) + ", other=" + str(other._W3) + ")"
                diff_list.append(name + ".W3" + val_str)
            else:
                diff_list.append(name + ".W3")
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
        if (
            other._H2 is not None
            and self._H2 is not None
            and isnan(other._H2)
            and isnan(self._H2)
        ):
            pass
        elif other._H2 != self._H2:
            if is_add_value:
                val_str = " (self=" + str(self._H2) + ", other=" + str(other._H2) + ")"
                diff_list.append(name + ".H2" + val_str)
            else:
                diff_list.append(name + ".H2")
        if (
            other._R1 is not None
            and self._R1 is not None
            and isnan(other._R1)
            and isnan(self._R1)
        ):
            pass
        elif other._R1 != self._R1:
            if is_add_value:
                val_str = " (self=" + str(self._R1) + ", other=" + str(other._R1) + ")"
                diff_list.append(name + ".R1" + val_str)
            else:
                diff_list.append(name + ".R1")
        if (
            other._R2 is not None
            and self._R2 is not None
            and isnan(other._R2)
            and isnan(self._R2)
        ):
            pass
        elif other._R2 != self._R2:
            if is_add_value:
                val_str = " (self=" + str(self._R2) + ", other=" + str(other._R2) + ")"
                diff_list.append(name + ".R2" + val_str)
            else:
                diff_list.append(name + ".R2")
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from Slot
        S += super(SlotW15, self).__sizeof__()
        S += getsizeof(self.W0)
        S += getsizeof(self.W3)
        S += getsizeof(self.H0)
        S += getsizeof(self.H1)
        S += getsizeof(self.H2)
        S += getsizeof(self.R1)
        S += getsizeof(self.R2)
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
        SlotW15_dict = super(SlotW15, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        SlotW15_dict["W0"] = self.W0
        SlotW15_dict["W3"] = self.W3
        SlotW15_dict["H0"] = self.H0
        SlotW15_dict["H1"] = self.H1
        SlotW15_dict["H2"] = self.H2
        SlotW15_dict["R1"] = self.R1
        SlotW15_dict["R2"] = self.R2
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        SlotW15_dict["__class__"] = "SlotW15"
        return SlotW15_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        W0_val = self.W0
        W3_val = self.W3
        H0_val = self.H0
        H1_val = self.H1
        H2_val = self.H2
        R1_val = self.R1
        R2_val = self.R2
        Zs_val = self.Zs
        if self.wedge_mat is None:
            wedge_mat_val = None
        else:
            wedge_mat_val = self.wedge_mat.copy()
        is_bore_val = self.is_bore
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(
            W0=W0_val,
            W3=W3_val,
            H0=H0_val,
            H1=H1_val,
            H2=H2_val,
            R1=R1_val,
            R2=R2_val,
            Zs=Zs_val,
            wedge_mat=wedge_mat_val,
            is_bore=is_bore_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.W0 = None
        self.W3 = None
        self.H0 = None
        self.H1 = None
        self.H2 = None
        self.R1 = None
        self.R2 = None
        # Set to None the properties inherited from Slot
        super(SlotW15, self)._set_None()

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

    def _get_W3(self):
        """getter of W3"""
        return self._W3

    def _set_W3(self, value):
        """setter of W3"""
        check_var("W3", value, "float", Vmin=0)
        self._W3 = value

    W3 = property(
        fget=_get_W3,
        fset=_set_W3,
        doc="""Tooth width

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
        doc="""Slot intermediate height.

        :Type: float
        :min: 0
        """,
    )

    def _get_H2(self):
        """getter of H2"""
        return self._H2

    def _set_H2(self, value):
        """setter of H2"""
        check_var("H2", value, "float", Vmin=0)
        self._H2 = value

    H2 = property(
        fget=_get_H2,
        fset=_set_H2,
        doc="""Slot height

        :Type: float
        :min: 0
        """,
    )

    def _get_R1(self):
        """getter of R1"""
        return self._R1

    def _set_R1(self, value):
        """setter of R1"""
        check_var("R1", value, "float", Vmin=0)
        self._R1 = value

    R1 = property(
        fget=_get_R1,
        fset=_set_R1,
        doc="""Top radius

        :Type: float
        :min: 0
        """,
    )

    def _get_R2(self):
        """getter of R2"""
        return self._R2

    def _set_R2(self, value):
        """setter of R2"""
        check_var("R2", value, "float", Vmin=0)
        self._R2 = value

    R2 = property(
        fget=_get_R2,
        fset=_set_R2,
        doc="""Bottom radius

        :Type: float
        :min: 0
        """,
    )
