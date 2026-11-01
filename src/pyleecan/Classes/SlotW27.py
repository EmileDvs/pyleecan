# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Slot/SlotW27.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Slot/SlotW27
"""

# Inline fallback report:
# These methods remain imported because their source or imports cannot be safely moved into this class.
# - check: module uses a wildcard import whose names cannot be resolved safely
# - plot_schematics: import name 'Arc1' refers to different sources (.Arc1.Arc1 and ..Methods.Slot.SlotW27.plot_schematics.Arc1)

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
from ..Methods.Slot.SlotW27.check import check
from ..Methods.Slot.SlotW27.plot_schematics import plot_schematics
from .Segment import Segment
from .Arc1 import Arc1
from numpy import arcsin, exp, cos, sin
from ..Functions.labels import WIND_LAB, DRAW_PROP_LAB, SOP_LAB
from .SurfLine import SurfLine

from numpy import isnan
from ._check import InitUnKnowClassError


class SlotW27(Slot):
    """semi-closed trapezoidal without fillet without wedge (flat bottom)"""

    VERSION = 1
    IS_SYMMETRICAL = 1

    # cf Methods.Slot.SlotW27._comp_line_dict
    def _comp_line_dict(self):
        """Define a dictionnary of the lines to draw the slot
        If a line has begin==end, it is replaced by "None" (dict has always the same number of keys)

        Parameters
        ----------
        self : SlotW27
            A SlotW27 object

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

        # Creation of curve
        line_dict = dict()
        line_dict["1-2"] = Segment(Z1, Z2)
        line_dict["2-3"] = Segment(Z2, Z3)
        line_dict["3-4"] = Segment(Z3, Z4)
        line_dict["4-5"] = Segment(Z4, Z5)
        line_dict["5-6"] = Segment(Z5, Z6)
        line_dict["6-7"] = Segment(Z6, Z7)
        line_dict["7-8"] = Segment(Z7, Z8)
        line_dict["8-9"] = Segment(Z8, Z9)
        line_dict["9-10"] = Segment(Z9, Z10)

        # Closing Arc (Rbo)
        line_dict["10-1"] = Arc1(Z10, Z1, -self.get_Rbo(), is_trigo_direction=False)

        # Closing Active part
        line_dict["2-9"] = Segment(Z2, Z9)
        line_dict["9-2"] = Segment(Z9, Z2)

        return line_dict

    # cf Methods.Slot.SlotW27._comp_point_coordinate
    def _comp_point_coordinate(self):
        """Compute the point coordinates needed to plot the Slot.

        Parameters
        ----------
        self : SlotW27
            A SlotW27 object

        Returns
        -------
        point_dict: dict
            A dict of the slot point coordinates
        """
        Rbo = self.get_Rbo()

        # alpha is the angle to rotate Z0 so ||Z1,Z10|| = W0
        alpha = float(arcsin(self.W0 / (2 * Rbo)))

        # comp point coordinate (in complex)
        Z0 = Rbo * exp(1j * 0)
        Z1 = Z0 * exp(-1j * alpha)

        if self.is_outwards():
            Z2 = Z1 + self.H0
            Z3 = Z2 - (self.W1 - self.W0) * 1j / 2.0
            Z4 = Z3 + self.H1 - (self.W2 - self.W1) / 2.0 * 1j
            Z5 = Z4 + self.H2 - (self.W3 - self.W2) / 2.0 * 1j
        else:  # inward slot
            Z2 = Z1 - self.H0
            Z3 = Z2 - (self.W1 - self.W0) * 1j / 2.0
            Z4 = Z3 - self.H1 - (self.W2 - self.W1) / 2.0 * 1j
            Z5 = Z4 - self.H2 - (self.W3 - self.W2) / 2.0 * 1j

        point_dict = dict()
        # symetry
        point_dict["Z1"] = Z1
        point_dict["Z2"] = Z2
        point_dict["Z3"] = Z3
        point_dict["Z4"] = Z4
        point_dict["Z5"] = Z5
        point_dict["Z6"] = Z5.conjugate()
        point_dict["Z7"] = Z4.conjugate()
        point_dict["Z8"] = Z3.conjugate()
        point_dict["Z9"] = Z2.conjugate()
        point_dict["Z10"] = Z1.conjugate()
        return point_dict

    # cf Methods.Slot.SlotW27.build_geometry
    def build_geometry(self):
        """Compute the curve (Line) needed to plot the object.
        The ending point of a curve is the starting point of the next curve in
        the list

        Parameters
        ----------
        self : SlotW27
            A SlotW27 object

        Returns
        -------
        curve_list: list
            A list of 9 Segment

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
            line_dict["8-9"],
            line_dict["9-10"],
        ]
        return [line for line in curve_list if line is not None]

    # cf Methods.Slot.SlotW27.check
    check = check

    # cf Methods.Slot.SlotW27.comp_angle_opening
    def comp_angle_opening(self):
        """Compute the average opening angle of the Slot

        Parameters
        ----------
        self : SlotW27
            A SlotW27 object

        Returns
        -------
        alpha: float
            Average opening angle of the slot [rad]

        """
        Rbo = self.get_Rbo()

        return float(2 * arcsin(self.W0 / (2 * Rbo)))

    # cf Methods.Slot.SlotW27.comp_height
    def comp_height(self):
        """Compute the height of the Slot.
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotW27
            A SlotW27 object

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
            return (
                abs(Rbo - Harc + self.H0 + self.H1 + self.H2 + 1j * self.W3 / 2.0) - Rbo
            )
        else:
            return self.H0 + self.H1 + self.H2 + Harc

    # cf Methods.Slot.SlotW27.comp_height_active
    def comp_height_active(self):
        """Compute the height of the winding area

        Parameters
        ----------
        self : SlotW27
            A SlotW27 object

        Returns
        -------
        Hwind: float
            Height of the winding area [m]

        """

        return self.H1 + self.H2

    # cf Methods.Slot.SlotW27.comp_surface
    def comp_surface(self):
        """Compute the Slot total surface (by analytical computation).
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotW27
            A SlotW27 object

        Returns
        -------
        S: float
            Slot total surface [m**2]

        """
        return self.comp_surface_active() + self.comp_surface_opening()

    # cf Methods.Slot.SlotW27.comp_surface_active
    def comp_surface_active(self):
        """Compute the Slot inner surface for winding (by analytical computation)

        Parameters
        ----------
        self : SlotW27
            A SlotW27 object

        Returns
        -------
        Swind: float
            Slot inner surface for winding [m**2]

        """

        S2 = 0.5 * (self.W1 + self.W2) * self.H1
        S3 = 0.5 * (self.W2 + self.W3) * self.H2

        return S2 + S3

    # cf Methods.Slot.SlotW27.comp_surface_opening
    def comp_surface_opening(self):
        """Compute the Slot total surface (by analytical computation).
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotW27
            A SlotW27 object

        Returns
        -------
        S: float
            Slot total surface [m**2]

        """
        Rbo = self.get_Rbo()

        S1 = self.H0 * self.W0

        # The bottom is an arc
        alpha = self.comp_angle_opening()
        Sarc = (Rbo**2.0) / 2.0 * (alpha - sin(alpha))

        # Because Slamination = S - Zs * Sslot
        if self.is_outwards():
            return S1 - Sarc
        else:
            return S1 + Sarc

    # cf Methods.Slot.SlotW27.get_surface_active
    def get_surface_active(self, alpha=0, delta=0):
        """Return the full winding surface

        Parameters
        ----------
        self : SlotW27
            A SlotW27 object
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
            line_dict["6-7"],
            line_dict["7-8"],
            line_dict["8-9"],
            line_dict["9-2"],
        ]
        curve_list = [line for line in curve_list if line is not None]

        # Only the closing arc (9-2) needs to be drawn (in FEMM)
        for curve in curve_list[:-1]:
            if curve.prop_dict is None:
                curve.prop_dict = dict()
            curve.prop_dict.update({DRAW_PROP_LAB: False})

        # Create surface
        if self.is_outwards():
            Zmid = self.get_Rbo() + self.H0 + self.H1
        else:
            Zmid = self.get_Rbo() - self.H0 - self.H1
        label = self.parent.get_label() + "_" + WIND_LAB + "_R0-T0-S0"
        surface = SurfLine(line_list=curve_list, label=label, point_ref=Zmid)

        # Apply transformation
        surface.rotate(alpha)
        surface.translate(delta)

        return surface

    # cf Methods.Slot.SlotW27.get_surface_opening
    def get_surface_opening(self, alpha=0, delta=0):
        """Return the list of surfaces defining the opening area of the Slot

        Parameters
        ----------
        self : SlotW27
            A SlotW27 object
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
            line_dict["2-9"],
            line_dict["9-10"],
            line_dict["10-1"],
        ]
        curve_list = [line for line in curve_list if line is not None]

        # Only the closing arc (10-1) needs to be drawn (in FEMM)
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

    # cf Methods.Slot.SlotW27.plot_schematics
    plot_schematics = plot_schematics
    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        H0=0.003,
        H1=0,
        H2=0.02,
        W0=0.003,
        W1=0.013,
        W2=0.01,
        W3=0.003,
        is_trap_wind=False,
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
            if "H2" in list(init_dict.keys()):
                H2 = init_dict["H2"]
            if "W0" in list(init_dict.keys()):
                W0 = init_dict["W0"]
            if "W1" in list(init_dict.keys()):
                W1 = init_dict["W1"]
            if "W2" in list(init_dict.keys()):
                W2 = init_dict["W2"]
            if "W3" in list(init_dict.keys()):
                W3 = init_dict["W3"]
            if "is_trap_wind" in list(init_dict.keys()):
                is_trap_wind = init_dict["is_trap_wind"]
            if "Zs" in list(init_dict.keys()):
                Zs = init_dict["Zs"]
            if "wedge_mat" in list(init_dict.keys()):
                wedge_mat = init_dict["wedge_mat"]
            if "is_bore" in list(init_dict.keys()):
                is_bore = init_dict["is_bore"]
        # Set the properties (value check and convertion are done in setter)
        self.H0 = H0
        self.H1 = H1
        self.H2 = H2
        self.W0 = W0
        self.W1 = W1
        self.W2 = W2
        self.W3 = W3
        self.is_trap_wind = is_trap_wind
        # Call Slot init
        super(SlotW27, self).__init__(Zs=Zs, wedge_mat=wedge_mat, is_bore=is_bore)
        # The class is frozen (in Slot init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        SlotW27_str = ""
        # Get the properties inherited from Slot
        SlotW27_str += super(SlotW27, self).__str__()
        SlotW27_str += "H0 = " + str(self.H0) + linesep
        SlotW27_str += "H1 = " + str(self.H1) + linesep
        SlotW27_str += "H2 = " + str(self.H2) + linesep
        SlotW27_str += "W0 = " + str(self.W0) + linesep
        SlotW27_str += "W1 = " + str(self.W1) + linesep
        SlotW27_str += "W2 = " + str(self.W2) + linesep
        SlotW27_str += "W3 = " + str(self.W3) + linesep
        SlotW27_str += "is_trap_wind = " + str(self.is_trap_wind) + linesep
        return SlotW27_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from Slot
        if not super(SlotW27, self).__eq__(other):
            return False
        if other.H0 != self.H0:
            return False
        if other.H1 != self.H1:
            return False
        if other.H2 != self.H2:
            return False
        if other.W0 != self.W0:
            return False
        if other.W1 != self.W1:
            return False
        if other.W2 != self.W2:
            return False
        if other.W3 != self.W3:
            return False
        if other.is_trap_wind != self.is_trap_wind:
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
            super(SlotW27, self).compare(
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
            other._W2 is not None
            and self._W2 is not None
            and isnan(other._W2)
            and isnan(self._W2)
        ):
            pass
        elif other._W2 != self._W2:
            if is_add_value:
                val_str = " (self=" + str(self._W2) + ", other=" + str(other._W2) + ")"
                diff_list.append(name + ".W2" + val_str)
            else:
                diff_list.append(name + ".W2")
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
        if other._is_trap_wind != self._is_trap_wind:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._is_trap_wind)
                    + ", other="
                    + str(other._is_trap_wind)
                    + ")"
                )
                diff_list.append(name + ".is_trap_wind" + val_str)
            else:
                diff_list.append(name + ".is_trap_wind")
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from Slot
        S += super(SlotW27, self).__sizeof__()
        S += getsizeof(self.H0)
        S += getsizeof(self.H1)
        S += getsizeof(self.H2)
        S += getsizeof(self.W0)
        S += getsizeof(self.W1)
        S += getsizeof(self.W2)
        S += getsizeof(self.W3)
        S += getsizeof(self.is_trap_wind)
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
        SlotW27_dict = super(SlotW27, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        SlotW27_dict["H0"] = self.H0
        SlotW27_dict["H1"] = self.H1
        SlotW27_dict["H2"] = self.H2
        SlotW27_dict["W0"] = self.W0
        SlotW27_dict["W1"] = self.W1
        SlotW27_dict["W2"] = self.W2
        SlotW27_dict["W3"] = self.W3
        SlotW27_dict["is_trap_wind"] = self.is_trap_wind
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        SlotW27_dict["__class__"] = "SlotW27"
        return SlotW27_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        H0_val = self.H0
        H1_val = self.H1
        H2_val = self.H2
        W0_val = self.W0
        W1_val = self.W1
        W2_val = self.W2
        W3_val = self.W3
        is_trap_wind_val = self.is_trap_wind
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
            H2=H2_val,
            W0=W0_val,
            W1=W1_val,
            W2=W2_val,
            W3=W3_val,
            is_trap_wind=is_trap_wind_val,
            Zs=Zs_val,
            wedge_mat=wedge_mat_val,
            is_bore=is_bore_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.H0 = None
        self.H1 = None
        self.H2 = None
        self.W0 = None
        self.W1 = None
        self.W2 = None
        self.W3 = None
        self.is_trap_wind = None
        # Set to None the properties inherited from Slot
        super(SlotW27, self)._set_None()

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
        doc="""Slot first part height

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
        doc="""Slot second part height

        :Type: float
        :min: 0
        """,
    )

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
        doc="""Slot top width.

        :Type: float
        :min: 0
        """,
    )

    def _get_W2(self):
        """getter of W2"""
        return self._W2

    def _set_W2(self, value):
        """setter of W2"""
        check_var("W2", value, "float", Vmin=0)
        self._W2 = value

    W2 = property(
        fget=_get_W2,
        fset=_set_W2,
        doc="""Slot middle width

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
        doc="""Slot bottom width.

        :Type: float
        :min: 0
        """,
    )

    def _get_is_trap_wind(self):
        """getter of is_trap_wind"""
        return self._is_trap_wind

    def _set_is_trap_wind(self, value):
        """setter of is_trap_wind"""
        check_var("is_trap_wind", value, "bool")
        self._is_trap_wind = value

    is_trap_wind = property(
        fget=_get_is_trap_wind,
        fset=_set_is_trap_wind,
        doc="""If True, split the winding on the  trapezium bases. Else split at the middle height as usual

        :Type: bool
        """,
    )
