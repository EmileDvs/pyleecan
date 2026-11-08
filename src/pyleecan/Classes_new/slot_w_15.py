# Experimental dataclass generated from Generator/ClassesRef/Slot/SlotW15.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass
from typing import ClassVar

import matplotlib.pyplot as plt
import numpy as np

from ..definitions import config_dict
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
)
from ._error import ParentMissingError, SlotCheckError
from .arc_1 import Arc1
from .lam_slot import LamSlot
from .segment import Segment
from .slot import Slot
from .surf_line import SurfLine


@dataclass(eq=False)
class SlotW15(Slot):
    """SlotW15

    Attributes
    ----------
    W0 : float
        Slot isthmus width.
        Unit: m; Default: 0.0122; Minimum: 0
    W3 : float
        Tooth width
        Unit: m; Default: 0.0122; Minimum: 0
    H0 : float
        Slot isthmus height.
        Unit: m; Default: 0.001; Minimum: 0
    H1 : float
        Slot intermediate height.
        Unit: m; Default: 0.0015; Minimum: 0
    H2 : float
        Slot height
        Unit: m; Default: 0.0122; Minimum: 0
    R1 : float
        Top radius
        Unit: m; Default: 0.001; Minimum: 0
    R2 : float
        Bottom radius
        Unit: m; Default: 0.001; Minimum: 0
    """

    IS_SYMMETRICAL: ClassVar = 1
    MAGNET_COLOR = config_dict["PLOT"]["COLOR_DICT"]["MAGNET_COLOR"]
    W0: float = 0.0122
    """Slot isthmus width."""
    W3: float = 0.0122
    """Tooth width"""
    H0: float = 0.001
    """Slot isthmus height."""
    H1: float = 0.0015
    """Slot intermediate height."""
    H2: float = 0.0122
    """Slot height"""
    R1: float = 0.001
    """Top radius"""
    R2: float = 0.001
    """Bottom radius"""

    # Inlined from Methods.Slot.SlotW15._comp_line_dict
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
        line_dict = {}
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

    # Inlined from Methods.Slot.SlotW15._comp_point_coordinate
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
        alpha = np.arcsin(self.W0 / (2 * Rbo))
        hsp = np.pi / self.Zs  # Half slot pitch

        Z0 = Rbo * np.exp(1j * 0)
        Z13 = Z0 * np.exp(1j * alpha)
        if self.is_outwards():
            Z12 = Z0 + self.H0 + 1j * Z13.imag
            Z7 = Z0 + self.H0 + self.H1 + self.H2

            # Zc3, Z8 and (0,0) are align (tangent) => abs(Zc3)=Rbo+H0+H1+H2-R2
            # In tooth ref: Im(Zc3') = -W3/2 - R2
            A = Rbo + self.H0 + self.H1 + self.H2 - self.R2
            B = -self.W3 / 2 - self.R2
            xc2 = B * np.sin(-hsp) + np.sqrt(-(B**2) + A**2) * np.cos(-hsp)
            yc2 = B * np.cos(-hsp) - np.sqrt(-(B**2) + A**2) * np.sin(-hsp)
            Zc3 = xc2 + 1j * yc2
            Z9 = (Zc3 * np.exp(1j * -hsp) + self.R2 * 1j) * np.exp(1j * hsp)

            # Zc3, Z8 and (0,0) are align, |Zc3, Z8| = R2
            Z8 = (Zc3 * np.exp(1j * -np.angle(Zc3)) + self.R2) * np.exp(
                1j * np.angle(Zc3)
            )

            # Real(Zc4) = Rbo+H0+H1
            # In tooth ref: Im(Zc4') = -W3/2 - R1
            xc1 = Rbo + self.H0 + self.H1
            yc1 = (-self.W3 / 2 - self.R1 - xc1 * np.sin(-hsp)) / np.cos(-hsp)
            Zc4 = xc1 + 1j * yc1
            Z10 = (Zc4 * np.exp(1j * -hsp) + self.R1 * 1j) * np.exp(1j * hsp)

            # Ref center at Zc4, (Z11,Z12) and (Z11,Zc4) are orthogonal
            # Z11 = R1*exp(1i*theta)
            # (R1*cos(theta)-x2)*R1*cos(theta)+(R1*sin(theta)-y2)*R1*sin(theta) = 0
            R1 = self.R1
            y2 = (Z12 - Zc4).imag
            x2 = (Z12 - Zc4).real
            theta = 2 * np.arctan((y2 - np.sqrt(-(R1**2) + x2**2 + y2**2)) / (R1 + x2))
            Z11 = R1 * np.exp(1j * theta) + Zc4
        else:
            raise self.S15InnerError("Slot Type 15 can't be used on inner lamination")

        point_dict = {}
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

    # Inlined from Methods.Slot.SlotW15.build_geometry
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

    # Inlined from Methods.Slot.SlotW15.check
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
            raise self.S15InnerError("Slot Type 15 can't be used on inner lamination")

    # Inlined from Methods.Slot.SlotW15.comp_angle_opening
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

        return float(2 * np.arcsin(self.W0 / (2 * Rbo)))

    # Inlined from Methods.Slot.SlotW15.comp_height
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

    # Inlined from Methods.Slot.SlotW15.comp_height_active
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

    # Inlined from Methods.Slot.SlotW15.comp_surface
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

    # Inlined from Methods.Slot.SlotW15.comp_surface_opening
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
        Sarc = (Rbo**2.0) / 2.0 * (alpha - np.sin(alpha))
        Harc = float(Rbo * (1 - np.cos(alpha / 2)))
        S1 = (self.H0 + Harc) * self.W0

        # Because Slamination = S - Zs * Sslot
        if self.is_outwards():
            return S1 - Sarc

    # Inlined from Methods.Slot.SlotW15.get_surface_active
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
                curve.prop_dict = {}
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

    # Inlined from Methods.Slot.SlotW15.get_surface_opening
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

    # Inlined from Methods.Slot.SlotW15.plot_schematics
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
        self : SlotW15
            A SlotW15 object
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
                W0=30e-3,
                W3=30e-3,
                H0=15e-3,
                H1=17.5e-3,
                H2=70e-3,
                R1=15e-3,
                R2=15e-3,
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
            Rbo = self.get_Rbo()
            sp = 2 * np.pi / self.Zs
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
                # H0
                line = Segment(
                    Rbo * np.exp(1j * sp),
                    (point_dict["Z2"] + point_dict["Z12"]) / 2 * np.exp(1j * sp),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="H0",
                    offset_label=self.W0 * 0.3,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # H1
                line = Segment(
                    (point_dict["Zc1"] + point_dict["Zc4"]) / 2,
                    (point_dict["Z2"] + point_dict["Z12"]) / 2,
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="H1",
                    offset_label=-self.W0 * 0.5 + 1j * self.W0 * 0.3,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # H2
                line = Segment(
                    (point_dict["Zc1"] + point_dict["Zc4"]) / 2, point_dict["Z7"]
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="H2",
                    offset_label=1j * self.W0 * 0.3,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # R1
                line = Segment(point_dict["Zc1"], point_dict["Z4"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="R1",
                    offset_label=self.W0 * 0.3,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # R2
                line = Segment(point_dict["Zc2"], point_dict["Z5"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="R2",
                    offset_label=self.W0 * 0.3,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # W3
                line = Segment(point_dict["Z10"], point_dict["Z4"] * np.exp(1j * sp))
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="W3",
                    offset_label=self.W0 * 0.4,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                line = Segment(
                    point_dict["Z13"] * np.exp(-1j * sp),
                    point_dict["Z1"] * np.exp(-1j * sp),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="W0",
                    offset_label=self.W0 * 0.4,
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
                # Tooth axis
                line = Segment(0, lam.Rext * 1.5 * np.exp(1j * np.pi / self.Zs))
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # Top arc
                line = Arc1(
                    begin=Rbo * np.exp(-1j * np.pi / 2 * 0.9),
                    end=Rbo * np.exp(1j * np.pi / 2 * 0.9),
                    radius=Rbo,
                    is_trigo_direction=True,
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # Bottom Arc
                line = Arc1(
                    begin=abs(point_dict["Z7"]) * np.exp(-1j * np.pi / 2 * 0.9),
                    end=abs(point_dict["Z7"]) * np.exp(1j * np.pi / 2 * 0.9),
                    radius=abs(point_dict["Z7"]),
                    is_trigo_direction=True,
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # H0 line
                line = Segment(point_dict["Z2"], point_dict["Z12"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                line = Segment(
                    point_dict["Z2"] * np.exp(1j * sp),
                    point_dict["Z12"] * np.exp(1j * sp),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # H1 line
                line = Segment(point_dict["Zc1"], point_dict["Zc4"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # R1 lines
                line = Segment(point_dict["Zc1"], point_dict["Z3"])
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
                line = Segment(point_dict["Z10"], point_dict["Zc4"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                line = Segment(point_dict["Z11"], point_dict["Zc4"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # R2 lines
                line = Segment(point_dict["Zc2"], point_dict["Z5"])
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
                line = Segment(point_dict["Z9"], point_dict["Zc3"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                line = Segment(point_dict["Z8"], point_dict["Zc3"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # W3 line
                line = Segment(point_dict["Z9"], point_dict["Z5"] * np.exp(1j * sp))
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
            W = (point_dict["Z7"] * np.exp(1j * sp)).imag * 1.2
            Rint = min(point_dict["Z5"].real, point_dict["Z1"].real)
            Rext = max(point_dict["Z5"].real, point_dict["Z1"].real)

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

    class S15InnerError(SlotCheckError):
        """ """
