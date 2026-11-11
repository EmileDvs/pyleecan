# Experimental dataclass generated from Generator/ClassesRef/Slot/SlotW25.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass
from typing import ClassVar

import matplotlib.pyplot as plt
import numpy as np

from ..definitions import config_dict
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
)
from ._error import ParentMissingError, SlotCheckError
from .arc_1 import Arc1
from .lam_slot import LamSlot
from .segment import Segment
from .slot import Slot
from .surf_line import SurfLine


@dataclass(eq=False)
class SlotW25(Slot):
    """SlotW25

    Attributes
    ----------
    W3 : float
        Teeth bottom width
        Unit: m; Default: 0.003; Minimum: 0
    H2 : float
        Slot bottom height
        Unit: m; Default: 0.003; Minimum: 0
    W4 : float
        Teeth top width
        Unit: m; Default: 0.003; Minimum: 0
    H1 : float
        Slot top height
        Unit: m; Default: 0.003; Minimum: 0
    """

    IS_SYMMETRICAL: ClassVar = 1
    MAGNET_COLOR = config_dict["PLOT"]["COLOR_DICT"]["MAGNET_COLOR"]
    W3: float = 0.003
    """Teeth bottom width"""
    H2: float = 0.003
    """Slot bottom height"""
    W4: float = 0.003
    """Teeth top width"""
    H1: float = 0.003
    """Slot top height"""

    # Inlined from Methods.Slot.SlotW25._comp_line_dict
    def _comp_line_dict(self):
        """Define a dictionnary of the lines to draw the slot
        If a line has begin==end, it is replaced by "None" (dict has always the same number of keys)

        Parameters
        ----------
        self : SlotW25
            A SlotW25 object

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
        line_dict["1-2"] = Segment(Z1, Z2)
        line_dict["2-3"] = Arc1(Z2, Z3, -abs(Z2), is_trigo_direction=False)
        line_dict["3-4"] = Segment(Z3, Z4)
        line_dict["4-5"] = Arc1(Z4, Z5, abs(Z5))
        line_dict["5-6"] = Segment(Z5, Z6)
        line_dict["6-7"] = Arc1(Z6, Z7, -abs(Z2), is_trigo_direction=False)
        line_dict["7-8"] = Segment(Z7, Z8)

        # Closing Arc (Rbo)
        line_dict["8-1"] = Arc1(Z8, Z1, -self.get_Rbo(), is_trigo_direction=False)

        # Closing Active part
        line_dict["2-7"] = Arc1(Z2, Z7, abs(Z2), is_trigo_direction=True)
        line_dict["7-2"] = Arc1(Z7, Z2, -abs(Z2), is_trigo_direction=False)

        return line_dict

    # Inlined from Methods.Slot.SlotW25._comp_point_coordinate
    def _comp_point_coordinate(self):
        """Compute the point coordinates needed to plot the Slot.

        Parameters
        ----------
        self : SlotW25
            A SlotW25 object

        Returns
        -------
        point_dict: dict
            A dict of the slot point coordinates
        """
        Rbo = self.get_Rbo()

        # We compute the point on the tooth, then rotation to get the slot
        # Zxt is the equivalent of point Zx in tooth ref

        # alpha_0 is the angle to rotate Z0 so ||Z1,Z8|| = W4
        alpha_0 = float(np.arcsin(self.W4 / (2 * Rbo)))

        # comp point coordinate (in complex)
        Z0 = Rbo * np.exp(1j * 0)
        Z1t = Z0 * np.exp(1j * alpha_0)

        if self.is_outwards():
            Z2t = Z1t + self.H1
            # alpha_1 is the angle of Z3t so ||Z3t,Z6t|| = W3
            alpha_1 = float(np.arcsin(self.W3 / (2 * abs(Z2t))))
            Z3t = abs(Z2t) * np.exp(1j * alpha_1)
            Z4t = Z3t + self.H2
        else:  # inward slot
            Z2t = Z1t - self.H1
            # alpha_1 is the angle of Z3t so ||Z3t,Z6t|| = W3
            alpha_1 = float(np.arcsin(self.W3 / (2 * abs(Z2t))))
            Z3t = abs(Z2t) * np.exp(1j * alpha_1)
            Z4t = Z3t - self.H2

        point_dict = {}
        # Rotation to get the slot
        hssp = np.pi / self.Zs
        point_dict["Z1"] = Z1t * np.exp(-1j * hssp)
        point_dict["Z2"] = Z2t * np.exp(-1j * hssp)
        point_dict["Z3"] = Z3t * np.exp(-1j * hssp)
        point_dict["Z4"] = Z4t * np.exp(-1j * hssp)
        # symetry
        point_dict["Z5"] = point_dict["Z4"].conjugate()
        point_dict["Z6"] = point_dict["Z3"].conjugate()
        point_dict["Z7"] = point_dict["Z2"].conjugate()
        point_dict["Z8"] = point_dict["Z1"].conjugate()

        return point_dict

    # Inlined from Methods.Slot.SlotW25.build_geometry
    def build_geometry(self):
        """Compute the curve needed to plot the object.
        The ending point of a curve is the starting point of the next curve in
        the list

        Parameters
        ----------
        self : SlotW25
            A SlotW25 object

        Returns
        -------
        curve_list: list
            A list of 4 Segment and 3 Arc
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

    # Inlined from Methods.Slot.SlotW25.build_geometry_active
    def build_geometry_active(self, Nrad, Ntan, alpha=0, delta=0):
        """Split the slot winding area in several zone

        Parameters
        ----------
        self : SlotW25
            A SlotW25 object
        Nrad : int
            Number of radial layer
        Ntan : int
            Number of tangentiel layer
        alpha : float
            Angle for rotation (Default value = 0) [rad]
        delta : Complex
            complex for translation (Default value = 0)

        Returns
        -------
        surf_list: list
            List of surface delimiting the winding zone

        """
        # get the name of the lamination
        lam_label = self.parent.get_label()

        point_dict = self._comp_point_coordinate()
        Z3 = point_dict["Z3"]
        Z4 = point_dict["Z4"]
        Z5 = point_dict["Z5"]
        Z6 = point_dict["Z6"]
        X = np.linspace(Z3, Z4, Nrad + 1)

        # Nrad+1 and Ntan+1 because 3 points => 2 zones
        Z = np.zeros((Nrad + 1, Ntan + 1), dtype=complex)
        for ii in range(Nrad + 1):
            Z[ii][:] = abs(X[ii]) * np.exp(
                1j * np.linspace(np.angle(X[ii]), np.angle(X[ii].conjugate()), Ntan + 1)
            )

        if self.is_outwards():
            assert abs(Z3) < abs(Z4)
            assert abs(Z6) < abs(Z5)
        assert abs(Z[0][0] - Z3) < 1e-6
        assert abs(Z[Nrad][0] - Z4) < 1e-6
        assert abs(Z[0][Ntan] - Z6) < 1e-6
        assert abs(Z[Nrad][Ntan] - Z5) < 1e-6

        # We go thought the zone by Rad then Tan, starting by (0,0)
        surf_list = []
        for jj in range(Ntan):  # jj from 0 to Ntan-1
            for ii in range(Nrad):  # ii from 0 to Nrad-1
                Z1 = Z[ii][jj]
                Z2 = Z[ii][jj + 1]
                Z3 = Z[ii + 1][jj + 1]
                Z4 = Z[ii + 1][jj]
                point_ref = (Z1 + Z2 + Z3 + Z4) / 4  # reference point of the surface
                # With one zone the order would be [Z7,Z4,Z5,Z6]
                curve_list = []
                curve_list.append(Arc1(Z1, Z2, abs(Z1), is_trigo_direction=True))
                curve_list.append(
                    Segment(
                        Z2,
                        Z3,
                        prop_dict={DRAW_PROP_LAB: False},
                    )
                )
                curve_list.append(
                    Arc1(
                        Z3,
                        Z4,
                        -abs(Z3),
                        is_trigo_direction=False,
                        prop_dict={DRAW_PROP_LAB: False},
                    )
                )
                curve_list.append(
                    Segment(
                        Z4,
                        Z1,
                        prop_dict={DRAW_PROP_LAB: jj != 0},
                    )
                )
                surface = SurfLine(
                    line_list=curve_list,
                    label=lam_label
                    + "_"
                    + WIND_LAB
                    + "_R"
                    + str(ii)
                    + "-T"
                    + str(jj)
                    + "-S0",
                    point_ref=point_ref,
                )
                surf_list.append(surface)

        # Correct bottom line for particular case (cf Tests\Validation\Magnetics\test_FEMM_fast_draw.py)
        if Ntan == 2 and Nrad == 1:
            Z2 = point_dict["Z2"]
            Z7 = point_dict["Z7"]
            # Cut Ox- surface
            arc_to_cut = surf_list[0].line_list[0]
            arc1, arc2 = arc_to_cut.split_line(Z1=0, Z2=Z2)
            surf_list[0].line_list = [arc1[0], arc2[0]] + surf_list[0].line_list[1:]
            surf_list[0].line_list[1].prop_dict = {DRAW_PROP_LAB: False}
            # Cut Ox+ surface
            arc_to_cut = surf_list[1].line_list[0]
            arc1, arc2 = arc_to_cut.split_line(Z1=0, Z2=Z7)
            surf_list[1].line_list = [arc1[0], arc2[0]] + surf_list[1].line_list[1:]
            surf_list[1].line_list[0].prop_dict = {DRAW_PROP_LAB: False}

        for surf in surf_list:
            surf.rotate(alpha)
            surf.translate(delta)
        return surf_list

    # Inlined from Methods.Slot.SlotW25.check
    def check(self):
        """Check that the SlotW25 object is correct

        Parameters
        ----------
        self : SlotW25
            A SlotW25 object

        Returns
        -------
        None

        Raises
        -------
        S25_W4CheckError
            The teeth are too wide, reduce Zs or W4
        S25_HWCheckError
            The teeth are too wide, reduce Zs, H2 or W3

        """
        Rbo = self.get_Rbo()

        if self.H1 == 0:
            raise self.S25_W4CheckError("You must have H1>0 (use Slot 24 for H1=0)")
        if self.H2 == 0:
            raise self.S25_W4CheckError("You must have H2>0 (use Slot 24 for H2=0)")
        if self.W4 == self.W3:
            raise self.S25_W4CheckError(
                "You must have W4 != W3 (use Slot 24 for W4=W3)"
            )

        if 2 * np.arcsin(self.W4 / (2 * Rbo)) > 2 * np.pi / self.Zs:
            raise self.S25_W4CheckError("The teeth are too wide, reduce Zs or W4")

        if (
            not self.is_outwards()
            and 2 * np.arcsin(self.W3 / (2 * Rbo - self.H2 - self.H1))
            > 2 * np.pi / self.Zs
        ):
            raise self.S25_HWCheckError("The teeth are too wide, reduce Zs, H2 or W3")

    # Inlined from Methods.Slot.SlotW25.comp_angle_opening
    def comp_angle_opening(self):
        """Compute the average opening angle of the Slot

        Parameters
        ----------
        self : SlotW25
            A SlotW25 object

        Returns
        -------
        alpha: float
            Average opening angle of the slot [rad]

        """
        Rbo = self.get_Rbo()

        slot_pitch = 2 * np.pi / self.Zs

        alpha_4 = float(2 * np.arcsin(self.W4 / (2 * Rbo)))
        return slot_pitch - alpha_4

    # Inlined from Methods.Slot.SlotW25.comp_height
    def comp_height(self):
        """Compute the height of the Slot.
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotW25
            A SlotW25 object

        Returns
        -------
        Htot: float
            Height of the slot [m]

        """
        point_dict = self._comp_point_coordinate()
        Z4 = point_dict["Z4"]
        Rbo = self.get_Rbo()

        if self.is_outwards():
            return abs(Z4) - Rbo
        else:  # inward slot
            return Rbo - abs(Z4)

    # Inlined from Methods.Slot.SlotW25.comp_height_active
    def comp_height_active(self):
        """Compute the height of the winding area

        Parameters
        ----------
        self : SlotW25
            A SlotW25 object

        Returns
        -------
        Hwind: float
            Height of the winding area [m]

        """

        return self.H2

    # Inlined from Methods.Slot.SlotW25.comp_surface
    def comp_surface(self):
        """Compute the Slot total surface (by analytical computation).
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotW25
            A SlotW25 object

        Returns
        -------
        S: float
            Slot total surface [m**2]

        """
        return self.comp_surface_active() + self.comp_surface_opening()

    # Inlined from Methods.Slot.SlotW25.comp_surface_active
    def comp_surface_active(self):
        """Compute the Slot inner surface for winding (by analytical computation)

        Parameters
        ----------
        self : SlotW25
            A SlotW25 object

        Returns
        -------
        Swind: float
            Slot inner surface for winding [m**2]

        """

        point_dict = self._comp_point_coordinate()
        Z2 = point_dict["Z2"]
        Z4 = point_dict["Z4"]

        if self.is_outwards():
            Rint = abs(Z2)
            Rext = abs(Z4)
        else:
            Rint = abs(Z4)
            Rext = abs(Z2)

        # Surface of a slot pitch
        Sring = (np.pi * Rext**2 - np.pi * Rint**2) * 1 / self.Zs

        # Tooth surface
        St = self.H2 * self.W3

        alpha_bore = 2 * np.arcsin(self.W3 / (2 * Rint))
        Sarc_bore = (Rint**2.0) / 2.0 * (alpha_bore - np.sin(alpha_bore))

        alpha_yoke = 2 * np.arcsin(self.W3 / (2 * Rext))
        Sarc_yoke = (Rext**2.0) / 2.0 * (alpha_yoke - np.sin(alpha_yoke))

        return Sring - (St + Sarc_yoke - Sarc_bore)

    # Inlined from Methods.Slot.SlotW25.comp_surface_opening
    def comp_surface_opening(self):
        """Compute the Slot opening surface (by analytical computation).
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotW25
            A SlotW25 object

        Returns
        -------
        S: float
            Slot opening surface [m**2]

        """

        point_dict = self._comp_point_coordinate()
        Z1 = point_dict["Z1"]
        Z2 = point_dict["Z2"]

        if self.is_outwards():
            Rint = abs(Z1)
            Rext = abs(Z2)
        else:
            Rint = abs(Z2)
            Rext = abs(Z1)

        # Surface of a slot pitch
        Sring = (np.pi * Rext**2 - np.pi * Rint**2) * 1 / self.Zs

        # Tooth surface
        St = self.H1 * self.W4

        alpha_bore = 2 * np.arcsin(self.W4 / (2 * Rint))
        Sarc_bore = (Rint**2.0) / 2.0 * (alpha_bore - np.sin(alpha_bore))

        alpha_yoke = 2 * np.arcsin(self.W4 / (2 * Rext))
        Sarc_yoke = (Rext**2.0) / 2.0 * (alpha_yoke - np.sin(alpha_yoke))

        return Sring - (St + Sarc_yoke - Sarc_bore)

    # Inlined from Methods.Slot.SlotW25.get_surface_active
    def get_surface_active(self, alpha=0, delta=0):
        """Return the full winding surface

        Parameters
        ----------
        self : SlotW25
            A SlotW25 object
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
            line_dict["7-2"],
        ]
        curve_list = [line for line in curve_list if line is not None]

        # Only the closing arc (7-2) needs to be drawn (in FEMM)
        for curve in curve_list[:-1]:
            if curve.prop_dict is None:
                curve.prop_dict = {}
            curve.prop_dict.update({DRAW_PROP_LAB: False})

        # Create surface
        if self.is_outwards():
            Zmid = self.get_Rbo() + self.H1 + self.H2 / 2
        else:
            Zmid = self.get_Rbo() - self.H1 - self.H2 / 2
        label = self.parent.get_label() + "_" + WIND_LAB + "_R0-T0-S0"
        surface = SurfLine(line_list=curve_list, label=label, point_ref=Zmid)

        # Apply transformation
        surface.rotate(alpha)
        surface.translate(delta)

        return surface

    # Inlined from Methods.Slot.SlotW25.get_surface_opening
    def get_surface_opening(self, alpha=0, delta=0):
        """Return the list of surfaces defining the opening area of the Slot

        Parameters
        ----------
        self : SlotW25
            A SlotW25 object
        alpha : float
            float number for rotation (Default value = 0) [rad]
        delta : complex
            complex number for translation (Default value = 0)

        Returns
        -------
        surf_list : list
            list of surfaces objects
        """

        # H1=0 no opening
        if self.H1 == 0:
            return []

        # Create curve list
        line_dict = self._comp_line_dict()
        curve_list = [
            line_dict["1-2"],
            line_dict["2-7"],
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
            Zmid = self.get_Rbo() + self.H1 / 2
        else:
            Zmid = self.get_Rbo() - self.H1 / 2
        label = self.parent.get_label() + "_" + SOP_LAB + "_R0-T0-S0"
        surface = SurfLine(line_list=curve_list, label=label, point_ref=Zmid)

        # Apply transformation
        surface.rotate(alpha)
        surface.translate(delta)

        return [surface]

    # Inlined from Methods.Slot.SlotW25.plot_schematics
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
        self : SlotW25
            A SlotW25 object
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
            slot = type(self)(Zs=14, W3=20e-3, H2=80e-3, H1=15e-3, W4=40e-3)
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
                # W4
                line = Segment(point_dict["Z8"], point_dict["Z1"] * np.exp(1j * sp))
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="W4",
                    offset_label=self.H1 * 0.3,
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
                # H1
                line = Segment(point_dict["Z1"], point_dict["Z2"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="H1",
                    offset_label=-1j * self.H1 * 0.8,
                    is_arrow=True,
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
                    offset_label=-1j * self.H1 * 0.6,
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
                # Middle arc
                R = abs(point_dict["Z3"])
                line = Arc1(
                    begin=R * np.exp(-1j * np.pi / 2 * 0.9),
                    end=R * np.exp(1j * np.pi / 2 * 0.9),
                    radius=R,
                    is_trigo_direction=True,
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # Bot arc
                R = abs(point_dict["Z4"])
                line = Arc1(
                    begin=R * np.exp(-1j * np.pi / 2 * 0.9),
                    end=R * np.exp(1j * np.pi / 2 * 0.9),
                    radius=R,
                    is_trigo_direction=True,
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # Tooth axis
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

    class S25_HWCheckError(SlotCheckError):
        """ """

    class S25_W4CheckError(SlotCheckError):
        """ """
