# Experimental dataclass generated from Generator/ClassesRef/Slot/SlotW26.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass
from typing import ClassVar

import matplotlib.pyplot as plt
import numpy as np

from . import ParentMissingError
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
from .arc_1 import Arc1
from .arc_3 import Arc3
from .lam_slot import LamSlot
from .segment import Segment
from .slot import Slot
from .surf_line import SurfLine


@dataclass(eq=False)
class SlotW26(Slot):
    """SlotW26

    Attributes
    ----------
    W0 : float
        Slot isthmus width.
        Unit: m; Default: 0.0122; Minimum: 0
    H0 : float
        Slot isthmus height.
        Unit: m; Default: 0.001; Minimum: 0
    H1 : float
        Slot depth
        Unit: m; Default: 0.003; Minimum: 0
    R1 : float
        Slot edge radius
        Unit: m; Default: 0.003; Minimum: 0
    R2 : float
        Slot top radius
        Unit: m; Default: 0.003; Minimum: 0
    """

    IS_SYMMETRICAL: ClassVar = 1
    MAGNET_COLOR = config_dict["PLOT"]["COLOR_DICT"]["MAGNET_COLOR"]
    W0: float = 0.0122
    """Slot isthmus width."""
    H0: float = 0.001
    """Slot isthmus height."""
    H1: float = 0.003
    """Slot depth """
    R1: float = 0.003
    """Slot edge radius"""
    R2: float = 0.003
    """Slot top radius"""

    # Inlined from Methods.Slot.SlotW26._comp_line_dict
    def _comp_line_dict(self):
        """Define a dictionnary of the lines to draw the slot
        If a line has begin==end, it is replaced by "None" (dict has always the same number of keys)

        Parameters
        ----------
        self : SlotW26
            A SlotW26 object

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

        if self.H1 > 0:
            line_dict["2-3"] = Arc1(
                Z2, Z3, rot_sign * self.R1, is_trigo_direction=self.is_outwards()
            )
            line_dict["3-4"] = Segment(Z3, Z4)
            line_dict["4-5"] = Arc3(Z4, Z5, self.is_outwards())
            line_dict["5-6"] = Segment(Z5, Z6)
            line_dict["6-7"] = Arc1(
                Z6, Z7, rot_sign * self.R1, is_trigo_direction=self.is_outwards()
            )
        elif self.H1 == 0:
            line_dict["2-3"] = Arc1(
                Z2, Z3, rot_sign * self.R1, is_trigo_direction=self.is_outwards()
            )
            line_dict["3-4"] = None
            line_dict["4-5"] = Arc3(Z3, Z6, self.is_outwards())
            line_dict["5-6"] = None
            line_dict["6-7"] = Arc1(
                Z6, Z7, rot_sign * self.R1, is_trigo_direction=self.is_outwards()
            )
        else:  # Should never be called
            raise Slot26_H1(Slot26_H1, "H1 can't be <0")

        if self.H0 > 0:
            line_dict["7-8"] = Segment(Z7, Z8)
        else:
            line_dict["7-8"] = None

        # Closing Arc (Rbo)
        line_dict["8-1"] = Arc1(Z8, Z1, -self.get_Rbo(), is_trigo_direction=False)

        # Closing Active part
        line_dict["2-7"] = Segment(Z2, Z7)
        line_dict["7-2"] = Segment(Z7, Z2)

        return line_dict

    # Inlined from Methods.Slot.SlotW26._comp_point_coordinate
    def _comp_point_coordinate(self):
        """Compute the point coordinates needed to plot the Slot.

        Parameters
        ----------
        self : SlotW26
            A SlotW26 object

        Returns
        -------
        point_dict: dict
            A dict of the slot point coordinates
        """
        Rbo = self.get_Rbo()

        # alpha is the angle to rotate Z0 so ||Z1,Z8|| = W0
        alpha = float(np.arcsin(self.W0 / (2 * Rbo)))
        # comp point coordinate (in complex)
        Z0 = Rbo * np.exp(1j * 0)
        Z1 = Z0 * np.exp(-1j * alpha)

        if self.is_outwards():
            Z2 = Z1 + self.H0
            Zc1 = Z2.real + np.sqrt(self.R1**2 - (self.W0 / 2.0) ** 2)
            Z3 = Zc1 - self.R1 * 1j
            Zc2 = Zc1 + self.H1
            Z4 = Zc2 - 1j * self.R2
            Zbot = Zc2 + self.R2
        else:  # inward slot
            Z2 = Z1 - self.H0
            Zc1 = Z2.real - np.sqrt(self.R1**2 - (self.W0 / 2.0) ** 2)
            Z3 = Zc1 - self.R1 * 1j
            Zc2 = Zc1 - self.H1
            Z4 = Zc2 - 1j * self.R2
            Zbot = Zc2 - self.R2

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
        point_dict["Zc1"] = Zc1
        point_dict["Zc2"] = Zc2
        point_dict["Zbot"] = Zbot
        return point_dict

    # Inlined from Methods.Slot.SlotW26.build_geometry
    def build_geometry(self):
        """Compute the curve (Segment) needed to plot the object.
        The ending point of a curve is the starting point of the next curve in
        the list

        Parameters
        ----------
        self : SlotW26
            A SlotW26 object

        Returns
        -------
        curve_list: list
            A list of 4 Segment and 3 Arc1

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

    # Inlined from Methods.Slot.SlotW26.check
    def check(self):
        """Check that the SlotW26 object is correct

        Parameters
        ----------
        self : SlotW26
            A SlotW26 object

        Returns
        -------
        None

        Raises
        -------
        S26_WCheckError
            You must have W0 < 2*R1
        """
        if self.R1 * 2 <= self.W0:
            raise S26_WCheckError("You must have W0 < 2*R1")

    # Inlined from Methods.Slot.SlotW26.comp_angle_opening
    def comp_angle_opening(self):
        """Compute the average opening angle of the Slot

        Parameters
        ----------
        self : SlotW26
            A SlotW26 object

        Returns
        -------
        alpha: float
            Average opening angle of the slot [rad]

        """
        Rbo = self.get_Rbo()

        return float(2 * np.arcsin(self.W0 / (2 * Rbo)))

    # Inlined from Methods.Slot.SlotW26.comp_height
    def comp_height(self):
        """Compute the height of the Slot.
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotW26
            A SlotW26 object

        Returns
        -------
        Htot: float
            Height of the slot [m]

        """
        Rbo = self.get_Rbo()

        # Computation of the arc height (P1,0,P8)
        alpha = self.comp_angle_opening() / 2
        Harc = float(Rbo * (1 - np.cos(alpha)))

        # Height of the arc (P2,C1,P7)
        Hwind = self.comp_height_active()

        if self.is_outwards():
            return self.H0 + Hwind - Harc
        else:
            return self.H0 + Hwind + Harc

    # Inlined from Methods.Slot.SlotW26.comp_height_active
    def comp_height_active(self):
        """Compute the height of the winding area

        Parameters
        ----------
        self : SlotW26
            A SlotW26 object

        Returns
        -------
        Hwind: float
            Height of the winding area [m]

        """

        # Height of the arc (P2,C1,P7)
        alpha2 = np.arcsin(self.W0 / (2.0 * self.R1))
        Harc2 = float(self.R1 * (1 - np.cos(alpha2)))

        return self.H1 + self.R2 + self.R1 - Harc2

    # Inlined from Methods.Slot.SlotW26.comp_surface
    def comp_surface(self):
        """Compute the Slot total surface (by analytical computation).
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotW26
            A SlotW26 object

        Returns
        -------
        S: float
            Slot total surface [m**2]

        """
        return self.comp_surface_active() + self.comp_surface_opening()

    # Inlined from Methods.Slot.SlotW26.comp_surface_active
    def comp_surface_active(self):
        """Compute the Slot inner surface for winding (by analytical computation)

        Parameters
        ----------
        self : SlotW26
            A SlotW26 object

        Returns
        -------
        Swind: float
            Slot inner surface for winding [m**2]

        """

        # 2 half circle
        S1 = 0.5 * np.pi * self.R1**2
        S2 = 0.5 * np.pi * self.R2**2
        # Trapeze
        S3 = self.H1 * (2 * self.R1 + 2 * self.R2) / 2

        # Angle of the arc (P2,C1,P7)
        alpha2 = 2 * np.arcsin(self.W0 / (2.0 * self.R1))

        # Surface of arc (P2,C1,P7) in the isthmus
        Sarc = (self.R1**2.0) / 2.0 * (alpha2 - np.sin(alpha2))

        return S1 + S2 + S3 - Sarc

    # Inlined from Methods.Slot.SlotW26.comp_surface_opening
    def comp_surface_opening(self):
        """Compute the Slot opening surface (by analytical computation).
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotW26
            A SlotW26 object

        Returns
        -------
        S: float
            Slot opening surface [m**2]

        """
        Rbo = self.get_Rbo()

        S1 = self.H0 * self.W0

        # The bottom is an arc
        alpha = self.comp_angle_opening()
        Sarc = (Rbo**2.0) / 2.0 * (alpha - np.sin(alpha))

        # Because Slamination = S - Zs * Sslot
        if self.is_outwards():
            return S1 - Sarc
        else:
            return S1 + Sarc

    # Inlined from Methods.Slot.SlotW26.get_surface_active
    def get_surface_active(self, alpha=0, delta=0):
        """Return the full winding surface

        Parameters
        ----------
        self : SlotW26
            A SlotW26 object
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
            Zmid = self.get_Rbo() + self.R1 + self.H1 / 2
        else:
            Zmid = self.get_Rbo() - self.R1 - self.H1 / 2
        label = self.parent.get_label() + "_" + WIND_LAB + "_R0-T0-S0"
        surface = SurfLine(line_list=curve_list, label=label, point_ref=Zmid)

        # Apply transformation
        surface.rotate(alpha)
        surface.translate(delta)

        return surface

    # Inlined from Methods.Slot.SlotW26.get_surface_opening
    def get_surface_opening(self, alpha=0, delta=0):
        """Return the list of surfaces defining the opening area of the Slot

        Parameters
        ----------
        self : SlotW26
            A SlotW26 object
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
            Zmid = self.get_Rbo() + self.H0 / 2
        else:
            Zmid = self.get_Rbo() - self.H0 / 2
        label = self.parent.get_label() + "_" + SOP_LAB + "_R0-T0-S0"
        surface = SurfLine(line_list=curve_list, label=label, point_ref=Zmid)

        # Apply transformation
        surface.rotate(alpha)
        surface.translate(delta)

        return [surface]

    # Inlined from Methods.Slot.SlotW26.plot_schematics
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
        self : SlotW21
            A SlotW21 object
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
            slot = type(self)(Zs=8, H0=10e-3, W0=20e-3, R1=15e-3, H1=50e-3, R2=20e-3)
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
                    offset_label=-self.H0 * 0.7,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # H0
                Zlim1 = point_dict["Z8"] + 1j * self.W0 / 2
                Zlim2 = point_dict["Z7"] + 1j * self.W0 / 2
                plot_quote(
                    point_dict["Z8"],
                    Zlim1,
                    Zlim2,
                    point_dict["Z7"],
                    offset_label=1j * self.H0 * 0.2,
                    fig=fig,
                    ax=ax,
                    label="H0",
                )
                # R1
                line = Segment(point_dict["Zc1"], point_dict["Z2"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="R1",
                    offset_label=self.H0 * 0.3 - 1j * self.H0 * 0.2,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # H1
                line = Segment(point_dict["Zc1"], point_dict["Zc2"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    label="H1",
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    offset_label=1j * self.W0 * 0.1,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # R2
                line = Segment(point_dict["Zc2"], point_dict["Z5"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    label="R2",
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    offset_label=self.W0 * 0.1,
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
                # R1 circle
                line = Arc1(
                    begin=point_dict["Z3"],
                    end=point_dict["Z2"],
                    radius=-self.R1,
                    is_trigo_direction=True,
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # R2 circle
                line = Arc1(
                    begin=point_dict["Zbot"],
                    end=point_dict["Z4"],
                    radius=-self.R2,
                    is_trigo_direction=True,
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # Radius lines
                line = Segment(point_dict["Zc2"], point_dict["Zbot"])
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
                line = Segment(point_dict["Z3"], point_dict["Z6"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                line = Segment(point_dict["Z2"], point_dict["Z7"])
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
            W = point_dict["Z5"].imag * 1.3
            Rint = min(point_dict["Zbot"].real, point_dict["Z1"].real)
            Rext = max(point_dict["Zbot"].real, point_dict["Z1"].real)

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

    class Slot26_H1(Exception):
        """ """

    class MachineCheckError(Exception):
        """ """

    class LaminationCheckError(MachineCheckError):
        """ """

    class SlotCheckError(LaminationCheckError):
        """ """

    class S26_WCheckError(SlotCheckError):
        """ """


Slot26_H1 = SlotW26.Slot26_H1
MachineCheckError = SlotW26.MachineCheckError
LaminationCheckError = SlotW26.LaminationCheckError
SlotCheckError = SlotW26.SlotCheckError
S26_WCheckError = SlotW26.S26_WCheckError
