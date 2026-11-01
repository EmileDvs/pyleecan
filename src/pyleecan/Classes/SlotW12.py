# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Slot/SlotW12.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Slot/SlotW12
"""

# Inline fallback report:
# These methods remain imported because their source or imports cannot be safely moved into this class.
# - check: module uses a wildcard import whose names cannot be resolved safely
# - plot_schematics: import name 'Arc1' refers to different sources (.Arc1.Arc1 and ..Methods.Slot.SlotW12.plot_schematics.Arc1)

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
from ..Methods.Slot.SlotW12.check import check
from ..Methods.Slot.SlotW12.plot_schematics import plot_schematics
from .Segment import Segment
from .Arc1 import Arc1
from .Arc3 import Arc3
from numpy import arcsin, exp, cos, pi, sin
from .SurfLine import SurfLine
from ..Functions.labels import WIND_LAB, DRAW_PROP_LAB, SOP_LAB

from numpy import isnan
from ._check import InitUnKnowClassError


class SlotW12(Slot):

    VERSION = 1
    IS_SYMMETRICAL = 1

    # cf Methods.Slot.SlotW12._comp_line_dict
    def _comp_line_dict(self):
        """Define a dictionnary of the lines to draw the slot
        If a line has begin==end, it is replaced by "None" (dict has always the same number of keys)

        Parameters
        ----------
        self : SlotW12
            A SlotW12 object

        Returns
        -------
        line_dict: dict
            Dictionnary of the slot lines (key: line name, value: line object)
        """

        if self.is_outwards():
            rot_sign = True
        else:  # inward slot
            rot_sign = False

        point_dict = self._comp_point_coordinate()
        Z1 = point_dict["Z1"]
        Z2 = point_dict["Z2"]
        Z3 = point_dict["Z3"]
        Z4 = point_dict["Z4"]
        Z5 = point_dict["Z5"]
        Z6 = point_dict["Z6"]
        Z7 = point_dict["Z7"]
        Z8 = point_dict["Z8"]

        # Creation of curve
        line_dict = dict()
        line_dict["1-2"] = Segment(Z1, Z2)

        if self.R1 > 0:  # R1=0 => Z2==Z3
            line_dict["2-3"] = Arc3(Z2, Z3, rot_sign)
        else:
            line_dict["2-3"] = None

        if self.H1 > 0:  # H1=0 => Z3==Z4
            line_dict["3-4"] = Segment(Z3, Z4)
        else:
            line_dict["3-4"] = None

        line_dict["4-5"] = Arc3(Z4, Z5, rot_sign)

        if self.H1 > 0:  # H1=0 => Z5==Z6
            line_dict["5-6"] = Segment(Z5, Z6)
        else:
            line_dict["5-6"] = None

        if self.R1 > 0:  # R1=0 => Z6==Z7
            line_dict["6-7"] = Arc3(Z6, Z7, rot_sign)
        else:
            line_dict["6-7"] = None

        line_dict["7-8"] = Segment(Z7, Z8)

        # Closing Arc
        line_dict["8-1"] = Arc1(Z8, Z1, -self.get_Rbo(), is_trigo_direction=False)

        # Closing Active part
        line_dict["3-6"] = Segment(Z3, Z6)
        line_dict["6-3"] = Segment(Z6, Z3)

        return line_dict

    # cf Methods.Slot.SlotW12._comp_point_coordinate
    def _comp_point_coordinate(self):
        """Compute the point coordinates needed to plot the Slot.

        Parameters
        ----------
        self : SlotW12
            A SlotW12 object

        Returns
        -------
        point_dict: dict
            A dict of the slot coordinates
        """
        Rbo = self.get_Rbo()

        # alpha is the angle to rotate Z0 so ||Z1,Z8|| = 2*R2
        alpha = float(arcsin(self.R2 / Rbo))

        # comp point coordinate (in complex)
        Z0 = Rbo * exp(1j * 0)
        Z1 = Z0 * exp(-1j * alpha)

        if self.is_outwards():
            Z2 = Z1 + self.H0
            Z3 = Z2 + self.R1 * 2
            Z4 = Z3 + self.H1
            Zc1 = Z2 + self.R1
            Zi2 = Z4.real + self.R2
        else:  # inward slot
            Z2 = Z1 - self.H0
            Z3 = Z2 - self.R1 * 2
            Z4 = Z3 - self.H1
            Zc1 = Z2 - self.R1
            Zi2 = Z4.real - self.R2
        Zc2 = Z4.real

        point_dict = dict()
        # symetry
        point_dict["Z1"] = Z1
        point_dict["Z2"] = Z2
        point_dict["Z3"] = Z3
        point_dict["Z4"] = Z4
        point_dict["Zc1"] = Zc1
        point_dict["Zc2"] = Zc2
        point_dict["Z5"] = Z4.conjugate()
        point_dict["Z6"] = Z3.conjugate()
        point_dict["Z7"] = Z2.conjugate()
        point_dict["Z8"] = Z1.conjugate()
        point_dict["Zc3"] = Zc1.conjugate()
        point_dict["Zi1"] = Zc1 - 1j * self.R1
        point_dict["Zi2"] = Zi2
        point_dict["Zi3"] = point_dict["Zc3"] + 1j * self.R1

        return point_dict

    # cf Methods.Slot.SlotW12.build_geometry
    def build_geometry(self):
        """Compute the curve (Line) needed to plot the object.
        The ending point of a curve is the starting point of the next curve
        in the list

        Parameters
        ----------
        self : SlotW12
            A SlotW12 object

        Returns
        -------
        curve_list: list
            A list of 4 Segment and 3 Arc3

        """

        line_dict = self._comp_line_dict()

        curve_list = [
            line_dict["1-2"],
            line_dict["2-3"],
            line_dict["3-4"],
            line_dict["4-5"],
            line_dict["5-6"],
            line_dict["6-7"],
            line_dict["7-8"],
        ]
        return [line for line in curve_list if line is not None]

    # cf Methods.Slot.SlotW12.check
    check = check

    # cf Methods.Slot.SlotW12.comp_angle_opening
    def comp_angle_opening(self):
        """Compute the average opening angle of the Slot

        Parameters
        ----------
        self : SlotW12
            A SlotW12 object

        Returns
        -------
        alpha: float
            Average opening angle of the slot [rad]

        """

        Rbo = self.get_Rbo()

        return float(2 * arcsin(self.R2 / Rbo))

    # cf Methods.Slot.SlotW12.comp_height
    def comp_height(self):
        """Compute the height of the Slot.
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotW12
            A SlotW12 object

        Returns
        -------
        Htot: float
            Height of the slot [m]

        """

        Rbo = self.get_Rbo()

        # Computation of the arc height
        alpha = self.comp_angle_opening() / 2
        Harc = float(Rbo * (1 - cos(alpha)))

        if self.is_outwards():
            return self.H0 - Harc + self.R1 * 2 + self.H1 + self.R2
        else:
            return self.H0 + Harc + self.R1 * 2 + self.H1 + self.R2

    # cf Methods.Slot.SlotW12.comp_height_active
    def comp_height_active(self):
        """Compute the height of the winding area

        Parameters
        ----------
        self : SlotW12
            A SlotW12 object

        Returns
        -------
        Hwind: float
            Height of the winding area [m]

        """

        return self.H1 + self.R2

    # cf Methods.Slot.SlotW12.comp_surface
    def comp_surface(self):
        """Compute the Slot total surface (by analytical computation).
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotW12
            A SlotW12 object

        Returns
        -------
        S: float
            Slot total surface [m**2]

        """
        return self.comp_surface_active() + self.comp_surface_opening()

    # cf Methods.Slot.SlotW12.comp_surface_active
    def comp_surface_active(self):
        """Compute the Slot inner surface for winding (by analytical computation)

        Parameters
        ----------
        self : SlotW12
            A SlotW12 object

        Returns
        -------
        Swind: float
            Slot inner surface for winding [m**2]

        """

        S3 = 2 * self.R2 * self.H1
        S4 = pi * self.R2**2 / 2.0

        return S3 + S4

    # cf Methods.Slot.SlotW12.comp_surface_opening
    def comp_surface_opening(self):
        """Compute the Slot opening surface (by analytical computation).
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotW12
            A SlotW12 object

        Returns
        -------
        Sop: float
            Slot opening surface [m**2]

        """

        Rbo = self.get_Rbo()

        S1 = self.H0 * 2 * self.R2
        S2 = 4 * self.R1 * self.R2
        S3 = pi * self.R1**2

        # The bottom is an arc
        alpha = self.comp_angle_opening()
        Sarc = (Rbo**2.0) / 2.0 * (alpha - sin(alpha))

        # Because Slamination = S - Zs * Sslot
        if self.is_outwards():
            return S1 + S2 + S3 - Sarc
        else:
            return S1 + S2 + S3 + Sarc

    # cf Methods.Slot.SlotW12.get_surface_active
    def get_surface_active(self, alpha=0, delta=0):
        """Return the full winding surface

        Parameters
        ----------
        self : SlotW12
            A SlotW12 object
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
        line_dict = self._comp_line_dict()
        curve_list = [
            line_dict["3-4"],
            line_dict["4-5"],
            line_dict["5-6"],
            line_dict["6-3"],
        ]
        curve_list = [line for line in curve_list if line is not None]

        # Only the closing arc (6-3) needs to be drawn (in FEMM)
        for curve in curve_list[:-1]:
            if curve.prop_dict is None:
                curve.prop_dict = dict()
            curve.prop_dict.update({DRAW_PROP_LAB: False})

        # Create surface
        if self.is_outwards():
            Zmid = self.get_Rbo() + self.H0 + 2 * self.R1 + self.H1
        else:
            Zmid = self.get_Rbo() - self.H0 - 2 * self.R1 - self.H1
        label = self.parent.get_label() + "_" + WIND_LAB + "_R0-T0-S0"
        surface = SurfLine(line_list=curve_list, label=label, point_ref=Zmid)

        # Apply transformation
        surface.rotate(alpha)
        surface.translate(delta)

        return surface

    # cf Methods.Slot.SlotW12.get_surface_opening
    def get_surface_opening(self, alpha=0, delta=0):
        """Return the list of surfaces defining the opening area of the Slot

        Parameters
        ----------
        self : SlotW12
            A SlotW12 object
        alpha : float
            float number for rotation (Default value = 0) [rad]
        delta : complex
            complex number for translation (Default value = 0)

        Returns
        -------
        surf_list : list
            list of surfaces objects
        """

        # H0=R1=0 no opening
        if self.H0 == 0 and self.R1 == 0:
            return []

        # Create curve list
        line_dict = self._comp_line_dict()
        curve_list = [
            line_dict["1-2"],
            line_dict["2-3"],
            line_dict["3-6"],
            line_dict["6-7"],
            line_dict["7-8"],
            line_dict["8-1"],
        ]
        curve_list = [line for line in curve_list if line is not None]

        # Only the closing arc (8-1) needs to be drawn (in FEMM)
        for curve in curve_list[:-1]:
            if curve.prop_dict is None:
                curve.prop_dict = dict()
            curve.prop_dict.update({DRAW_PROP_LAB: False})

        # Create surface
        if self.is_outwards():
            Zmid = self.get_Rbo() + (self.H0 + self.R1 * 2) / 2
        else:
            Zmid = self.get_Rbo() - (self.H0 + self.R1 * 2) / 2
        label = self.parent.get_label() + "_" + SOP_LAB + "_R0-T0-S0"
        surface = SurfLine(line_list=curve_list, label=label, point_ref=Zmid)

        # Apply transformation
        surface.rotate(alpha)
        surface.translate(delta)

        return [surface]

    # cf Methods.Slot.SlotW12.plot_schematics
    plot_schematics = plot_schematics
    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        H0=0.003,
        H1=0,
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
            if "H0" in list(init_dict.keys()):
                H0 = init_dict["H0"]
            if "H1" in list(init_dict.keys()):
                H1 = init_dict["H1"]
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
        self.H0 = H0
        self.H1 = H1
        self.R1 = R1
        self.R2 = R2
        # Call Slot init
        super(SlotW12, self).__init__(Zs=Zs, wedge_mat=wedge_mat, is_bore=is_bore)
        # The class is frozen (in Slot init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        SlotW12_str = ""
        # Get the properties inherited from Slot
        SlotW12_str += super(SlotW12, self).__str__()
        SlotW12_str += "H0 = " + str(self.H0) + linesep
        SlotW12_str += "H1 = " + str(self.H1) + linesep
        SlotW12_str += "R1 = " + str(self.R1) + linesep
        SlotW12_str += "R2 = " + str(self.R2) + linesep
        return SlotW12_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from Slot
        if not super(SlotW12, self).__eq__(other):
            return False
        if other.H0 != self.H0:
            return False
        if other.H1 != self.H1:
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
            super(SlotW12, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
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
        S += super(SlotW12, self).__sizeof__()
        S += getsizeof(self.H0)
        S += getsizeof(self.H1)
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
        SlotW12_dict = super(SlotW12, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        SlotW12_dict["H0"] = self.H0
        SlotW12_dict["H1"] = self.H1
        SlotW12_dict["R1"] = self.R1
        SlotW12_dict["R2"] = self.R2
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        SlotW12_dict["__class__"] = "SlotW12"
        return SlotW12_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        H0_val = self.H0
        H1_val = self.H1
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
            H0=H0_val,
            H1=H1_val,
            R1=R1_val,
            R2=R2_val,
            Zs=Zs_val,
            wedge_mat=wedge_mat_val,
            is_bore=is_bore_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.H0 = None
        self.H1 = None
        self.R1 = None
        self.R2 = None
        # Set to None the properties inherited from Slot
        super(SlotW12, self)._set_None()

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
        doc="""Slot middle height

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
        doc="""Wedges radius

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
        doc="""Slot bottom radius

        :Type: float
        :min: 0
        """,
    )
