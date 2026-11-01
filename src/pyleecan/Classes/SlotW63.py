# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Slot/SlotW63.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Slot/SlotW63
"""

# Inline fallback report:
# These methods remain imported because their source or imports cannot be safely moved into this class.
# - check: module uses a wildcard import whose names cannot be resolved safely
# - plot_schematics: import name 'Arc1' refers to different sources (.Arc1.Arc1 and ..Methods.Slot.SlotW63.plot_schematics.Arc1)

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
from ..Methods.Slot.SlotW63.check import check
from ..Methods.Slot.SlotW63.plot_schematics import plot_schematics
from .Segment import Segment
from .Arc1 import Arc1
from numpy import pi, exp, arcsin, sin
from ..Functions.Geometry.inter_line_line import inter_line_line
from .SurfLine import SurfLine
from ..Methods.Slot.SlotW63 import S63_WindError
from ..Functions.labels import WIND_LAB, SOP_LAB, DRAW_PROP_LAB

from numpy import isnan
from ._check import InitUnKnowClassError


class SlotW63(Slot):

    VERSION = 1
    IS_SYMMETRICAL = 0

    # cf Methods.Slot.SlotW63._comp_line_dict
    def _comp_line_dict(self):
        """Define a dictionnary of the lines to draw the slot
        If a line has begin==end, it is replaced by "None" (dict has always the same number of keys)

        Parameters
        ----------
        self : SlotW63
            A SlotW63 object

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

        Zw1 = point_dict["Zw1"]
        Zw2 = point_dict["Zw2"]

        Zw1s = point_dict["Zw1s"]
        Zw2s = point_dict["Zw2s"]

        # Creation of curve
        line_dict = dict()
        line_dict["1-2"] = Segment(Z1, Z2)
        line_dict["2-3"] = Segment(Z2, Z3)
        line_dict["3-4"] = Segment(Z3, Z4)
        line_dict["4-5"] = Segment(Z4, Z5)
        line_dict["5-6"] = Segment(Z5, Z6)
        line_dict["6-7"] = Segment(Z6, Z7)
        line_dict["7-8"] = Segment(Z7, Z8)

        # Winding lines
        line_dict["w1-2"] = Segment(Zw1, Z2)
        line_dict["2-w1"] = Segment(Z2, Zw1)
        line_dict["4-w2"] = Segment(Z4, Zw2)
        line_dict["w2-w1"] = Segment(Zw2, Zw1)
        line_dict["w1-w2"] = Segment(Zw1, Zw2)

        line_dict["w2s-5"] = Segment(Zw2s, Z5)
        line_dict["7-w1s"] = Segment(Z7, Zw1s)
        line_dict["w1s-w2s"] = Segment(Zw1s, Zw2s)

        line_dict["w1s-7"] = Segment(Zw1s, Z7)

        line_dict["w2s-w1s"] = Segment(Zw2s, Zw1s)
        line_dict["w2-w2s"] = Segment(Zw2, Zw2s)

        line_dict["7-2"] = Segment(Z7, Z2)
        line_dict["2-7"] = Segment(Z2, Z7)

        line_dict["8-1"] = Arc1(Z8, Z1, -abs(Z8), is_trigo_direction=False)

        if self.H2 == 0:
            line_dict["7w-2w"] = Arc1(Z7, Z2, -abs(Z7), is_trigo_direction=False)

        return line_dict

    # cf Methods.Slot.SlotW63._comp_point_coordinate
    def _comp_point_coordinate(self):
        """Compute the point coordinate needed to plot the Slot.

        Parameters
        ----------
        self : SlotW63
            A SlotW63 object

        Returns
        -------
        point_dict: dict
            A dict of the slot point coordinates

        """

        Rbo = self.get_Rbo()
        hsp = pi / self.Zs  # Half slot pitch

        alpha = arcsin(self.W1 / (2 * Rbo))

        # Point used to define geometry of slot
        Z1 = Rbo * exp(1j * alpha)
        Z2 = Z1 - self.H2
        Z3 = (
            Z2
            - ((self.W1 - self.W0) / 2) * sin(self.H1)
            - 1j * ((self.W1 - self.W0) / 2)
        )
        Z4 = Z3 - self.H0

        # Set points in correct base with a rotation
        Z1 = Z1 * exp(-1j * hsp)
        Z2 = Z2 * exp(-1j * hsp)
        Z3 = Z3 * exp(-1j * hsp)
        Z4 = Z4 * exp(-1j * hsp)

        Z5 = Z4.conjugate()
        Z6 = Z3.conjugate()
        Z7 = Z2.conjugate()
        Z8 = Z1.conjugate()

        Zmid = (Z2 + Z7) / 2

        # Zw are points used to define geometry of winding
        Zw1 = Zmid - 1j * self.W2 / 2
        Zc = Zw1 - 1
        Zw2 = inter_line_line(Z5, Z4, Zw1, Zc)
        Zw2 = Zw2[0]

        Zw1s = Zw1.conjugate()
        Zw2s = Zw2.conjugate()

        point_dict = dict()
        # symetry
        point_dict["Z1"] = Z1
        point_dict["Z2"] = Z2
        point_dict["Z3"] = Z3
        point_dict["Z4"] = Z4
        point_dict["Z5"] = Z5
        point_dict["Z6"] = Z6
        point_dict["Z7"] = Z7
        point_dict["Z8"] = Z8

        point_dict["Zw1"] = Zw1
        point_dict["Zw2"] = Zw2
        point_dict["Zw1s"] = Zw1s
        point_dict["Zw2s"] = Zw2s

        return point_dict

    # cf Methods.Slot.SlotW63.build_geometry
    def build_geometry(self):
        """Compute the curve (Line) needed to plot the Slot.
        The ending point of a curve is the starting point of the next curve in
        the list

        Parameters
        ----------
        self : SlotW63
            A SlotW63 object

        Returns
        -------
        curve_list: list
            A list of 7 Segment

        """

        line_dict = self._comp_line_dict()

        if self.H2 != 0:
            # Creation of curve
            curve_list = [
                line_dict["1-2"],
                line_dict["2-3"],
                line_dict["3-4"],
                line_dict["4-5"],
                line_dict["5-6"],
                line_dict["6-7"],
                line_dict["7-8"],
            ]

        else:
            # Creation of curve
            curve_list = [
                line_dict["2-3"],
                line_dict["3-4"],
                line_dict["4-5"],
                line_dict["5-6"],
                line_dict["6-7"],
            ]

        return [line for line in curve_list if line is not None]

    # cf Methods.Slot.SlotW63.build_geometry_active
    def build_geometry_active(self, Nrad, Ntan, is_simplified=False, alpha=0, delta=0):
        """Split the slot winding area in several zone

        Parameters
        ----------
        self : SlotW63
            A SlotW63 object
        Nrad : int
            Number of radial layer
        Ntan : int
            Number of tangentiel layer
        is_simplified : bool
            boolean to specify if the coincident lines are considered as one
            or different lines (Default value = False)
        alpha : float
            Angle for rotation (Default value = 0) [rad]
        delta : complex
            complex for translation (Default value = 0)

        Returns
        -------
        surf_list: list
            List of surface delimiting the winding zone

        """

        if Nrad != 1 or Ntan != 2:
            raise S63_WindError(
                "Slot 63 can use only for winding with Nrad=1 and Ntan=2"
            )
        self.check()

        # get the name of the lamination
        lam_label = self.parent.get_label()

        line_dict = self._comp_line_dict()

        if self.W2 != 0:
            Ref1 = (line_dict["w1-2"].get_begin() + line_dict["4-w2"].get_begin()) / 2
            Ref2 = (line_dict["w1s-w2s"].get_begin() + line_dict["5-6"].get_begin()) / 2

            # Create the surfaces
            wind1_lines = [
                line_dict["w1-2"],
                line_dict["2-3"],
                line_dict["3-4"],
                line_dict["4-w2"],
                line_dict["w2-w1"],
            ]

            wind2_lines = [
                line_dict["w1s-w2s"],
                line_dict["w2s-5"],
                line_dict["5-6"],
                line_dict["6-7"],
                line_dict["7-w1s"],
            ]

            surf_list = list()
            surf_list.append(
                SurfLine(
                    line_list=wind1_lines,
                    label=f"{lam_label}_{WIND_LAB}_R0-T0-S0",
                    point_ref=Ref1,
                )
            )
            surf_list.append(
                SurfLine(
                    line_list=wind2_lines,
                    label=f"{lam_label}_{WIND_LAB}_R0-T1-S0",
                    point_ref=Ref2,
                )
            )

        else:
            Ref1 = (line_dict["7-2"].get_begin() + line_dict["4-5"].get_begin()) / 2

            # Create the surfaces
            wind1_lines = [
                line_dict["7-2"],
                line_dict["2-3"],
                line_dict["3-4"],
                line_dict["4-5"],
                line_dict["5-6"],
                line_dict["6-7"],
            ]

            surf_list = list()
            surf_list.append(
                SurfLine(
                    line_list=wind1_lines,
                    label=f"{lam_label}_{WIND_LAB}_R0-T0-S0",
                    point_ref=Ref1,
                )
            )

        # Rotate and translate the surfaces
        for surf in surf_list:
            surf.rotate(alpha)
            surf.translate(delta)

        return surf_list

    # cf Methods.Slot.SlotW63.check
    check = check

    # cf Methods.Slot.SlotW63.comp_angle_opening
    def comp_angle_opening(self):
        """Compute the average opening angle of the Slot

        Parameters
        ----------
        self : SlotW63
            A SlotW63 object

        Returns
        -------
        alpha: float
            Average opening angle of the slot [rad]

        """
        slot_pitch = 2 * pi / self.Zs
        tooth_angle = 2 * arcsin(self.W1 / (2 * self.get_Rbo()))

        return slot_pitch - tooth_angle

    # cf Methods.Slot.SlotW63.comp_height
    def comp_height(self):
        """Compute the height of the Slot.
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotW63
            A SlotW63 object

        Returns
        -------
        Htot: float
            Height of the slot [m]

        """

        Rbo = self.get_Rbo()
        point_dict = self._comp_point_coordinate()
        Z5 = point_dict["Z5"]
        Z4 = point_dict["Z4"]

        return Rbo - abs((Z5 + Z4) / 2)

    # cf Methods.Slot.SlotW63.comp_height_active
    def comp_height_active(self):
        """Compute the height of the winding area

        Parameters
        ----------
        self : SlotW63
            A SlotW63 object

        Returns
        -------
        Hwind: float
            Height of the winding area [m]

        """

        point_dict = self._comp_point_coordinate()
        Zw1 = point_dict["Zw1"]
        Zw2 = point_dict["Zw2"]

        return abs(Zw1 - Zw2)

    # cf Methods.Slot.SlotW63.comp_surface
    def comp_surface(self):
        """Compute the Slot total surface (by analytical computation).
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotW63
            A SlotW63 object

        Returns
        -------
        S: float
            Slot total surface [m**2]

        """

        point_dict = self._comp_point_coordinate()
        Z4 = point_dict["Z4"]
        Z5 = point_dict["Z5"]
        Rext = self.get_Rbo()
        Rint = abs(Z5)

        # Surface of a slot pitch
        Sring = (pi * Rext**2 - pi * Rint**2) / self.Zs

        # Surface define by arc of circle between Z4 and Z5 with radius abs(Z5)
        # bottom is not a cercle
        D54 = abs(Z5 - Z4)
        alpha = 2 * arcsin(D54 / (2 * Rint))
        Sarc_bot2 = (Rint**2.0) / 2.0 * (alpha - sin(alpha))

        # Tooth surface
        H = sin(self.H1) * (self.W1 - self.W0) / 2
        St = (
            self.H0 * self.W0
            + self.H2 * self.W1
            + H * (self.W1 - self.W0) / 2
            + self.W0 * H
        )

        # Surface define by arc of circle between Z8 and Z1d with radius rbo
        alpha_top = 2 * arcsin(self.W1 / (2 * Rext))
        Sarc_top = (Rext**2.0) / 2.0 * (alpha_top - sin(alpha_top))

        # Surface define by arc of circle between Z5 and Z4d with radius abs(Z5)
        alpha_bot = 2 * arcsin(self.W0 / (2 * Rint))
        Sarc_bot1 = (Rint**2.0) / 2.0 * (alpha_bot - sin(alpha_bot))

        return Sring - (St + Sarc_top - Sarc_bot1) + Sarc_bot2

    # cf Methods.Slot.SlotW63.comp_surface_active
    def comp_surface_active(self):
        """Compute the Slot inner surface for winding

        Parameters
        ----------
        self : SlotW63
            A SlotW63 object

        Returns
        -------
        Swind: float
            Slot inner surface for winding [m**2]

        """
        Rbo = self.get_Rbo()
        surface = self.comp_surface()

        point_dict = self._comp_point_coordinate()
        Zw1 = point_dict["Zw1"]
        Zw2 = point_dict["Zw2"]
        Z1 = point_dict["Z1"]
        Z2 = point_dict["Z2"]
        Z7 = point_dict["Z7"]
        Z8 = point_dict["Z8"]

        s_bottom = abs(Zw1 - Zw2) * self.W2

        # top cercle
        D81 = abs(Z8 - Z1)
        alpha = 2 * arcsin(D81 / (2 * Rbo))
        Sarc_top = (Rbo**2.0) / 2.0 * (alpha - sin(alpha))

        D72 = abs(Z7 - Z2)

        Striangle = (Z8.real - Z7.real) * (Z8.imag - Z7.imag)

        Srect = D72 * (Z8.real - Z7.real)

        return surface - s_bottom - Sarc_top - Striangle - Srect

    # cf Methods.Slot.SlotW63.get_surface_active
    def get_surface_active(self, alpha=0, delta=0):
        """Return the full winding surface

        Parameters
        ----------
        self : SlotW63
            A SlotW63 object
        alpha : float
            float number for rotation (Default value = 0) [rad]
        delta : complex
            complex number for translation (Default value = 0)

        Returns
        -------
        surf_wind: Surface
            Surface corresponding to the Winding Area
        """

        raise Exception("get_surface_active not available for SlotW63")

    # cf Methods.Slot.SlotW63.get_surface_opening
    def get_surface_opening(self, alpha=0, delta=0):
        """Return the list of surfaces defining the opening area of the Slot

        Parameters
        ----------
        self : SlotW63
            A SlotW63 object
        alpha : float
            float number for rotation (Default value = 0) [rad]
        delta : complex
            complex number for translation (Default value = 0)

        Returns
        -------
        surf_list : list
            list of surfaces objects
        """

        # Create curve list
        line_dict = self._comp_line_dict()
        if self.W2 != 0:
            if self.H2 != 0:
                curve_list = [
                    line_dict["1-2"],
                    line_dict["2-w1"],
                    line_dict["w1-w2"],
                    line_dict["w2-w2s"],
                    line_dict["w2s-w1s"],
                    line_dict["w1s-7"],
                    line_dict["7-8"],
                    line_dict["8-1"],
                ]

            else:
                curve_list = [
                    line_dict["2-w1"],
                    line_dict["w1-w2"],
                    line_dict["w2-w2s"],
                    line_dict["w2s-w1s"],
                    line_dict["w1s-7"],
                    line_dict["7-2"],
                ]
        else:
            if self.H2 != 0:
                curve_list = [
                    line_dict["1-2"],
                    line_dict["2-7"],
                    line_dict["7-8"],
                    line_dict["8-1"],
                ]

            else:
                curve_list = [
                    line_dict["2-7"],
                    line_dict["7w-2w"],
                ]

        curve_list = [line for line in curve_list if line is not None]

        # Only the closing arc (10-1) needs to be drawn (in FEMM)
        for curve in curve_list[:-1]:
            if curve.prop_dict is None:
                curve.prop_dict = dict()
            curve.prop_dict.update({DRAW_PROP_LAB: False})

        # Create surface
        point_dict = self._comp_point_coordinate()
        Z2 = point_dict["Z2"]
        Z8 = point_dict["Z8"]

        Zmid = (Z8 + Z2) / 2
        label = f"{self.parent.get_label()}_{SOP_LAB}_R0-T0-S0"
        surface = SurfLine(line_list=curve_list, label=label, point_ref=Zmid)

        # Apply transformation
        if alpha != 0:
            surface.rotate(alpha)
        if delta != 0:
            surface.translate(delta)

        return [surface]

    # cf Methods.Slot.SlotW63.plot_schematics
    plot_schematics = plot_schematics
    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        W0=0.314,
        W1=0.02,
        H0=0.003,
        H1=0.05,
        H2=0.0,
        W2=0.0,
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
            if "W1" in list(init_dict.keys()):
                W1 = init_dict["W1"]
            if "H0" in list(init_dict.keys()):
                H0 = init_dict["H0"]
            if "H1" in list(init_dict.keys()):
                H1 = init_dict["H1"]
            if "H2" in list(init_dict.keys()):
                H2 = init_dict["H2"]
            if "W2" in list(init_dict.keys()):
                W2 = init_dict["W2"]
            if "Zs" in list(init_dict.keys()):
                Zs = init_dict["Zs"]
            if "wedge_mat" in list(init_dict.keys()):
                wedge_mat = init_dict["wedge_mat"]
            if "is_bore" in list(init_dict.keys()):
                is_bore = init_dict["is_bore"]
        # Set the properties (value check and convertion are done in setter)
        self.W0 = W0
        self.W1 = W1
        self.H0 = H0
        self.H1 = H1
        self.H2 = H2
        self.W2 = W2
        # Call Slot init
        super(SlotW63, self).__init__(Zs=Zs, wedge_mat=wedge_mat, is_bore=is_bore)
        # The class is frozen (in Slot init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        SlotW63_str = ""
        # Get the properties inherited from Slot
        SlotW63_str += super(SlotW63, self).__str__()
        SlotW63_str += "W0 = " + str(self.W0) + linesep
        SlotW63_str += "W1 = " + str(self.W1) + linesep
        SlotW63_str += "H0 = " + str(self.H0) + linesep
        SlotW63_str += "H1 = " + str(self.H1) + linesep
        SlotW63_str += "H2 = " + str(self.H2) + linesep
        SlotW63_str += "W2 = " + str(self.W2) + linesep
        return SlotW63_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from Slot
        if not super(SlotW63, self).__eq__(other):
            return False
        if other.W0 != self.W0:
            return False
        if other.W1 != self.W1:
            return False
        if other.H0 != self.H0:
            return False
        if other.H1 != self.H1:
            return False
        if other.H2 != self.H2:
            return False
        if other.W2 != self.W2:
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
            super(SlotW63, self).compare(
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
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from Slot
        S += super(SlotW63, self).__sizeof__()
        S += getsizeof(self.W0)
        S += getsizeof(self.W1)
        S += getsizeof(self.H0)
        S += getsizeof(self.H1)
        S += getsizeof(self.H2)
        S += getsizeof(self.W2)
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
        SlotW63_dict = super(SlotW63, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs,
        )
        SlotW63_dict["W0"] = self.W0
        SlotW63_dict["W1"] = self.W1
        SlotW63_dict["H0"] = self.H0
        SlotW63_dict["H1"] = self.H1
        SlotW63_dict["H2"] = self.H2
        SlotW63_dict["W2"] = self.W2
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        SlotW63_dict["__class__"] = "SlotW63"
        return SlotW63_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        W0_val = self.W0
        W1_val = self.W1
        H0_val = self.H0
        H1_val = self.H1
        H2_val = self.H2
        W2_val = self.W2
        Zs_val = self.Zs
        if self.wedge_mat is None:
            wedge_mat_val = None
        else:
            wedge_mat_val = self.wedge_mat.copy()
        is_bore_val = self.is_bore
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(
            W0=W0_val,
            W1=W1_val,
            H0=H0_val,
            H1=H1_val,
            H2=H2_val,
            W2=W2_val,
            Zs=Zs_val,
            wedge_mat=wedge_mat_val,
            is_bore=is_bore_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.W0 = None
        self.W1 = None
        self.H0 = None
        self.H1 = None
        self.H2 = None
        self.W2 = None
        # Set to None the properties inherited from Slot
        super(SlotW63, self)._set_None()

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
        doc="""Pole bottom width

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
        doc="""Pole top width

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
        doc="""Pole bottom height

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
        doc="""Pole top height

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
        doc="""Heigh Ploe

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
        doc="""Width Ploe

        :Type: float
        :min: 0
        """,
    )
