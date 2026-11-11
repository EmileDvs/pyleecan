# Experimental dataclass generated from Generator/ClassesRef/Slot/SlotW11_2.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass
from typing import ClassVar

import matplotlib.pyplot as plt
import numpy as np

from ..definitions import config_dict
from ..Functions_new.Geometry.inter_line_circle import inter_line_circle
from ..Functions_new.Geometry.inter_line_line import inter_line_line
from ..Functions_new.labels import DRAW_PROP_LAB, SOP_LAB, WIND_LAB
from ..Functions_new.Plot import (
    ARROW_COLOR,
    ARROW_WIDTH,
    MAIN_LINE_COLOR,
    MAIN_LINE_STYLE,
    MAIN_LINE_WIDTH,
    P_FONT_SIZE,
    SC_FONT_SIZE,
    TEXT_BOX,
    plot_quote,
)
from ._check import check_var
from ._error import ParentMissingError, SlotCheckError
from .arc_1 import Arc1
from .arc_3 import Arc3
from .lam_slot import LamSlot
from .segment import Segment
from .slot import Slot
from .surf_line import SurfLine


@dataclass(eq=False)
class SlotW11_2(Slot):
    """SlotW11_2

    Attributes
    ----------
    W0 : float or None
        Slot isthmus width.
        Unit: m; Default: None; Minimum: 0
    H0 : float or None
        Slot isthmus height.
        Unit: m; Default: None; Minimum: 0
    H1 : float or None
        height or angle  (See Schematics)
        Unit: m/rad; Default: None; Minimum: 0
    H1_is_rad : bool
        H1 unit, False for m, True for rad
        Default: False
    W1 : float or None
        Slot top width.
        Unit: m; Default: None; Minimum: 0
    H2 : float or None
        Slot height below wedge
        Unit: m; Default: None; Minimum: 0
    W2 : float or None
        Slot bottom width.
        Unit: m; Default: None; Minimum: 0
    is_cstt_tooth : bool
        True: use W3 to define the slot, False: use W2 and W1
        Default: False
    W3 : float or None
        Tooth width
        Unit: m; Default: None; Minimum: 0
    R1 : float or None
        Slot bottom radius
        Unit: m; Default: None; Minimum: 0
    """

    IS_SYMMETRICAL: ClassVar = 1
    MAGNET_COLOR = config_dict["PLOT"]["COLOR_DICT"]["MAGNET_COLOR"]
    W0: float | None = None
    """Slot isthmus width."""
    H0: float | None = None
    """Slot isthmus height."""
    H1: float | None = None
    """height or angle  (See Schematics)"""
    H1_is_rad: bool = False
    """H1 unit, False for m, True for rad"""
    W1: float | None = None
    """Slot top width."""
    H2: float | None = None
    """Slot height below wedge """
    W2: float | None = None
    """Slot bottom width."""
    is_cstt_tooth: bool = False
    """True: use W3 to define the slot, False: use W2 and W1"""
    W3: float | None = None
    """Tooth width"""
    R1: float | None = None
    """Slot bottom radius"""

    # Inlined from Methods.Slot.SlotW11_2._comp_line_dict
    def _comp_line_dict(self):
        """Define a dictionnary of the lines to draw the slot
        If a line has begin==end, it is replaced by "None" (dict has always the same number of keys)

        Parameters
        ----------
        self : SlotW11_2
            A SlotW11_2 object

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

        if self.is_outwards():
            rot_sign = 1  # Rotation direction for Arc1
        else:  # inward slot
            rot_sign = -1  # Rotation direction for Arc1

        # Creation of curve
        line_dict = {}
        if self.H0 > 0:
            line_dict["1-2"] = Segment(Z1, Z2)
        else:
            line_dict["1-2"] = None

        H1 = self.get_H1()
        if H1 == 0 and self.W1 == self.W0:
            line_dict["2-3"] = None
        else:
            line_dict["2-3"] = Segment(Z2, Z3)
        line_dict["3-4"] = Segment(Z3, Z4)

        if self.R1 * 2 < self.W2:
            line_dict["4-5"] = Arc1(
                Z4, Z5, rot_sign * self.R1, is_trigo_direction=self.is_outwards()
            )
            line_dict["5-6"] = Segment(Z5, Z6)
            line_dict["6-7"] = Arc1(
                Z6, Z7, rot_sign * self.R1, is_trigo_direction=self.is_outwards()
            )
        else:
            line_dict["4-5"] = None
            line_dict["5-6"] = Arc3(Z4, Z7, self.is_outwards())
            line_dict["6-7"] = None

        line_dict["7-8"] = Segment(Z7, Z8)
        if H1 == 0 and self.W1 == self.W0:
            line_dict["8-9"] = None
        else:
            line_dict["8-9"] = Segment(Z8, Z9)

        if self.H0 > 0:
            line_dict["9-10"] = Segment(Z9, Z10)
        else:
            line_dict["9-10"] = None

        # Closing Arc
        line_dict["10-1"] = Arc1(Z10, Z1, -self.get_Rbo(), is_trigo_direction=False)

        # Closing Active part
        line_dict["3-8"] = Segment(Z3, Z8)
        line_dict["8-3"] = Segment(Z8, Z3)
        line_dict["9-2"] = Segment(Z9, Z2)

        return line_dict

    # Inlined from Methods.Slot.SlotW11_2._comp_point_coordinate
    def _comp_point_coordinate(self):
        """Compute the point coordinates needed to plot the Slot.

        Parameters
        ----------
        self : SlotW11_2
            A SlotW11_2 object

        Returns
        -------
        point_dict: dict
            A dict of the slot coordinates
        """

        if self.is_cstt_tooth and (self.W1 is None or self.W2 is None):
            # Compute W1 and W2 to match W3 tooth constraint
            self._comp_W()

        Rbo = self.get_Rbo()

        H1 = self.get_H1()

        # alpha is the angle to rotate Z0 so ||Z1,Z8|| = W0
        alpha = float(np.arcsin(self.W0 / (2 * Rbo)))

        # comp point coordinate (in complex)
        Z0 = Rbo * np.exp(1j * 0)
        Z1 = Z0 * np.exp(-1j * alpha)

        if self.is_outwards():
            Z2 = Z1 + self.H0
            Z3 = Z2.real + H1 + -1j * self.W1 / 2.0
            Z4 = Z3.real + (self.H2 - self.R1) - 1j * self.W2 / 2.0
            Z5 = Z4 + self.R1 + self.R1 * 1j
            Zc1 = Z4 + 1j * self.R1
            Z4c = Z4

        else:  # inward slot
            Z2 = Z1 - self.H0
            Z3 = Z2.real - H1 + -1j * self.W1 / 2.0
            Z4 = Z3.real - (self.H2 - self.R1) - 1j * self.W2 / 2.0
            Z4c = Z4

            c = (Z4.imag - Z3.imag) / (Z4.real - Z3.real)
            b = Z4.imag - c * Z4.real

            # straight equation
            y = c * 0.5 + b
            Zl2 = y * 1j + 0.5

            Zct1 = Z1 - self.H2 - H1 - self.H0 + self.R1 - 1j
            Zct2 = Zct1 + 2j

            Zi = inter_line_line(Z3, Zl2, Zct1, Zct2)
            Zc1 = Zi[0] + self.R1 * 1j

            if abs(2 * self.R1 - self.W2) < 1e-6:
                Zc1 = Z4c + self.R1 * 1j
                Z5 = Zc1 - self.R1

            else:
                Z4 = inter_line_circle(Z3, Zl2, self.R1, Zc1)
                Z4 = Z4[0]

                Zct1 = Z1 - self.H2 - H1 - self.H0 - 1j
                Zct2 = Zct1 + 2j

                Z5 = inter_line_circle(Zct1, Zct2, self.R1, Zc1)

                if len(Z5) == 0:
                    Z5 = inter_line_circle(Zct1, Zct2, self.R1, Zc1 - 0.0000001)
                Z5 = Z5[0]

        point_dict = {}
        # symetry
        point_dict["Z1"] = Z1
        point_dict["Z2"] = Z2
        point_dict["Z3"] = Z3
        point_dict["Z4"] = Z4
        point_dict["Z4c"] = Z4c
        point_dict["Z5"] = Z5
        point_dict["Z6"] = Z5.conjugate()
        point_dict["Z7"] = Z4.conjugate()
        point_dict["Z7c"] = Z4c.conjugate()
        point_dict["Z8"] = Z3.conjugate()
        point_dict["Z9"] = Z2.conjugate()
        point_dict["Z10"] = Z1.conjugate()

        point_dict["Zc1"] = Zc1
        point_dict["Zc2"] = Zc1.conjugate()

        return point_dict

    # Inlined from Methods.Slot.SlotW11_2._comp_W
    def _comp_W(self):
        """Compute W1 and W2 method (cste tooth compatibility)

        Parameters
        ----------
        self : SlotW11_2
            A SlotW11_2 object

        Returns
        -------
        None

        """
        Rbo = self.get_Rbo()

        # alpha is the angle to rotate Z0 so ||Z1,Z10|| = W0
        alpha = float(np.abs(self.W0 / (2 * Rbo)))

        # comp point coordinate (in complex)
        Z0 = Rbo * np.exp(1j * 0)
        Z1 = Z0 * np.exp(-1j * alpha)

        Harc = Rbo - abs(Z1.real)

        # To compute the slot width we use the fact that
        # alpha_tooth + alpha_slot = slot_pitch
        slot_pitch = 2 * np.pi / self.Zs

        # H0 and H1 are radial
        if self.is_outwards():
            radius = Rbo + self.get_H1() + self.H0
        else:
            radius = Rbo - self.get_H1() - self.H0

        alpha_T1 = float(np.abs(self.W3 / (2 * radius)))
        alpha_S1 = slot_pitch - 2 * alpha_T1
        self.W1 = 2 * np.tan(alpha_S1 / 2) * radius

        # define W2
        if self.is_outwards():
            self.W2 = (
                2
                * np.tan(slot_pitch / 2)
                * (
                    Rbo
                    - Harc
                    + self.H0
                    + self.get_H1()
                    + self.H2
                    - self.R1
                    - self.W3 / (2 * np.tan(slot_pitch / 2) * np.cos(slot_pitch / 2))
                )
            )

        else:
            self.W2 = (
                2
                * np.tan(slot_pitch / 2)
                * (
                    Rbo
                    - Harc
                    - self.H0
                    - self.get_H1()
                    - self.H2
                    + self.R1
                    - self.W3 / (2 * np.tan(slot_pitch / 2) * np.cos(slot_pitch / 2))
                )
            )

    # Inlined from Methods.Slot.SlotW11_2._set_W3
    def _set_W3(self, value):
        """setter of W3

        Parameters
        ----------
        self : SlotW11_2
            A SlotW11_2 object
        value : float
            value of W3
        """

        check_var("W3", value, "float", Vmin=0)
        self._W3 = value

        # Compute W1 and W2 to match W3 tooth constraint
        try:
            self._comp_W()
        except Exception:
            pass

    # Inlined from Methods.Slot.SlotW11_2.build_geometry
    def build_geometry(self):
        """Compute the curve (Line) needed to plot the object.
        The ending point of a curve is the starting point of the next curve
        in the list

        Parameters
        ----------
        self : SlotW11_2
            A SlotW11_2 object

        Returns
        -------
        curve_list: list
            A list of 7 Segment and 2 Arc1

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

    # Inlined from Methods.Slot.SlotW11_2.check
    def check(self):
        """Check that the SlotW11_2 object is correct

        Parameters
        ----------
        self : SlotW11_2
            A SlotW11_2 object

        Returns
        -------
        None

        Raises
        -------
        S11_W01CheckError
            You must have W0 <= W1
        S11_RWCheckError
            You must have 2*R1 <= W2
        S11_RHCheckError
            You must have R1 <= H2
        S11_H1rCheckError
            With H1 in radian, you must have H1 < pi/2"""

        if self.W0 is None:
            return "You must set W0 !"
        if self.W1 is None and not self.is_cstt_tooth:
            return "You must set W1 !"
        if self.W2 is None and not self.is_cstt_tooth:
            return "You must set W2 !"
        elif self.H0 is None:
            return "You must set H0 !"
        elif self.H1 is None:
            return "You must set H1 !"
        elif self.H2 is None:
            return "You must set H2 !"
        elif self.R1 is None:
            return "You must set R1 !"
        elif self.is_cstt_tooth and self.W3 is None:
            return "In constant tooth mode, you must set W3 !"

        if self.R1 <= 0:
            raise self.S11_2_R1CheckError("You must have R1 > 0")

        if self.H1_is_rad and self.H1 >= np.pi / 2:
            raise self.S11_2_H1rCheckError("With H1 in radian, you must have H1 < pi/2")
            # return "With H1 in radian, you must have H1 < pi/2"

        if self.W1 is None or self.W0 is None:
            pass
        else:
            if self.W1 < self.W0:
                raise self.S11_2_W01CheckError("You must have W0 <= W1")

        if not self.W1 is None or not self.W2 is None:
            if 2 * self.R1 >= self.W2 and (not self.W2 is None or not self.R1 is None):
                raise self.S11_2_RWCheckError("You must have 2*R1 <= W2")

        if self.R1 > self.H2:
            raise self.S11_2_RHCheckError("You must have R1 <= H2")

        if self.H1_is_rad and self.H1 >= np.pi / 2:
            raise self.S11_2_H1rCheckError("With H1 in radian, you must have H1 < pi/2")

    # Inlined from Methods.Slot.SlotW11_2.comp_angle_opening
    def comp_angle_opening(self):
        """Compute the average opening angle of the Slot

        Parameters
        ----------
        self : SlotW11_2
            A SlotW11_2 object

        Returns
        -------
        alpha: float
            Average opening angle of the slot [rad]

        """

        Rbo = self.get_Rbo()

        return float(2 * np.arcsin(self.W0 / (2 * Rbo)))

    # Inlined from Methods.Slot.SlotW11_2.comp_height
    def comp_height(self):
        """Compute the height of the Slot.
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotW11_2
            A SlotW11_2 object

        Returns
        -------
        Htot: float
            Height of the slot [m]

        """
        if self.is_cstt_tooth and (self.W1 is None or self.W2 is None):
            # Compute W1 and W2 to match W3 tooth constraint
            self._comp_W()

        Rbo = self.get_Rbo()

        if self.is_outwards():
            if self.R1 * 2 == self.W2:
                # Computation of the arc height
                alpha = self.comp_angle_opening() / 2
                Harc = float(Rbo * (1 - np.cos(alpha)))
                return self.H0 + self.get_H1() + self.H2 - Harc

            else:
                line_dict = self._comp_line_dict()
                Arc = line_dict["6-7"]
                Ndisc = 200
                point_list = Arc.discretize(Ndisc)
                point_list = np.array(point_list)
                return max(abs(point_list)) - Rbo

        else:
            # Computation of the arc height
            alpha = self.comp_angle_opening() / 2
            Harc = float(Rbo * (1 - np.cos(alpha)))

            return self.H0 + self.get_H1() + self.H2 + Harc

    # Inlined from Methods.Slot.SlotW11_2.comp_height_active
    def comp_height_active(self):
        """Compute the height of the winding area

        Parameters
        ----------
        self : SlotW11_2
            A SlotW11_2 object

        Returns
        -------
        Hwind: float
            Height of the winding area [m]

        """

        return self.H2

    # Inlined from Methods.Slot.SlotW11_2.comp_surface
    def comp_surface(self):
        """Compute the Slot total surface (by analytical computation for comp_surface_opening and numerical computation for comp_surface_active).
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotW11_2
            A SlotW11_2 object

        Returns
        -------
        S: float
            Slot total surface [m**2]

        """
        return self.comp_surface_active() + self.comp_surface_opening()

    # Inlined from Methods.Slot.SlotW11_2.comp_surface_opening
    def comp_surface_opening(self):
        """Compute the Slot opening surface (by analytical computation).
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotW11_2
            A SlotW11_2 object

        Returns
        -------
        S: float
            Slot opening surface [m**2]

        """
        if self.is_cstt_tooth and (self.W1 is None or self.W2 is None):
            # Compute W1 and W2 to match W3 tooth constraint
            self._comp_W()

        Rbo = self.get_Rbo()

        S1 = self.H0 * self.W0
        H1 = self.get_H1()

        S2 = 0.5 * (self.W0 + self.W1) * H1

        # The bottom is an arc
        alpha = self.comp_angle_opening()
        Sarc = (Rbo**2.0) / 2.0 * (alpha - np.sin(alpha))

        # Because Slamination = S - Zs * Sslot
        if self.is_outwards():
            return S1 + S2 - Sarc
        else:
            return S1 + S2 + Sarc

    # Inlined from Methods.Slot.SlotW11_2.get_H1
    def get_H1(self):
        """Return H1 in [m]

        Parameters
        ----------
        self : SlotW11_2
            A SlotW11_2 object

        Returns
        -------
        H1: float
            H1 in [m]

        """

        Rbo = self.get_Rbo()

        # alpha is the angle to rotate Z0 so ||Z1,Z8|| = W0
        alpha = float(np.arcsin(self.W0 / (2 * Rbo)))

        if self.is_outwards():
            Z2 = (Rbo + self.H0) * np.exp(-1j * alpha)

        else:  # inward slot
            Z2 = (Rbo - self.H0) * np.exp(-1j * alpha)

        if self.H1_is_rad:  # H1 in rad
            if self.is_cstt_tooth:
                Z2t = Z2 * np.exp(1j * np.pi / self.Zs)
                Zangle = np.exp(-1j * ((np.pi / 2) - self.H1)) + Z2t

                Zt1 = 1j * (self.W3 / 2)
                Zt2 = 1 + (1j * self.W3) / 2
                L = inter_line_line(Zt1, Zt2, Z2t, Zangle)
                Z3 = L[0]
                return abs(Z3.real - Z2.real)

            else:
                return (self.W1 - self.W0) * np.tan(self.H1) / 2.0  # convertion to m

        else:  # H1 in m
            return self.H1

    # Inlined from Methods.Slot.SlotW11_2.get_surface_active
    def get_surface_active(self, alpha=0, delta=0):
        """Return the full winding surface

        Parameters
        ----------
        self : SlotW11_2
            A SlotW11_2 object
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
                line_dict["6-7"],
                line_dict["7-8"],
                line_dict["8-3"],
            ]
        else:
            # Add 2-3 and 9-3 to make sure that FEMM handles all the lines
            # cf (Tests\Validation\Magnetics\test_FEMM_fast_draw.py)
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

        # Only the closing arc (8-3) needs to be drawn (in FEMM)
        for curve in curve_list[:-1]:
            if curve.prop_dict is None:
                curve.prop_dict = {}
            curve.prop_dict.update({DRAW_PROP_LAB: False})

        # Create surface
        H1 = self.get_H1()
        if self.is_outwards():
            Zmid = self.get_Rbo() + self.H0 + H1 + self.H2 / 2
        else:
            Zmid = self.get_Rbo() - self.H0 - H1 - self.H2 / 2
        label = self.parent.get_label() + "_" + WIND_LAB + "_R0-T0-S0"
        surface = SurfLine(line_list=curve_list, label=label, point_ref=Zmid)

        # Apply transformation
        surface.rotate(alpha)
        surface.translate(delta)

        return surface

    # Inlined from Methods.Slot.SlotW11_2.get_surface_opening
    def get_surface_opening(self, alpha=0, delta=0):
        """Return the list of surfaces defining the opening area of the Slot

        Parameters
        ----------
        self : SlotW11_2
            A SlotW11_2 object
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
        H1 = self.get_H1()
        if self.H0 == 0 and H1 == 0:
            return []

        # Create curve list
        line_dict = self._comp_line_dict()
        curve_list = [
            line_dict["1-2"],
            line_dict["2-3"],
            line_dict["3-8"],
            line_dict["8-9"],
            line_dict["9-10"],
            line_dict["10-1"],
        ]
        curve_list = [line for line in curve_list if line is not None]

        # Only the closing arc (10-1) needs to be drawn (in FEMM)
        for curve in curve_list[:-1]:
            if curve.prop_dict is None:
                curve.prop_dict = {}
            curve.prop_dict.update({DRAW_PROP_LAB: False})

        # Create surface
        if self.is_outwards():
            Zmid = self.get_Rbo() + (self.H0 + H1) / 2
        else:
            Zmid = self.get_Rbo() - (self.H0 + H1) / 2
        label = self.parent.get_label() + "_" + SOP_LAB + "_R0-T0-S0"
        surface = SurfLine(line_list=curve_list, label=label, point_ref=Zmid)

        # Apply transformation
        surface.rotate(alpha)
        surface.translate(delta)

        return [surface]

    # Inlined from Methods.Slot.SlotW11_2.plot_schematics
    def plot_schematics(
        self,
        is_default=False,
        is_return_default=False,
        is_add_point_label=False,
        is_add_schematics=True,
        is_add_main_line=True,
        type_add_active=1,
        save_path=None,
        is_show_fig=True,
        fig=None,
        ax=None,
    ):
        """Plot the schematics of the slot

        Parameters
        ----------
        self : SlotW11_2
            A SlotW11_2 object
        is_default : bool
            True: plot default schematics, else use current slot values
        is_return_default : bool
            True: return the default lamination used for the schematics (skip plot)
        is_add_point_label : bool
            True to display the name of the points (Z1, Z2....)
        is_add_schematics : bool
            True to display the schematics information (W0, H0...)
        is_add_main_line : bool
            True to display "main lines" (slot opening and 0x axis)
        type_add_active : int
            0: No active surface, 1: active surface as winding, 2: active surface as magnet, 3: active surface as winding + wedges    save_path : str
            full path including folder, name and extension of the file to save if save_path is not None
        is_show_fig : bool
            To call show at the end of the method
        fig : Matplotlib.figure.Figure
            existing figure to use if None create a new one
        ax : Matplotlib.axes.Axes object
            Axis on which to plot the data

        Returns
        -------
        fig : Matplotlib.figure.Figure
            Figure containing the schematics
        ax : Matplotlib.axes.Axes object
            Axis containing the schematics
        -------
        lam : LamSlot
            Default lamination used for the schematics
        """

        # Use some default parameter
        if is_default:
            slot = type(self)(
                Zs=8,
                H0=10e-3,
                W0=20e-3,
                H1=10e-3,
                H2=40e-3,
                W1=40e-3,
                W2=20e-3,
                R1=5e-3,
            )
            lam = LamSlot(
                Rint=0.135, Rext=0.3, is_internal=True, is_stator=False, slot=slot
            )
            if is_return_default:
                return lam
            else:
                return slot.plot_schematics(
                    is_default=False,
                    is_return_default=False,
                    is_add_point_label=is_add_point_label,
                    is_add_schematics=is_add_schematics,
                    is_add_main_line=is_add_main_line,
                    type_add_active=type_add_active,
                    save_path=save_path,
                    is_show_fig=is_show_fig,
                    fig=fig,
                    ax=ax,
                )
        else:
            # Getting the main plot
            if self.parent is None:
                raise ParentMissingError("Error: The slot is not inside a Lamination")
            lam = self.parent
            fig, ax = lam.plot(
                alpha=np.pi / self.Zs, is_show_fig=False, fig=fig, ax=ax
            )  # center slot on Ox axis
            point_dict = self._comp_point_coordinate()
            if self.is_outwards():
                sign = 1
            else:
                sign = -1
            # Adding point label
            if is_add_point_label:
                for name, Z in point_dict.items():
                    ax.text(
                        Z.real,
                        Z.imag,
                        name,
                        fontsize=P_FONT_SIZE,
                        bbox=TEXT_BOX,
                    )

            # Adding schematics
            if is_add_schematics:
                # W0
                line = Segment(point_dict["Z1"], point_dict["Z10"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="W0",
                    offset_label=self.H0 * 0.15 + 1j * self.W0 * 0.1,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # W1
                line = Segment(point_dict["Z3"], point_dict["Z8"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="W1",
                    offset_label=self.H0 * 0.15 + 1j * self.W1 * 0.3,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # W2
                Zlim1 = (
                    point_dict["Z5"].real + sign * self.R1 + 1j * point_dict["Z4c"].imag
                )
                Zlim2 = (
                    point_dict["Z6"].real + sign * self.R1 + 1j * point_dict["Z7c"].imag
                )
                plot_quote(
                    point_dict["Z4c"],
                    Zlim1,
                    Zlim2,
                    point_dict["Z7c"],
                    offset_label=sign * 0.05 * self.H2,
                    fig=fig,
                    ax=ax,
                    label="W2",
                )
                # H0
                line = Segment(point_dict["Z10"], point_dict["Z9"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    label="H0",
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    offset_label=1j * self.W0 * 0.15,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # H1 [m]
                line = Segment(point_dict["Z2"].real, point_dict["Z3"].real)
                line.plot(
                    fig=fig,
                    ax=ax,
                    label="H1 [m]",
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    offset_label=1j * self.W0 * 0.15 - self.get_H1() / 2,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # H1 [rad]
                line = Arc1(
                    begin=(point_dict["Z2"] + point_dict["Z3"]) / 2
                    - self.get_H1() / 2
                    - 0.007j,
                    end=(((point_dict["Z2"] + point_dict["Z3"]) / 2) + point_dict["Z3"])
                    / 2,
                    radius=(self.get_H1() / 2),
                    is_trigo_direction=True,
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="H1 [rad]",
                    offset_label=-1j * sign * self.get_H1() * 0.5,
                    fontsize=SC_FONT_SIZE,
                )
                # H2
                line = Segment(point_dict["Z3"].real, point_dict["Z5"].real)
                line.plot(
                    fig=fig,
                    ax=ax,
                    label="H2",
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    offset_label=1j * self.W0 * 0.15,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # R1
                line = Segment(point_dict["Zc1"], point_dict["Z5"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    label="R1",
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    offset_label=1j * self.W0 * 0.15,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )

            if is_add_main_line:
                # Ox axis
                line = Segment(0, lam.Rext * 1.5)
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # Top arc
                line = Arc1(
                    begin=point_dict["Z1"],
                    end=point_dict["Z10"],
                    radius=self.get_Rbo(),
                    is_trigo_direction=True,
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # H1 line
                line = Segment(point_dict["Z2"], point_dict["Z9"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # R1 circle
                line = Segment(point_dict["Zc1"], point_dict["Z5"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                line = Segment(point_dict["Zc1"], point_dict["Z4"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                line = Segment(point_dict["Zc2"], point_dict["Z6"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                line = Segment(point_dict["Zc2"], point_dict["Z7"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )

            if type_add_active in [1, 3]:  # Wind and Wedge
                is_add_wedge = type_add_active == 3
                self.plot_active(
                    fig=fig, ax=ax, is_show_fig=False, is_add_wedge=is_add_wedge
                )
            elif type_add_active == 2:  # Magnet
                self.plot_active(
                    fig=fig,
                    ax=ax,
                    is_show_fig=False,
                    enforced_default_color=self.MAGNET_COLOR,
                )

            # Zooming and cleaning
            W = max([self.W1, self.W0, self.W2]) * 0.6
            Rint = min(point_dict["Z6"].real, point_dict["Z1"].real)
            Rext = max(point_dict["Z6"].real, point_dict["Z1"].real)

            ax.axis("equal")
            ax.set_xlim(Rint, Rext)
            ax.set_ylim(-W, W)
            manager = plt.get_current_fig_manager()
            if manager is not None:
                manager.set_window_title(type(self).__name__ + " Schematics")
            ax.set_title("")
            ax.get_legend().remove()
            ax.set_axis_off()
            fig.tight_layout()

            # Save / Show
            if save_path is not None:
                fig.savefig(save_path)
                plt.close(fig=fig)

            if is_show_fig:
                fig.show()
            return fig, ax

    # Inlined from Methods.Slot.SlotW11_2.plot_schematics_constant_tooth
    def plot_schematics_constant_tooth(
        self,
        is_default=False,
        is_return_default=False,
        is_add_point_label=False,
        is_add_schematics=True,
        is_add_main_line=True,
        type_add_active=1,
        save_path=None,
        is_show_fig=True,
        fig=None,
        ax=None,
    ):
        """Plot the schematics of the slot

        Parameters
        ----------
        self : SlotW11_2
            A SlotW11_2 object
        is_default : bool
            True: plot default schematics, else use current slot values
        is_return_default : bool
            True: return the default lamination used for the schematics (skip plot)
        is_add_point_label : bool
            True to display the name of the points (Z1, Z2....)
        is_add_schematics : bool
            True to display the schematics information (W0, H0...)
        is_add_main_line : bool
            True to display "main lines" (slot opening and 0x axis)
        type_add_active : int
            0: No active surface, 1: active surface as winding, 2: active surface as magnet, 3: active surface as winding + wedges    save_path : str
            full path including folder, name and extension of the file to save if save_path is not None
        is_show_fig : bool
            To call show at the end of the method
        fig : Matplotlib.figure.Figure
            existing figure to use if None create a new one
        ax : Matplotlib.axes.Axes object
            Axis on which to plot the data

        Returns
        -------
        fig : Matplotlib.figure.Figure
            Figure containing the schematics
        ax : Matplotlib.axes.Axes object
            Axis containing the schematics
        -------
        lam : LamSlot
            Default lamination used for the schematics
        """

        # Use some default parameter
        if is_default:
            slot = type(self)(
                Zs=12,
                H0=20e-3,
                W0=30e-3,
                H1=30e-3,
                H2=80e-3,
                W3=20e-3,
                is_cstt_tooth=True,
                R1=20e-3,
            )
            lam = LamSlot(
                Rint=0.135, Rext=0.3, is_internal=True, is_stator=False, slot=slot
            )
            if is_return_default:
                return lam
            else:
                return slot.plot_schematics_constant_tooth(
                    is_default=False,
                    is_return_default=False,
                    is_add_point_label=is_add_point_label,
                    is_add_schematics=is_add_schematics,
                    is_add_main_line=is_add_main_line,
                    type_add_active=type_add_active,
                    save_path=save_path,
                    is_show_fig=is_show_fig,
                    fig=fig,
                    ax=ax,
                )
        else:
            # Getting the main plot
            if self.parent is None:
                raise ParentMissingError("Error: The slot is not inside a Lamination")
            lam = self.parent
            fig, ax = lam.plot(
                alpha=np.pi / self.Zs, is_show_fig=False, fig=fig, ax=ax
            )  # center slot on Ox axis
            point_dict = self._comp_point_coordinate()
            if self.is_outwards():
                sign = 1
            else:
                sign = -1
            # Adding point label
            if is_add_point_label:
                for name, Z in point_dict.items():
                    ax.text(
                        Z.real,
                        Z.imag,
                        name,
                        fontsize=P_FONT_SIZE,
                        bbox=TEXT_BOX,
                    )
            sp = 2 * np.pi / self.Zs

            # Adding schematics
            if is_add_schematics:
                # W0
                line = Segment(point_dict["Z1"], point_dict["Z10"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="W0",
                    offset_label=self.H0 * 0.1 - 0.02,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # W3
                line = Segment(
                    (point_dict["Z3"] + point_dict["Z4"]) / 2,
                    (point_dict["Z7"] + point_dict["Z8"]) / 2 * np.exp(-1j * sp),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="W3",
                    offset_label=self.get_H1() * 0.2 - 0.001j,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # H0
                line = Segment(point_dict["Z10"], point_dict["Z9"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    label="H0",
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    offset_label=1j * self.W0 * 0.11 + 0.005j - 0.005,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # H1[m]
                line = Segment(point_dict["Z2"].real, point_dict["Z3"].real)
                line.plot(
                    fig=fig,
                    ax=ax,
                    label="H1[m]",
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    offset_label=1j * self.W0 * 0.25 - 0.01,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # H1 [rad]
                line = Arc1(
                    begin=(point_dict["Z2"] + point_dict["Z3"]) / 2
                    - self.get_H1() / 2
                    - 0.007j,
                    end=(((point_dict["Z2"] + point_dict["Z3"]) / 2) + point_dict["Z3"])
                    / 2,
                    radius=(self.get_H1() / 2),
                    is_trigo_direction=True,
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="H1 [rad]",
                    offset_label=-1j * sign * self.get_H1() * 0.5,
                    fontsize=SC_FONT_SIZE,
                )
                # H2
                line = Segment(point_dict["Z3"].real, point_dict["Z5"].real)
                line.plot(
                    fig=fig,
                    ax=ax,
                    label="H2",
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    offset_label=1j * self.W0 * 0.3,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # R1
                line = Segment(point_dict["Zc1"], point_dict["Z5"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    label="R1",
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    offset_label=1j * self.W0 * 0.3,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )

            if is_add_main_line:
                # Ox axis
                line = Segment(0, lam.Rext * 1.5)
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # Top arc
                line = Arc1(
                    begin=point_dict["Z1"],
                    end=point_dict["Z10"],
                    radius=self.get_Rbo(),
                    is_trigo_direction=True,
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # H1 line
                line = Segment(point_dict["Z2"], point_dict["Z9"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # R1 circle
                line = Segment(point_dict["Zc1"], point_dict["Z5"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                line = Segment(point_dict["Zc1"], point_dict["Z4"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                line = Segment(point_dict["Zc2"], point_dict["Z6"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                line = Segment(point_dict["Zc2"], point_dict["Z7"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # W3 parralel
                line = Segment(point_dict["Z3"] * np.exp(1j * sp), point_dict["Z8"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )

                line = Segment(point_dict["Z3"], point_dict["Z8"] * np.exp(-1j * sp))
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )

                # H0 lines
                line = Segment(0, point_dict["Z1"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                line = Segment(0, point_dict["Z10"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # H1
                line = Segment(point_dict["Z2"] - 1j, point_dict["Z9"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # axis between Slot
                line = Segment(0, lam.Rext * 1.5 * np.exp(-1j * sp / 2))
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )

                line = Segment(0, lam.Rext * 1.5 * np.exp(1j * sp / 2))
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )

            if type_add_active in [1, 3]:  # Wind and Wedge
                is_add_wedge = type_add_active == 3
                self.plot_active(
                    fig=fig, ax=ax, is_show_fig=False, is_add_wedge=is_add_wedge
                )
            elif type_add_active == 2:  # Magnet
                self.plot_active(
                    fig=fig,
                    ax=ax,
                    is_show_fig=False,
                    enforced_default_color=self.MAGNET_COLOR,
                )

            # Zooming and cleaning
            # W = max([self.W1, self.W0, self.W2]) * 0.6
            W = (point_dict["Z4"] * np.exp(1j * sp)).imag * 1.1
            Rint = min(point_dict["Z6"].real, point_dict["Z1"].real)
            Rext = max(point_dict["Z6"].real, point_dict["Z1"].real)

            ax.axis("equal")
            ax.set_xlim(Rint, Rext)
            ax.set_ylim(-W, W)
            manager = plt.get_current_fig_manager()
            if manager is not None:
                manager.set_window_title(type(self).__name__ + " Schematics")
            ax.set_title("")
            ax.get_legend().remove()
            ax.set_axis_off()
            fig.tight_layout()

            # Save / Show
            if save_path is not None:
                fig.savefig(save_path)
                plt.close(fig=fig)

            if is_show_fig:
                fig.show()
            return fig, ax

    class S11_2_H1rCheckError(SlotCheckError):
        """ """

    class S11_2_R1CheckError(SlotCheckError):
        """ """

    class S11_2_RHCheckError(SlotCheckError):
        """ """

    class S11_2_RWCheckError(SlotCheckError):
        """ """

    class S11_2_W01CheckError(SlotCheckError):
        """ """
