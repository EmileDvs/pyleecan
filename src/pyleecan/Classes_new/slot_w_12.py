# Experimental dataclass generated from Generator/ClassesRef/Slot/SlotW12.csv
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
    plot_quote,
)
from . import ParentMissingError
from .arc_1 import Arc1
from .arc_3 import Arc3
from .lam_slot import LamSlot
from .segment import Segment
from .slot import Slot
from .surf_line import SurfLine


@dataclass(eq=False)
class SlotW12(Slot):
    """SlotW12

    Attributes
    ----------
    H0 : float
        Slot isthmus height.
        Unit: m; Default: 0.003; Minimum: 0
    H1 : float
        Slot middle height
        Unit: m/rad; Default: 0; Minimum: 0
    R1 : float
        Wedges radius
        Unit: m; Default: 0.001; Minimum: 0
    R2 : float
        Slot bottom radius
        Unit: m; Default: 0.001; Minimum: 0
    """

    IS_SYMMETRICAL: ClassVar = 1
    MAGNET_COLOR = config_dict["PLOT"]["COLOR_DICT"]["MAGNET_COLOR"]
    H0: float = 0.003
    """Slot isthmus height."""
    H1: float = 0
    """Slot middle height"""
    R1: float = 0.001
    """Wedges radius"""
    R2: float = 0.001
    """Slot bottom radius"""

    # Inlined from Methods.Slot.SlotW12._comp_line_dict
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
        line_dict = {}
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

    # Inlined from Methods.Slot.SlotW12._comp_point_coordinate
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
        alpha = float(np.arcsin(self.R2 / Rbo))

        # comp point coordinate (in complex)
        Z0 = Rbo * np.exp(1j * 0)
        Z1 = Z0 * np.exp(-1j * alpha)

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

        point_dict = {}
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

    # Inlined from Methods.Slot.SlotW12.build_geometry
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

    # Inlined from Methods.Slot.SlotW12.check
    def check(self):
        """Check that the SlotW12 object is correct

        Parameters
        ----------
        self : SlotW12
            A SlotW12 object

        Returns
        -------
        None

        Raises
        -------
        S12_R20CheckError
            You must have R2 > 0
        S12_RboCheckError
            You must have R2 < Rbo
        """

        Rbo = self.get_Rbo()

        if self.R2 <= 0:
            raise S12_R20CheckError("You must have R2 > 0")

        if self.R2 / Rbo >= 1:
            raise S12_RboCheckError("You must have R2 < Rbo")

    # Inlined from Methods.Slot.SlotW12.comp_angle_opening
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

        return float(2 * np.arcsin(self.R2 / Rbo))

    # Inlined from Methods.Slot.SlotW12.comp_height
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
        Harc = float(Rbo * (1 - np.cos(alpha)))

        if self.is_outwards():
            return self.H0 - Harc + self.R1 * 2 + self.H1 + self.R2
        else:
            return self.H0 + Harc + self.R1 * 2 + self.H1 + self.R2

    # Inlined from Methods.Slot.SlotW12.comp_height_active
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

    # Inlined from Methods.Slot.SlotW12.comp_surface
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

    # Inlined from Methods.Slot.SlotW12.comp_surface_active
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
        S4 = np.pi * self.R2**2 / 2.0

        return S3 + S4

    # Inlined from Methods.Slot.SlotW12.comp_surface_opening
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
        S3 = np.pi * self.R1**2

        # The bottom is an arc
        alpha = self.comp_angle_opening()
        Sarc = (Rbo**2.0) / 2.0 * (alpha - np.sin(alpha))

        # Because Slamination = S - Zs * Sslot
        if self.is_outwards():
            return S1 + S2 + S3 - Sarc
        else:
            return S1 + S2 + S3 + Sarc

    # Inlined from Methods.Slot.SlotW12.get_surface_active
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
                curve.prop_dict = {}
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

    # Inlined from Methods.Slot.SlotW12.get_surface_opening
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
                curve.prop_dict = {}
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

    # Inlined from Methods.Slot.SlotW12.plot_schematics
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
        self : SlotW12
            A SlotW12 object
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
            slot = type(self)(Zs=8, H0=10e-3, R1=5e-3, H1=25e-3, R2=10e-3)
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
                # 2* R2
                line = Segment(point_dict["Z2"], point_dict["Z7"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="2*R2",
                    offset_label=self.R2 * 0.1,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # H0
                Zlim1 = point_dict["Z7"] + 1j * self.R1
                Zlim2 = point_dict["Z8"] + 1j * self.R1
                plot_quote(
                    point_dict["Z7"],
                    Zlim1,
                    Zlim2,
                    point_dict["Z8"],
                    offset_label=-1j * self.R1 * 0.5,
                    fig=fig,
                    ax=ax,
                    label="H0",
                )
                # H1
                Zlim1 = point_dict["Z6"] + 1j * self.R1
                Zlim2 = point_dict["Z5"] + 1j * self.R1
                plot_quote(
                    point_dict["Z6"],
                    Zlim1,
                    Zlim2,
                    point_dict["Z5"],
                    offset_label=-1j * self.R1 * 0.5,
                    fig=fig,
                    ax=ax,
                    label="H1",
                )
                # R1
                line = Segment(point_dict["Zc1"], point_dict["Zi1"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="R1",
                    offset_label=self.R2 * 0.1,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # R2
                line = Segment(point_dict["Zc2"], point_dict["Zi2"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="R2",
                    offset_label=1j * self.R2 * 0.2,
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
                # Radius
                line = Segment(point_dict["Z2"], point_dict["Z3"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                line = Segment(point_dict["Zc3"], point_dict["Zi3"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                line = Segment(point_dict["Z6"], point_dict["Z7"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                line = Segment(point_dict["Z5"], point_dict["Z4"])
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
            W = (self.R1 + self.R2) * 1.2
            Rint = min(point_dict["Z1"].real, point_dict["Zi2"].real)
            Rext = max(point_dict["Z1"].real, point_dict["Zi2"].real)

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

    class MachineCheckError(Exception):
        """ """

    class LaminationCheckError(MachineCheckError):
        """ """

    class SlotCheckError(LaminationCheckError):
        """ """

    class S12_RboCheckError(SlotCheckError):
        """ """

    class S12_R20CheckError(SlotCheckError):
        """ """


MachineCheckError = SlotW12.MachineCheckError
LaminationCheckError = SlotW12.LaminationCheckError
SlotCheckError = SlotW12.SlotCheckError
S12_RboCheckError = SlotW12.S12_RboCheckError
S12_R20CheckError = SlotW12.S12_R20CheckError
