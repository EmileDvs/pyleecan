# Experimental dataclass generated from Generator/ClassesRef/Slot/SlotW27.csv
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
    plot_quote,
)
from ._error import ParentMissingError, SlotCheckError
from .arc_1 import Arc1
from .lam_slot import LamSlot
from .segment import Segment
from .slot import Slot
from .surf_line import SurfLine


@dataclass(eq=False)
class SlotW27(Slot):
    """semi-closed trapezoidal without fillet without wedge (flat bottom)

    Attributes
    ----------
    H0 : float
        Slot isthmus height.
        Unit: m; Default: 0.003; Minimum: 0
    H1 : float
        Slot first part height
        Unit: m; Default: 0; Minimum: 0
    H2 : float
        Slot second part height
        Unit: m; Default: 0.02; Minimum: 0
    W0 : float
        Slot isthmus width.
        Unit: m; Default: 0.003; Minimum: 0
    W1 : float
        Slot top width.
        Unit: m; Default: 0.013; Minimum: 0
    W2 : float
        Slot middle width
        Unit: m; Default: 0.01; Minimum: 0
    W3 : float
        Slot bottom width.
        Unit: m; Default: 0.003; Minimum: 0
    is_trap_wind : bool
        If True, split the winding on the  trapezium bases. Else split at the middle height as usual
        Default: False
    """

    IS_SYMMETRICAL: ClassVar = 1
    MAGNET_COLOR = config_dict["PLOT"]["COLOR_DICT"]["MAGNET_COLOR"]
    H0: float = 0.003
    """Slot isthmus height."""
    H1: float = 0
    """Slot first part height"""
    H2: float = 0.02
    """Slot second part height"""
    W0: float = 0.003
    """Slot isthmus width."""
    W1: float = 0.013
    """Slot top width."""
    W2: float = 0.01
    """Slot middle width"""
    W3: float = 0.003
    """Slot bottom width."""
    is_trap_wind: bool = False
    """If True, split the winding on the  trapezium bases. Else split at the middle height as usual"""

    # Inlined from Methods.Slot.SlotW27._comp_line_dict
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
        line_dict = {}
        line_dict["1-2"] = Segment(begin=Z1, end=Z2)
        line_dict["2-3"] = Segment(begin=Z2, end=Z3)
        line_dict["3-4"] = Segment(begin=Z3, end=Z4)
        line_dict["4-5"] = Segment(begin=Z4, end=Z5)
        line_dict["5-6"] = Segment(begin=Z5, end=Z6)
        line_dict["6-7"] = Segment(begin=Z6, end=Z7)
        line_dict["7-8"] = Segment(begin=Z7, end=Z8)
        line_dict["8-9"] = Segment(begin=Z8, end=Z9)
        line_dict["9-10"] = Segment(begin=Z9, end=Z10)

        # Closing Arc (Rbo)
        line_dict["10-1"] = Arc1(
            begin=Z10, end=Z1, radius=-self.get_Rbo(), is_trigo_direction=False
        )

        # Closing Active part
        line_dict["2-9"] = Segment(begin=Z2, end=Z9)
        line_dict["9-2"] = Segment(begin=Z9, end=Z2)

        return line_dict

    # Inlined from Methods.Slot.SlotW27._comp_point_coordinate
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
        alpha = float(np.arcsin(self.W0 / (2 * Rbo)))

        # comp point coordinate (in complex)
        Z0 = Rbo * np.exp(1j * 0)
        Z1 = Z0 * np.exp(-1j * alpha)

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

        point_dict = {}
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

    # Inlined from Methods.Slot.SlotW27.build_geometry
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

    # Inlined from Methods.Slot.SlotW27.check
    def check(self):
        """Check that the SlotW27 object is correct

        Parameters
        ----------
        self : SlotW27
            A SlotW27 object

        Returns
        -------
        None

        Raises
        -------
        S27_W01CheckError
            You must have W0 <= W1
        S27_W12CheckError
            You must have W1 <= W2
        S27_W03CheckError
            You must have W0 <= W3

        """
        if self.W1 < self.W0:
            raise self.S27_W01CheckError("You must have W0 <= W1")

        if self.W2 < self.W1:
            raise self.S27_W12CheckError("You must have W1 <= W2")

        if self.W3 < self.W0:
            raise self.S27_W03CheckError("You must have W0 <= W3")

    # Inlined from Methods.Slot.SlotW27.comp_angle_opening
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

        return float(2 * np.arcsin(self.W0 / (2 * Rbo)))

    # Inlined from Methods.Slot.SlotW27.comp_height
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
        Harc = float(Rbo * (1 - np.cos(alpha)))

        if self.is_outwards():
            return (
                abs(Rbo - Harc + self.H0 + self.H1 + self.H2 + 1j * self.W3 / 2.0) - Rbo
            )
        else:
            return self.H0 + self.H1 + self.H2 + Harc

    # Inlined from Methods.Slot.SlotW27.comp_height_active
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

    # Inlined from Methods.Slot.SlotW27.comp_surface
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

    # Inlined from Methods.Slot.SlotW27.comp_surface_active
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

    # Inlined from Methods.Slot.SlotW27.comp_surface_opening
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
        Sarc = (Rbo**2.0) / 2.0 * (alpha - np.sin(alpha))

        # Because Slamination = S - Zs * Sslot
        if self.is_outwards():
            return S1 - Sarc
        else:
            return S1 + Sarc

    # Inlined from Methods.Slot.SlotW27.get_surface_active
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
                curve.prop_dict = {}
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

    # Inlined from Methods.Slot.SlotW27.get_surface_opening
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

    # Inlined from Methods.Slot.SlotW27.plot_schematics
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
        self : SlotW27
            A SlotW27 object
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
            0: No active surface, 1: active surface as winding, 2: active surface as , 3: active surface as winding + wedges
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
                Zs=8,
                H0=10e-3,
                H1=40e-3,
                H2=20e-3,
                W0=20e-3,
                W1=40e-3,
                W2=60e-3,
                W3=30e-3,
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
                line = Segment(begin=point_dict["Z1"], end=point_dict["Z10"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="W0",
                    offset_label=-self.H0 * 0.9,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # W1
                Zlim1 = point_dict["Z3"] + sign * self.H1 * 0.3
                Zlim2 = point_dict["Z8"] + sign * self.H1 * 0.3
                plot_quote(
                    point_dict["Z3"],
                    Zlim1,
                    Zlim2,
                    point_dict["Z8"],
                    offset_label=sign * self.H0 * 0.2,
                    fig=fig,
                    ax=ax,
                    label="W1",
                )
                # W2
                line = Segment(begin=point_dict["Z4"], end=point_dict["Z7"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="W2",
                    offset_label=self.H0 * 0.2,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # W3
                Zlim1 = point_dict["Z6"] + sign * self.H0 * 0.4
                Zlim2 = point_dict["Z5"] + sign * self.H0 * 0.4
                plot_quote(
                    point_dict["Z6"],
                    Zlim1,
                    Zlim2,
                    point_dict["Z5"],
                    offset_label=self.H0 * 0.2,
                    fig=fig,
                    ax=ax,
                    label="W3",
                )
                # H0
                line = Segment(begin=point_dict["Z10"], end=point_dict["Z9"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    label="H0",
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    offset_label=1j * self.W0 * 0.2,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # H1
                Zlim1 = point_dict["Z3"].real + 1j * point_dict["Z4"].imag
                Zlim2 = point_dict["Z4"]
                plot_quote(
                    point_dict["Z3"],
                    Zlim1,
                    Zlim2,
                    point_dict["Z4"],
                    offset_label=-1j * self.H0 * 0.6,
                    fig=fig,
                    ax=ax,
                    label="H1",
                )
                # H2
                Zlim1 = point_dict["Z6"].real + 1j * point_dict["Z7"].imag
                Zlim2 = point_dict["Z7"]
                plot_quote(
                    point_dict["Z6"],
                    Zlim1,
                    Zlim2,
                    point_dict["Z7"],
                    offset_label=1j * self.H0 * 0.4,
                    fig=fig,
                    ax=ax,
                    label="H2",
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
            W = max(self.W1, self.W2, self.W3) * 0.7
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

    class S27_W01CheckError(SlotCheckError):
        """ """

    class S27_W03CheckError(SlotCheckError):
        """ """

    class S27_W12CheckError(SlotCheckError):
        """ """
