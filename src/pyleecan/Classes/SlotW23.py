# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Slot/SlotW23.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Slot/SlotW23
"""

# Inline fallback report:
# These methods remain imported because their source or imports cannot be safely moved into this class.
# - check: module uses a wildcard import whose names cannot be resolved safely
# - plot_schematics: import name 'Arc1' refers to different sources (.Arc1.Arc1 and ..Methods.Slot.SlotW23.plot_schematics.Arc1)
# - plot_schematics_constant_tooth: import name 'Arc1' refers to different sources (.Arc1.Arc1 and ..Methods.Slot.SlotW23.plot_schematics_constant_tooth.Arc1)

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
from ..Methods.Slot.SlotW23.check import check
from ..Methods.Slot.SlotW23.plot_schematics import plot_schematics
from ..Methods.Slot.SlotW23.plot_schematics_constant_tooth import (
    plot_schematics_constant_tooth,
)
from .Segment import Segment
from .Arc1 import Arc1
from numpy import arcsin, exp, sqrt, abs as np_abs, pi, sin, tan
from pyleecan.Classes._check import check_var
from ..Functions.Geometry.inter_line_line import inter_line_line
from ..Functions.labels import WIND_LAB, DRAW_PROP_LAB, SOP_LAB
from .SurfLine import SurfLine

from numpy import isnan
from ._check import InitUnKnowClassError


class SlotW23(Slot):
    """semi-closed trapezoidal without fillet without wedge (rounded bottom)"""

    VERSION = 1
    IS_SYMMETRICAL = 1

    # cf Methods.Slot.SlotW23._comp_line_dict
    def _comp_line_dict(self):
        """Define a dictionnary of the lines to draw the slot
        If a line has begin==end, it is replaced by "None" (dict has always the same number of keys)

        Parameters
        ----------
        self : SlotW23
            A SlotW23 object

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

        # Creation of curve
        line_dict = dict()
        if self.H0 > 0:
            line_dict["1-2"] = Segment(Z1, Z2)
        else:
            line_dict["1-2"] = None
        line_dict["2-3"] = Segment(Z2, Z3)
        line_dict["3-4"] = Segment(Z3, Z4)
        line_dict["4-5"] = Arc1(Z4, Z5, abs(Z5))
        line_dict["5-6"] = Segment(Z5, Z6)
        line_dict["6-7"] = Segment(Z6, Z7)
        if self.H0 > 0:
            line_dict["7-8"] = Segment(Z7, Z8)
        else:
            line_dict["7-8"] = None

        # Closing Arc (Rbo)
        line_dict["8-1"] = Arc1(Z8, Z1, -self.get_Rbo(), is_trigo_direction=False)

        # Closing Active part
        line_dict["3-6"] = Segment(Z3, Z6)
        line_dict["6-3"] = Segment(Z6, Z3)
        line_dict["7-2"] = Segment(Z7, Z2)

        return line_dict

    # cf Methods.Slot.SlotW23._comp_point_coordinate
    def _comp_point_coordinate(self):
        """Compute the point coordinates needed to plot the Slot.

        Parameters
        ----------
        self : SlotW23
            A SlotW23 object

        Returns
        -------
        point_dict: dict
            A dict of the slot point coordinates
        """

        if self.is_cstt_tooth:
            # Compute W1 and W2 to match W3 tooth constraint
            self._comp_W()

        Rbo = self.get_Rbo()

        # alpha is the angle to rotate Z0 so ||Z1,Z8|| = W0
        alpha = float(arcsin(self.W0 / (2 * Rbo)))

        # comp point coordinate (in complex)
        Z0 = Rbo * exp(1j * 0)
        Z1 = Z0 * exp(-1j * alpha)

        if self.is_outwards():
            Z2 = (Rbo + self.H0) * exp(-1j * alpha)
            Z3 = Z2.real + self.get_H1() - 1j * self.W1 / 2

            H2 = sqrt(self.H2**2 - ((self.W2 - self.W1) / 2.0) ** 2)
            Z4 = Z3.real + H2 - 1j * self.W2 / 2
        else:  # inward slot
            Z2 = (Rbo - self.H0) * exp(-1j * alpha)
            Z3 = Z2.real - self.get_H1() - 1j * self.W1 / 2

            H2 = sqrt(self.H2**2 - ((self.W2 - self.W1) / 2.0) ** 2)
            Z4 = Z3.real - H2 - 1j * self.W2 / 2

        point_dict = dict()
        # symetry
        point_dict["Z1"] = Z1
        point_dict["Z2"] = Z2
        point_dict["Z3"] = Z3
        point_dict["Z4"] = Z4
        point_dict["Z5"] = Z4.conjugate()
        point_dict["Z6"] = Z3.conjugate()
        point_dict["Z7"] = Z2.conjugate()
        point_dict["Z8"] = Z1.conjugate()
        return point_dict

    # cf Methods.Slot.SlotW23._comp_W
    def _comp_W(self):
        """Compute W1 and W2 method (cste tooth compatibility)

        Parameters
        ----------
        self : SlotW23
            A SlotW23 object
        Zs : int
            Number of Slot

        Returns
        -------
        None

        """
        Rbo = self.get_Rbo()

        # To compute the slot width we use the fact that
        # alpha_tooth + alpha_slot = slot_pitch
        slot_pitch = 2 * pi / self.Zs

        # H0 and H1 are radial
        if self.is_outwards():
            R1 = Rbo + self.get_H1() + self.H0
        else:
            R1 = Rbo - self.get_H1() - self.H0

        alpha_T1 = float(arcsin(self.W3 / (2 * R1)))
        alpha_S1 = slot_pitch - 2 * alpha_T1
        self.W1 = 2 * sin(alpha_S1 / 2) * R1

        # H2 is parallel to the tooth axis
        if self.is_outwards():
            R2 = np_abs(R1 * exp(1j * alpha_T1) + self.H2)
        else:
            R2 = np_abs(R1 * exp(1j * alpha_T1) - self.H2)

        alpha_T2 = float(arcsin(self.W3 / (2 * R2)))
        alpha_S2 = slot_pitch - 2 * alpha_T2
        self.W2 = 2 * sin(alpha_S2 / 2) * R2

    # cf Methods.Slot.SlotW23._set_W3
    def _set_W3(self, value):
        """setter of W3"""
        check_var("W3", value, "float", Vmin=0)
        self._W3 = value

        # Compute W1 and W2 to match W3 tooth constraint
        try:
            self._comp_W()
        except Exception:
            pass

    # cf Methods.Slot.SlotW23.build_geometry
    def build_geometry(self):
        """Compute the curve (Line) needed to plot the object.
        The ending point of a curve is the starting point of the next curve in
        the list

        Parameters
        ----------
        self : SlotW23
            A SlotW23 object

        Returns
        -------
        curve_list: list
            A list of 6 Segment and 1 Arc

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

    # cf Methods.Slot.SlotW23.check
    check = check

    # cf Methods.Slot.SlotW23.comp_angle_opening
    def comp_angle_opening(self):
        """Compute the average opening angle of the Slot

        Parameters
        ----------
        self : SlotW23
            A SlotW23 object

        Returns
        -------
        alpha: float
            Average opening angle of the slot [rad]

        """

        Rbo = self.get_Rbo()

        return float(2 * arcsin(self.W0 / (2 * Rbo)))

    # cf Methods.Slot.SlotW23.comp_height
    def comp_height(self):
        """Compute the height of the Slot.
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotW23
            A SlotW23 object

        Returns
        -------
        Htot: float
            Height of the slot [m]

        """

        Rbo = self.get_Rbo()
        point_dict = self._comp_point_coordinate()
        Z4 = point_dict["Z4"]

        if self.is_outwards():
            return abs(Z4) - Rbo
        else:
            return Rbo - abs(Z4)

    # cf Methods.Slot.SlotW23.comp_height_active
    def comp_height_active(self):
        """Compute the height of the winding area

        Parameters
        ----------
        self : SlotW23
            A SlotW23 object

        Returns
        -------
        Hwind: float
            Height of the winding area [m]

        """

        point_dict = self._comp_point_coordinate()
        Z3 = point_dict["Z3"]
        Z4 = point_dict["Z4"]
        Z6 = point_dict["Z6"]

        if self.is_outwards():
            return abs(Z4) - abs((Z3 + Z6) / 2)
        else:
            return abs(Z3) - abs(Z4)

    # cf Methods.Slot.SlotW23.comp_surface
    def comp_surface(self):
        """Compute the Slot total surface (by analytical computation).
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotW23
            A SlotW23 object

        Returns
        -------
        S: float
            Slot total surface [m**2]

        """

        return self.comp_surface_active() + self.comp_surface_opening()

    # cf Methods.Slot.SlotW23.comp_surface_active
    def comp_surface_active(self):
        """Compute the Slot inner surface for winding (by analytical computation)

        Parameters
        ----------
        self : SlotW23
            A SlotW23 object

        Returns
        -------
        Swind: float
            Slot inner surface for winding [m**2]

        """
        if self.is_cstt_tooth and (self.W1 is None or self.W2 is None):
            # Compute W1 and W2 to match W3 tooth constraint
            self._comp_W()

        Rbo = self.get_Rbo()

        # By Pythagore
        # self.H2 projection
        H2 = sqrt(self.H2**2 - ((self.W2 - self.W1) / 2.0) ** 2)
        S2 = 0.5 * (self.W1 + self.W2) * H2

        if self.is_outwards():
            Rslot = Rbo + self.comp_height()  # External radius of the slot
            alpha = float(2 * arcsin(self.W2 / (2 * Rslot)))  # W2 in rad
            S3 = (Rslot**2.0) / 2.0 * (alpha - sin(alpha))
            return S2 + S3
        else:
            Rslot = Rbo - self.comp_height()  # External radius of the slot
            alpha = float(2 * arcsin(self.W2 / (2 * Rslot)))  # W2 in rad
            S3 = (Rslot**2.0) / 2.0 * (alpha - sin(alpha))
            return S2 - S3

    # cf Methods.Slot.SlotW23.comp_surface_opening
    def comp_surface_opening(self):
        """Compute the Slot opening surface (by analytical computation).
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotW23
            A SlotW23 object

        Returns
        -------
        S: float
            Slot opening surface [m**2]

        """
        if self.is_cstt_tooth and (self.W1 is None or self.W2 is None):
            # Compute W1 and W2 to match W3 tooth constraint
            self._comp_W()

        Rbo = self.get_Rbo()

        # Wint is the with at the top of the opening
        alpha = self.comp_angle_opening()
        if self.is_outwards():
            Wint = 2 * sin(alpha / 2) * (Rbo + self.H0)
            # Arc between opening H0 and wedge H1
            Sarc = ((Rbo + self.H0) ** 2.0) / 2.0 * (alpha - sin(alpha))
            # The opening part is radial
            S1 = (pi * ((Rbo + self.H0) ** 2) - pi * (Rbo**2)) * alpha / (2 * pi) - Sarc
        else:
            Wint = 2 * sin(alpha / 2) * (Rbo - self.H0)
            # Arc between opening H0 and wedge H1
            Sarc = ((Rbo - self.H0) ** 2.0) / 2.0 * (alpha - sin(alpha))
            # The opening part is radial
            S1 = (pi * (Rbo**2) - pi * ((Rbo - self.H0) ** 2)) * alpha / (2 * pi) + Sarc

        S2 = 0.5 * self.get_H1() * (Wint + self.W1)

        return S1 + S2

    # cf Methods.Slot.SlotW23.get_H1
    def get_H1(self):
        """Return H1 in [m]

        Parameters
        ----------
        self : SlotW23
            A SlotW23 object

        Returns
        -------
        H1: float
            H1 in [m]

        """

        if not (self.H1_is_rad):
            return self.H1

        Rbo = self.get_Rbo()

        # alpha is the angle to rotate Z0 so ||Z1,Z8|| = W0
        alpha = float(arcsin(self.W0 / (2 * Rbo)))

        if self.is_outwards():
            Z2 = (Rbo + self.H0) * exp(-1j * alpha)

        else:  # inward slot
            Z2 = (Rbo - self.H0) * exp(-1j * alpha)

        if self.H1_is_rad:  # H1 in rad
            if self.is_cstt_tooth:
                Z2t = Z2 * exp(1j * pi / self.Zs)
                Zangle = exp(-1j * ((pi / 2) - self.H1)) + Z2t

                Zt1 = 1j * (self.W3 / 2)
                Zt2 = 1 + (1j * self.W3) / 2
                L = inter_line_line(Zt1, Zt2, Z2t, Zangle)
                Z3 = L[0]
                return abs(Z3.real - Z2.real)

            else:
                return (self.W1 - self.W0) * tan(self.H1) / 2.0  # convertion to m

    # cf Methods.Slot.SlotW23.get_surface_active
    def get_surface_active(self, alpha=0, delta=0):
        """Return the full winding surface

        Parameters
        ----------
        self : SlotW23
            A SlotW23 object
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
        if self.H1 != 0:
            curve_list = [
                line_dict["3-4"],
                line_dict["4-5"],
                line_dict["5-6"],
                line_dict["6-3"],
            ]
        else:
            # Add 2-3 and 7-2 to make sure that FEMM handles all the lines
            # cf (Tests\Validation\Magnetics\test_FEMM_fast_draw.py)
            curve_list = [
                line_dict["2-3"],
                line_dict["3-4"],
                line_dict["4-5"],
                line_dict["5-6"],
                line_dict["6-7"],
                line_dict["7-2"],
            ]
        curve_list = [line for line in curve_list if line is not None]

        # Only the closing arc (6-3) needs to be drawn (in FEMM)
        for curve in curve_list[:-1]:
            if curve.prop_dict is None:
                curve.prop_dict = dict()
            curve.prop_dict.update({DRAW_PROP_LAB: False})

        # Create surface
        if self.is_outwards():
            Zmid = self.get_Rbo() + self.H0 + self.get_H1() + self.H2 / 2
        else:
            Zmid = self.get_Rbo() - self.H0 - self.get_H1() - self.H2 / 2
        label = self.parent.get_label() + "_" + WIND_LAB + "_R0-T0-S0"
        surface = SurfLine(line_list=curve_list, label=label, point_ref=Zmid)

        # Apply transformation
        surface.rotate(alpha)
        surface.translate(delta)

        return surface

    # cf Methods.Slot.SlotW23.get_surface_opening
    def get_surface_opening(self, alpha=0, delta=0):
        """Return the list of surfaces defining the opening area of the Slot

        Parameters
        ----------
        self : SlotW23
            A SlotW23 object
        alpha : float
            float number for rotation (Default value = 0) [rad]
        delta : complex
            complex number for translation (Default value = 0)

        Returns
        -------
        surf_list : list
            list of surfaces objects
        """

        # H0=H1=0 no opening
        if self.H0 == 0 and self.get_H1() == 0:
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
            Zmid = self.get_Rbo() + self.H0 / 2
        else:
            Zmid = self.get_Rbo() - self.H0 / 2
        label = self.parent.get_label() + "_" + SOP_LAB + "_R0-T0-S0"
        surface = SurfLine(line_list=curve_list, label=label, point_ref=Zmid)

        # Apply transformation
        surface.rotate(alpha)
        surface.translate(delta)

        return [surface]

    # cf Methods.Slot.SlotW23.plot_schematics
    plot_schematics = plot_schematics
    # cf Methods.Slot.SlotW23.plot_schematics_constant_tooth
    plot_schematics_constant_tooth = plot_schematics_constant_tooth
    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        W0=None,
        H0=None,
        H1=None,
        W1=None,
        H2=None,
        W2=None,
        H1_is_rad=False,
        is_cstt_tooth=False,
        W3=None,
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
            if "H1" in list(init_dict.keys()):
                H1 = init_dict["H1"]
            if "W1" in list(init_dict.keys()):
                W1 = init_dict["W1"]
            if "H2" in list(init_dict.keys()):
                H2 = init_dict["H2"]
            if "W2" in list(init_dict.keys()):
                W2 = init_dict["W2"]
            if "H1_is_rad" in list(init_dict.keys()):
                H1_is_rad = init_dict["H1_is_rad"]
            if "is_cstt_tooth" in list(init_dict.keys()):
                is_cstt_tooth = init_dict["is_cstt_tooth"]
            if "W3" in list(init_dict.keys()):
                W3 = init_dict["W3"]
            if "Zs" in list(init_dict.keys()):
                Zs = init_dict["Zs"]
            if "wedge_mat" in list(init_dict.keys()):
                wedge_mat = init_dict["wedge_mat"]
            if "is_bore" in list(init_dict.keys()):
                is_bore = init_dict["is_bore"]
        # Set the properties (value check and convertion are done in setter)
        self.W0 = W0
        self.H0 = H0
        self.H1 = H1
        self.W1 = W1
        self.H2 = H2
        self.W2 = W2
        self.H1_is_rad = H1_is_rad
        self.is_cstt_tooth = is_cstt_tooth
        self.W3 = W3
        # Call Slot init
        super(SlotW23, self).__init__(Zs=Zs, wedge_mat=wedge_mat, is_bore=is_bore)
        # The class is frozen (in Slot init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        SlotW23_str = ""
        # Get the properties inherited from Slot
        SlotW23_str += super(SlotW23, self).__str__()
        SlotW23_str += "W0 = " + str(self.W0) + linesep
        SlotW23_str += "H0 = " + str(self.H0) + linesep
        SlotW23_str += "H1 = " + str(self.H1) + linesep
        SlotW23_str += "W1 = " + str(self.W1) + linesep
        SlotW23_str += "H2 = " + str(self.H2) + linesep
        SlotW23_str += "W2 = " + str(self.W2) + linesep
        SlotW23_str += "H1_is_rad = " + str(self.H1_is_rad) + linesep
        SlotW23_str += "is_cstt_tooth = " + str(self.is_cstt_tooth) + linesep
        SlotW23_str += "W3 = " + str(self.W3) + linesep
        return SlotW23_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from Slot
        if not super(SlotW23, self).__eq__(other):
            return False
        if other.W0 != self.W0:
            return False
        if other.H0 != self.H0:
            return False
        if other.H1 != self.H1:
            return False
        if other.W1 != self.W1:
            return False
        if other.H2 != self.H2:
            return False
        if other.W2 != self.W2:
            return False
        if other.H1_is_rad != self.H1_is_rad:
            return False
        if other.is_cstt_tooth != self.is_cstt_tooth:
            return False
        if other.W3 != self.W3:
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
            super(SlotW23, self).compare(
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
        if other._H1_is_rad != self._H1_is_rad:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._H1_is_rad)
                    + ", other="
                    + str(other._H1_is_rad)
                    + ")"
                )
                diff_list.append(name + ".H1_is_rad" + val_str)
            else:
                diff_list.append(name + ".H1_is_rad")
        if other._is_cstt_tooth != self._is_cstt_tooth:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._is_cstt_tooth)
                    + ", other="
                    + str(other._is_cstt_tooth)
                    + ")"
                )
                diff_list.append(name + ".is_cstt_tooth" + val_str)
            else:
                diff_list.append(name + ".is_cstt_tooth")
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
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from Slot
        S += super(SlotW23, self).__sizeof__()
        S += getsizeof(self.W0)
        S += getsizeof(self.H0)
        S += getsizeof(self.H1)
        S += getsizeof(self.W1)
        S += getsizeof(self.H2)
        S += getsizeof(self.W2)
        S += getsizeof(self.H1_is_rad)
        S += getsizeof(self.is_cstt_tooth)
        S += getsizeof(self.W3)
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
        SlotW23_dict = super(SlotW23, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        SlotW23_dict["W0"] = self.W0
        SlotW23_dict["H0"] = self.H0
        SlotW23_dict["H1"] = self.H1
        SlotW23_dict["W1"] = self.W1
        SlotW23_dict["H2"] = self.H2
        SlotW23_dict["W2"] = self.W2
        SlotW23_dict["H1_is_rad"] = self.H1_is_rad
        SlotW23_dict["is_cstt_tooth"] = self.is_cstt_tooth
        SlotW23_dict["W3"] = self.W3
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        SlotW23_dict["__class__"] = "SlotW23"
        return SlotW23_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        W0_val = self.W0
        H0_val = self.H0
        H1_val = self.H1
        W1_val = self.W1
        H2_val = self.H2
        W2_val = self.W2
        H1_is_rad_val = self.H1_is_rad
        is_cstt_tooth_val = self.is_cstt_tooth
        W3_val = self.W3
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
            H1=H1_val,
            W1=W1_val,
            H2=H2_val,
            W2=W2_val,
            H1_is_rad=H1_is_rad_val,
            is_cstt_tooth=is_cstt_tooth_val,
            W3=W3_val,
            Zs=Zs_val,
            wedge_mat=wedge_mat_val,
            is_bore=is_bore_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.W0 = None
        self.H0 = None
        self.H1 = None
        self.W1 = None
        self.H2 = None
        self.W2 = None
        self.H1_is_rad = None
        self.is_cstt_tooth = None
        self.W3 = None
        # Set to None the properties inherited from Slot
        super(SlotW23, self)._set_None()

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
        doc="""height or angle  (See Schematics)

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
        doc="""Slot height below wedge 

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
        doc="""Slot bottom width.

        :Type: float
        :min: 0
        """,
    )

    def _get_H1_is_rad(self):
        """getter of H1_is_rad"""
        return self._H1_is_rad

    def _set_H1_is_rad(self, value):
        """setter of H1_is_rad"""
        check_var("H1_is_rad", value, "bool")
        self._H1_is_rad = value

    H1_is_rad = property(
        fget=_get_H1_is_rad,
        fset=_set_H1_is_rad,
        doc="""H1 unit, 0 for m, 1 for rad

        :Type: bool
        """,
    )

    def _get_is_cstt_tooth(self):
        """getter of is_cstt_tooth"""
        return self._is_cstt_tooth

    def _set_is_cstt_tooth(self, value):
        """setter of is_cstt_tooth"""
        check_var("is_cstt_tooth", value, "bool")
        self._is_cstt_tooth = value

    is_cstt_tooth = property(
        fget=_get_is_cstt_tooth,
        fset=_set_is_cstt_tooth,
        doc="""True: use W3 to define the slot, False: use W2 and W1

        :Type: bool
        """,
    )

    def _get_W3(self):
        """getter of W3"""
        return self._W3

    W3 = property(
        fget=_get_W3,
        fset=_set_W3,
        doc="""Tooth width

        :Type: float
        :min: 0
        """,
    )
