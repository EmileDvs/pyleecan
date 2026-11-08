# Experimental dataclass generated from Generator/ClassesRef/Slot/SlotW23.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass
from typing import ClassVar

import matplotlib.pyplot as plt
import numpy as np

from ..definitions import config_dict
from ..Functions.Geometry.inter_line_line import inter_line_line
from ..Functions.labels import DRAW_PROP_LAB, SOP_LAB, WIND_LAB
from ..Functions.Plot import (
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
from .lam_slot import LamSlot
from .segment import Segment
from .slot import Slot
from .surf_line import SurfLine


@dataclass(eq=False)
class SlotW23(Slot):
    """semi-closed trapezoidal without fillet without wedge (rounded bottom)

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
    W1 : float or None
        Slot top width.
        Unit: m; Default: None; Minimum: 0
    H2 : float or None
        Slot height below wedge
        Unit: m; Default: None; Minimum: 0
    W2 : float or None
        Slot bottom width.
        Unit: m; Default: None; Minimum: 0
    H1_is_rad : bool
        H1 unit, False for m, True for rad
        Default: False
    is_cstt_tooth : bool
        True: use W3 to define the slot, False: use W2 and W1
        Default: False
    W3 : float or None
        Tooth width
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
    W1: float | None = None
    """Slot top width."""
    H2: float | None = None
    """Slot height below wedge """
    W2: float | None = None
    """Slot bottom width."""
    H1_is_rad: bool = False
    """H1 unit, False for m, True for rad"""
    is_cstt_tooth: bool = False
    """True: use W3 to define the slot, False: use W2 and W1"""
    W3: float | None = None
    """Tooth width"""

    # Inlined from Methods.Slot.SlotW23._comp_line_dict
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
        line_dict = {}
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

    # Inlined from Methods.Slot.SlotW23._comp_point_coordinate
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
        alpha = float(np.arcsin(self.W0 / (2 * Rbo)))

        # comp point coordinate (in complex)
        Z0 = Rbo * np.exp(1j * 0)
        Z1 = Z0 * np.exp(-1j * alpha)

        if self.is_outwards():
            Z2 = (Rbo + self.H0) * np.exp(-1j * alpha)
            Z3 = Z2.real + self.get_H1() - 1j * self.W1 / 2

            H2 = np.sqrt(self.H2**2 - ((self.W2 - self.W1) / 2.0) ** 2)
            Z4 = Z3.real + H2 - 1j * self.W2 / 2
        else:  # inward slot
            Z2 = (Rbo - self.H0) * np.exp(-1j * alpha)
            Z3 = Z2.real - self.get_H1() - 1j * self.W1 / 2

            H2 = np.sqrt(self.H2**2 - ((self.W2 - self.W1) / 2.0) ** 2)
            Z4 = Z3.real - H2 - 1j * self.W2 / 2

        point_dict = {}
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

    # Inlined from Methods.Slot.SlotW23._comp_W
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
        slot_pitch = 2 * np.pi / self.Zs

        # H0 and H1 are radial
        if self.is_outwards():
            R1 = Rbo + self.get_H1() + self.H0
        else:
            R1 = Rbo - self.get_H1() - self.H0

        alpha_T1 = float(np.arcsin(self.W3 / (2 * R1)))
        alpha_S1 = slot_pitch - 2 * alpha_T1
        self.W1 = 2 * np.sin(alpha_S1 / 2) * R1

        # H2 is parallel to the tooth axis
        if self.is_outwards():
            R2 = np.abs(R1 * np.exp(1j * alpha_T1) + self.H2)
        else:
            R2 = np.abs(R1 * np.exp(1j * alpha_T1) - self.H2)

        alpha_T2 = float(np.arcsin(self.W3 / (2 * R2)))
        alpha_S2 = slot_pitch - 2 * alpha_T2
        self.W2 = 2 * np.sin(alpha_S2 / 2) * R2

    # Inlined from Methods.Slot.SlotW23._set_W3
    def _set_W3(self, value):
        """setter of W3"""
        check_var("W3", value, "float", Vmin=0)
        self._W3 = value

        # Compute W1 and W2 to match W3 tooth constraint
        try:
            self._comp_W()
        except Exception:
            pass

    # Inlined from Methods.Slot.SlotW23.build_geometry
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

    # Inlined from Methods.Slot.SlotW23.check
    def check(self):
        """Check that the SlotW23 object is correct

        Parameters
        ----------
        self : SlotW23
            A SlotW23 object

        Returns
        -------
        None

        Raises
        -------
        S23_W01CheckError
            You must have W0 <= W1
        S23_H1rCheckError
            With H1 in radian, you must have H1 < pi/2

        """

        if self.H1_is_rad and self.H1 >= np.pi / 2:
            raise self.S23_H1rCheckError("With H1 in radian, you must have H1 < pi/2")

        if self.W1 is not None and self.W1 < self.W0:
            raise self.S23_W01CheckError("You must have W0 <= W1")

    # Inlined from Methods.Slot.SlotW23.comp_angle_opening
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

        return float(2 * np.arcsin(self.W0 / (2 * Rbo)))

    # Inlined from Methods.Slot.SlotW23.comp_height
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

    # Inlined from Methods.Slot.SlotW23.comp_height_active
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

    # Inlined from Methods.Slot.SlotW23.comp_surface
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

    # Inlined from Methods.Slot.SlotW23.comp_surface_active
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
        H2 = np.sqrt(self.H2**2 - ((self.W2 - self.W1) / 2.0) ** 2)
        S2 = 0.5 * (self.W1 + self.W2) * H2

        if self.is_outwards():
            Rslot = Rbo + self.comp_height()  # External radius of the slot
            alpha = float(2 * np.arcsin(self.W2 / (2 * Rslot)))  # W2 in rad
            S3 = (Rslot**2.0) / 2.0 * (alpha - np.sin(alpha))
            return S2 + S3
        else:
            Rslot = Rbo - self.comp_height()  # External radius of the slot
            alpha = float(2 * np.arcsin(self.W2 / (2 * Rslot)))  # W2 in rad
            S3 = (Rslot**2.0) / 2.0 * (alpha - np.sin(alpha))
            return S2 - S3

    # Inlined from Methods.Slot.SlotW23.comp_surface_opening
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
            Wint = 2 * np.sin(alpha / 2) * (Rbo + self.H0)
            # Arc between opening H0 and wedge H1
            Sarc = ((Rbo + self.H0) ** 2.0) / 2.0 * (alpha - np.sin(alpha))
            # The opening part is radial
            S1 = (np.pi * ((Rbo + self.H0) ** 2) - np.pi * (Rbo**2)) * alpha / (
                2 * np.pi
            ) - Sarc
        else:
            Wint = 2 * np.sin(alpha / 2) * (Rbo - self.H0)
            # Arc between opening H0 and wedge H1
            Sarc = ((Rbo - self.H0) ** 2.0) / 2.0 * (alpha - np.sin(alpha))
            # The opening part is radial
            S1 = (np.pi * (Rbo**2) - np.pi * ((Rbo - self.H0) ** 2)) * alpha / (
                2 * np.pi
            ) + Sarc

        S2 = 0.5 * self.get_H1() * (Wint + self.W1)

        return S1 + S2

    # Inlined from Methods.Slot.SlotW23.get_H1
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

    # Inlined from Methods.Slot.SlotW23.get_surface_active
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
                curve.prop_dict = {}
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

    # Inlined from Methods.Slot.SlotW23.get_surface_opening
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
                curve.prop_dict = {}
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

    # Inlined from Methods.Slot.SlotW23.plot_schematics
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
        self : SlotW23
            A SlotW23 object
        is_default : bool
            True: plot default schematics, else use current slot values
        is_return_default : bool
            True: return the default lamination used for the schematics (skip plot
        is_add_point_label : bool
            True to display the name of the points (Z1, Z2....)
        is_add_schematics : bool
            True to display the schematics information (W0, H0...)
        is_add_main_line : bool
            True to display "main lines" (slot opening and 0x axis)
        type_add_active : int
            0: No active surface, 1: active surface as winding, 2: active surface as magnet, 3: active surface as winding + wedges
        save_path : str
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
                Zs=8, H0=10e-3, W0=20e-3, H1=10e-3, H2=50e-3, W1=40e-3, W2=30e-3
            )
            lam = LamSlot(
                Rint=0.135, Rext=0.3, is_internal=False, is_stator=True, slot=slot
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
                line = Segment(point_dict["Z1"], point_dict["Z8"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="W0",
                    offset_label=self.H0 * 0.2,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # W1
                line = Segment(point_dict["Z3"], point_dict["Z6"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    label="W1",
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    offset_label=self.get_H1() * 0.2,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # W2
                Zlim1 = point_dict["Z4"] + sign * 0.1 * self.H2
                Zlim2 = point_dict["Z5"] + sign * 0.1 * self.H2
                plot_quote(
                    point_dict["Z4"],
                    Zlim1,
                    Zlim2,
                    point_dict["Z5"],
                    offset_label=sign * 0.05 * self.H2,
                    fig=fig,
                    ax=ax,
                    label="W2",
                )
                # H0
                line = Segment(point_dict["Z8"], point_dict["Z7"])
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
                line = Segment(
                    point_dict["Z2"].real,
                    point_dict["Z3"].real,
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    label="H1 [m]",
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    offset_label=1j * self.get_H1() * 0.3 - self.get_H1() * 0.6,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # H1 [rad]
                line = Arc1(
                    begin=(
                        (point_dict["Z2"] + point_dict["Z3"]) / 2
                        - self.get_H1() / 2
                        - 0.003j
                    ),
                    end=((point_dict["Z2"] + point_dict["Z3"]) / 2),
                    radius=(self.get_H1() / 2),
                    is_trigo_direction=True,
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="H1 [rad]",
                    offset_label=-1j * sign * self.get_H1() * 0.7,
                    fontsize=SC_FONT_SIZE,
                )

                # H2
                line = Segment(point_dict["Z5"], point_dict["Z6"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    label="H2",
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    offset_label=1j * self.W0 * 0.1,
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
                    end=point_dict["Z8"],
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
                # Bot Arc
                line = Arc1(
                    begin=abs(point_dict["Z4"]) * np.exp(-1j * np.pi / 4),
                    end=abs(point_dict["Z4"]) * np.exp(1j * np.pi / 4),
                    radius=abs(point_dict["Z4"]),
                    is_trigo_direction=True,
                )
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
                line = Segment(0, point_dict["Z8"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # H1 lines
                line = Segment(point_dict["Z2"] - 1j, point_dict["Z7"])
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
            W = max(self.W1, self.W2) * 0.7
            Rint = min(point_dict["Z4"].real, point_dict["Z1"].real)
            Rext = max(point_dict["Z4"].real, point_dict["Z1"].real)

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

    # Inlined from Methods.Slot.SlotW23.plot_schematics_constant_tooth
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
        self : SlotW23
            A SlotW23 object
        is_default : bool
            True: plot default schematics, else use current slot values
        is_return_default : bool
            True: return the default lamination used for the schematics (skip plot
        is_add_point_label : bool
            True to display the name of the points (Z1, Z2....)
        is_add_schematics : bool
            True to display the schematics information (W0, H0...)
        is_add_main_line : bool
            True to display "main lines" (slot opening and 0x axis)
        type_add_active : int
            0: No active surface, 1: active surface as winding, 2: active surface as magnet, 3: active surface as winding + wedges
        save_path : str
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
                W0=20e-3,
                H1=20e-3,
                H2=80e-3,
                W3=20e-3,
                is_cstt_tooth=True,
            )
            lam = LamSlot(
                Rint=0.135, Rext=0.3, is_internal=False, is_stator=True, slot=slot
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
                line = Segment(point_dict["Z1"], point_dict["Z8"])
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
                    (point_dict["Z5"] + point_dict["Z6"]) / 2 * np.exp(-1j * sp),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="W3",
                    offset_label=self.H1 * 0.3,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )

                # H0
                line = Segment(point_dict["Z8"], point_dict["Z7"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    label="H0",
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    offset_label=1j * self.W0 * 0.1 + 0.005j - 0.005,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # H1 [m]
                line = Segment(
                    point_dict["Z2"].real,
                    point_dict["Z3"].real,
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    label="H1 [m]",
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    offset_label=1j * self.W0 * 0.1 + 0.005j - 0.005,
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
                    offset_label=-1j * sign * self.get_H1() * 0.8,
                    fontsize=SC_FONT_SIZE,
                )

                # H2
                line = Segment(point_dict["Z5"], point_dict["Z6"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    label="H2",
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    offset_label=1j * self.W0 * 0.05 + 0.005j,
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
                    end=point_dict["Z8"],
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
                # Bot Arc
                line = Arc1(
                    begin=abs(point_dict["Z4"]) * np.exp(-1j * np.pi / 4),
                    end=abs(point_dict["Z4"]) * np.exp(1j * np.pi / 4),
                    radius=abs(point_dict["Z4"]),
                    is_trigo_direction=True,
                )
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
                # W3 parralel
                line = Segment(point_dict["Z3"] * np.exp(1j * sp), point_dict["Z6"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )

                line = Segment(point_dict["Z3"], point_dict["Z6"] * np.exp(-1j * sp))
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
                line = Segment(0, point_dict["Z8"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # H1
                line = Segment(point_dict["Z2"] - 1j, point_dict["Z7"])
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
            W = (point_dict["Z4"] * np.exp(1j * sp)).imag * 1.1
            Rint = min(point_dict["Z4"].real, point_dict["Z1"].real)
            Rext = max(point_dict["Z4"].real, point_dict["Z1"].real)

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

    class S23_H1rCheckError(SlotCheckError):
        """ """

    class S23_W01CheckError(SlotCheckError):
        """ """
