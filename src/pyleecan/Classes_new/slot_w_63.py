# Experimental dataclass generated from Generator/ClassesRef/Slot/SlotW63.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass
from typing import ClassVar

import matplotlib.pyplot as plt
import numpy as np

from ..definitions import config_dict
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
from ._error import ParentMissingError, SlotCheckError
from .arc_1 import Arc1
from .lam_slot import LamSlot
from .segment import Segment
from .slot import Slot
from .surf_line import SurfLine


@dataclass(eq=False)
class SlotW63(Slot):
    """SlotW63

    Attributes
    ----------
    W0 : float
        Pole bottom width
        Unit: m; Default: 0.314; Minimum: 0
    W1 : float
        Pole top width
        Unit: m; Default: 0.02; Minimum: 0
    H0 : float
        Pole bottom height
        Unit: m; Default: 0.003; Minimum: 0
    H1 : float
        Pole top height
        Unit: m; Default: 0.05; Minimum: 0
    H2 : float
        Heigh Ploe
        Unit: m; Default: 0.0; Minimum: 0
    W2 : float
        Width Ploe
        Unit: m; Default: 0.0; Minimum: 0
    """

    IS_SYMMETRICAL: ClassVar = 0
    MAGNET_COLOR = config_dict["PLOT"]["COLOR_DICT"]["MAGNET_COLOR"]
    W0: float = 0.314
    """Pole bottom width"""
    W1: float = 0.02
    """Pole top width"""
    H0: float = 0.003
    """Pole bottom height"""
    H1: float = 0.05
    """Pole top height"""
    H2: float = 0.0
    """Heigh Ploe"""
    W2: float = 0.0
    """Width Ploe"""

    # Inlined from Methods.Slot.SlotW63._comp_line_dict
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
        line_dict = {}
        line_dict["1-2"] = Segment(begin=Z1, end=Z2)
        line_dict["2-3"] = Segment(begin=Z2, end=Z3)
        line_dict["3-4"] = Segment(begin=Z3, end=Z4)
        line_dict["4-5"] = Segment(begin=Z4, end=Z5)
        line_dict["5-6"] = Segment(begin=Z5, end=Z6)
        line_dict["6-7"] = Segment(begin=Z6, end=Z7)
        line_dict["7-8"] = Segment(begin=Z7, end=Z8)

        # Winding lines
        line_dict["w1-2"] = Segment(begin=Zw1, end=Z2)
        line_dict["2-w1"] = Segment(begin=Z2, end=Zw1)
        line_dict["4-w2"] = Segment(begin=Z4, end=Zw2)
        line_dict["w2-w1"] = Segment(begin=Zw2, end=Zw1)
        line_dict["w1-w2"] = Segment(begin=Zw1, end=Zw2)

        line_dict["w2s-5"] = Segment(begin=Zw2s, end=Z5)
        line_dict["7-w1s"] = Segment(begin=Z7, end=Zw1s)
        line_dict["w1s-w2s"] = Segment(begin=Zw1s, end=Zw2s)

        line_dict["w1s-7"] = Segment(begin=Zw1s, end=Z7)

        line_dict["w2s-w1s"] = Segment(begin=Zw2s, end=Zw1s)
        line_dict["w2-w2s"] = Segment(begin=Zw2, end=Zw2s)

        line_dict["7-2"] = Segment(begin=Z7, end=Z2)
        line_dict["2-7"] = Segment(begin=Z2, end=Z7)

        line_dict["8-1"] = Arc1(
            begin=Z8, end=Z1, radius=-abs(Z8), is_trigo_direction=False
        )

        if self.H2 == 0:
            line_dict["7w-2w"] = Arc1(
                begin=Z7, end=Z2, radius=-abs(Z7), is_trigo_direction=False
            )

        return line_dict

    # Inlined from Methods.Slot.SlotW63._comp_point_coordinate
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
        hsp = np.pi / self.Zs  # Half slot pitch

        alpha = np.arcsin(self.W1 / (2 * Rbo))

        # Point used to define geometry of slot
        Z1 = Rbo * np.exp(1j * alpha)
        Z2 = Z1 - self.H2
        Z3 = (
            Z2
            - ((self.W1 - self.W0) / 2) * np.sin(self.H1)
            - 1j * ((self.W1 - self.W0) / 2)
        )
        Z4 = Z3 - self.H0

        # Set points in correct base with a rotation
        Z1 = Z1 * np.exp(-1j * hsp)
        Z2 = Z2 * np.exp(-1j * hsp)
        Z3 = Z3 * np.exp(-1j * hsp)
        Z4 = Z4 * np.exp(-1j * hsp)

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

        point_dict = {}
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

    # Inlined from Methods.Slot.SlotW63.build_geometry
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

    # Inlined from Methods.Slot.SlotW63.build_geometry_active
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
            raise self.S63_WindError(
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

            surf_list = []
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

            surf_list = []
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

    # Inlined from Methods.Slot.SlotW63.check
    def check(self):
        """Check that the SlotW63 object is correct

        Parameters
        ----------
        self : SlotW63
            A SlotW63 object

        Returns
        -------
        None
        Raises
        -------
        S63_InnerCheckError
            Slot 63 is for inner lamination only

        """
        if self.is_outwards():
            raise self.S63_InnerCheckError("Slot 63 is for inner lamination only")

        if self.W0 >= self.W1:
            raise self.S63_W0CheckError("You must have W1 > W0")

        if self.H0 == 0:
            raise self.S63_H0CheckError("You must have H0 > 0")

        if self.W0 == 0:
            raise self.S63_W0CheckError("You must have W0 > 0")

    # Inlined from Methods.Slot.SlotW63.comp_angle_opening
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
        slot_pitch = 2 * np.pi / self.Zs
        tooth_angle = 2 * np.arcsin(self.W1 / (2 * self.get_Rbo()))

        return slot_pitch - tooth_angle

    # Inlined from Methods.Slot.SlotW63.comp_height
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

    # Inlined from Methods.Slot.SlotW63.comp_height_active
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

    # Inlined from Methods.Slot.SlotW63.comp_surface
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
        Sring = (np.pi * Rext**2 - np.pi * Rint**2) / self.Zs

        # Surface define by arc of circle between Z4 and Z5 with radius abs(Z5)
        # bottom is not a cercle
        D54 = abs(Z5 - Z4)
        alpha = 2 * np.arcsin(D54 / (2 * Rint))
        Sarc_bot2 = (Rint**2.0) / 2.0 * (alpha - np.sin(alpha))

        # Tooth surface
        H = np.sin(self.H1) * (self.W1 - self.W0) / 2
        St = (
            self.H0 * self.W0
            + self.H2 * self.W1
            + H * (self.W1 - self.W0) / 2
            + self.W0 * H
        )

        # Surface define by arc of circle between Z8 and Z1d with radius rbo
        alpha_top = 2 * np.arcsin(self.W1 / (2 * Rext))
        Sarc_top = (Rext**2.0) / 2.0 * (alpha_top - np.sin(alpha_top))

        # Surface define by arc of circle between Z5 and Z4d with radius abs(Z5)
        alpha_bot = 2 * np.arcsin(self.W0 / (2 * Rint))
        Sarc_bot1 = (Rint**2.0) / 2.0 * (alpha_bot - np.sin(alpha_bot))

        return Sring - (St + Sarc_top - Sarc_bot1) + Sarc_bot2

    # Inlined from Methods.Slot.SlotW63.comp_surface_active
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
        alpha = 2 * np.arcsin(D81 / (2 * Rbo))
        Sarc_top = (Rbo**2.0) / 2.0 * (alpha - np.sin(alpha))

        D72 = abs(Z7 - Z2)

        Striangle = (Z8.real - Z7.real) * (Z8.imag - Z7.imag)

        Srect = D72 * (Z8.real - Z7.real)

        return surface - s_bottom - Sarc_top - Striangle - Srect

    # Inlined from Methods.Slot.SlotW63.get_surface_active
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

    # Inlined from Methods.Slot.SlotW63.get_surface_opening
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
                curve.prop_dict = {}
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

    # Inlined from Methods.Slot.SlotW63.plot_schematics
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
        self : SlotW63
            A SlotW63 object
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
                H0=30e-3,
                W0=30e-3,
                H1=0.78539,
                W1=80e-3,
                H2=40e-3,
                W2=15e-3,
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
                is_show_fig=False, fig=fig, ax=ax
            )  # center slot on Ox axis
            point_dict = {}
            point_dict_temp = self._comp_point_coordinate()
            for key in point_dict_temp:
                point_dict[key] = point_dict_temp[key] * np.exp(
                    1j * (np.pi / self.Zs + 4 * np.pi / self.Zs)
                )
                point_dict[key + "d"] = point_dict[key] * np.exp(
                    1j * (2 * np.pi / self.Zs)
                )
                point_dict[key + "dd"] = point_dict[key + "d"] * np.exp(
                    1j * (2 * np.pi / self.Zs)
                )

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
                line = Segment(
                    begin=(point_dict["Z4d"] + point_dict["Z3d"]) / 2,
                    end=(point_dict["Z6"] + point_dict["Z5"]) / 2,
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    label="W0",
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    offset_label=1j * self.W0 * 0.2 - (0.007 + 0j),
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # H0
                Zlim1 = (
                    point_dict["Z3d"]
                    - (self.W1 - self.W0) / 8
                    - (self.W1 - self.W0) / 2
                )
                Zlim2 = (
                    point_dict["Z4d"]
                    - (self.W1 - self.W0) / 8
                    - (self.W1 - self.W0) / 2
                )
                plot_quote(
                    point_dict["Z3d"],
                    Zlim1,
                    Zlim2,
                    point_dict["Z4d"],
                    offset_label=-self.H0 * 0.6,
                    fig=fig,
                    ax=ax,
                    label="H0",
                )
                # W1
                line = Segment(
                    begin=(point_dict["Z1d"] + point_dict["Z2d"]) / 2,
                    end=(point_dict["Z8"] + point_dict["Z7"]) / 2,
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    label="W1",
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    offset_label=1j * self.W0 * 0.2 - self.W1 * 0.05,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )

                # H2
                line = Segment(
                    begin=point_dict["Z1d"],
                    end=point_dict["Z2d"],
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    label="H2",
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    offset_label=-self.H2 * 0.5,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )

                # H1 [rad]
                line = Arc1(
                    begin=point_dict["Z6"] + self.W0 / 1.5,
                    end=(((point_dict["Z6"] + point_dict["Z7"]) / 2) + point_dict["Z7"])
                    / 2,
                    radius=(self.W0 / 2),
                    is_trigo_direction=True,
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="H1",
                    offset_label=self.W0 * 0.2,
                    fontsize=SC_FONT_SIZE,
                )

                if type_add_active != 0:
                    # W2
                    line = Segment(
                        begin=point_dict["Zw1s"],
                        end=point_dict["Zw1"],
                    )
                    line.plot(
                        fig=fig,
                        ax=ax,
                        label="W2",
                        color=ARROW_COLOR,
                        linewidth=ARROW_WIDTH,
                        offset_label=1j * self.W2 * 0.6,
                        is_arrow=True,
                        fontsize=SC_FONT_SIZE,
                    )

            if is_add_main_line:
                # Ox axis
                line = Segment(begin=0, end=lam.Rext * 1.5)
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # H1
                line = Segment(begin=point_dict["Z6"], end=point_dict["Z6"] + self.W0)
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # Top arc
                line = Arc1(
                    begin=self.get_Rbo(),
                    end=-self.get_Rbo(),
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

            if type_add_active in [1, 3]:  # Wind and Wedge
                is_add_wedge = False  # No wedge for this false
                self.plot_active(
                    fig=fig,
                    ax=ax,
                    is_show_fig=False,
                    is_add_wedge=is_add_wedge,
                    wind_mat=np.ones((1, 2, self.Zs, 1)),
                    alpha=np.pi / self.Zs + 2 * np.pi / self.Zs,
                )
                self.plot_active(
                    fig=fig,
                    ax=ax,
                    is_show_fig=False,
                    is_add_wedge=is_add_wedge,
                    wind_mat=np.ones((1, 2, self.Zs, 1)),
                    alpha=np.pi / self.Zs + 4 * np.pi / self.Zs,
                )
                self.plot_active(
                    fig=fig,
                    ax=ax,
                    is_show_fig=False,
                    is_add_wedge=is_add_wedge,
                    wind_mat=np.ones((1, 2, self.Zs, 1)),
                    alpha=np.pi / self.Zs + 6 * np.pi / self.Zs,
                )
                self.plot_active(
                    fig=fig,
                    ax=ax,
                    is_show_fig=False,
                    is_add_wedge=is_add_wedge,
                    wind_mat=np.ones((1, 2, self.Zs, 1)),
                    alpha=np.pi / self.Zs + 8 * np.pi / self.Zs,
                )
            elif type_add_active == 2:  # Magnet
                self.plot_active(
                    fig=fig,
                    ax=ax,
                    is_show_fig=False,
                    enforced_default_color=self.MAGNET_COLOR,
                )

            # Zooming and cleaning
            ax.axis("equal")
            ax.set_ylim(abs(point_dict["Z2"]) * 0.5, abs(point_dict["Z2"]) * 1.2)
            ax.set_xlim(-2 * self.W0, 2 * self.W0)
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

    class S63_H0CheckError(SlotCheckError):
        """ """

    class S63_InnerCheckError(SlotCheckError):
        """ """

    class S63_W0CheckError(SlotCheckError):
        """ """

    class S63_WindError(SlotCheckError):
        """

        Parameters
        ----------

        Returns
        -------

        Raises
        ------
        winding


        """
