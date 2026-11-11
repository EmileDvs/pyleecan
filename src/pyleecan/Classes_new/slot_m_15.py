# Experimental dataclass generated from Generator/ClassesRef/Slot/SlotM15.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass
from typing import ClassVar

import matplotlib.pyplot as plt
import numpy as np

from ..definitions import config_dict
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
class SlotM15(Slot):
    """single magnet with polar base and curved-top shape and parallel sides

    Attributes
    ----------
    W0 : float
        Slot isthmus angular width.
        Unit: rad; Default: 0.0122; Minimum: 0
    H0 : float
        Slot isthmus height.
        Unit: m; Default: 0.001; Minimum: 0
    W1 : float
        Magnet width
        Unit: m; Default: 0.0122; Minimum: 0
    H1 : float
        Magnet Height
        Unit: m; Default: 0.001; Minimum: 0
    Rtopm : float
        Radius of the magnet top
        Unit: m; Default: 0.001; Minimum: 0
    """

    IS_SYMMETRICAL: ClassVar = 1
    MAGNET_COLOR = config_dict["PLOT"]["COLOR_DICT"]["MAGNET_COLOR"]
    W0: float = 0.0122
    """Slot isthmus angular width."""
    H0: float = 0.001
    """Slot isthmus height."""
    W1: float = 0.0122
    """Magnet width"""
    H1: float = 0.001
    """Magnet Height"""
    Rtopm: float = 0.001
    """Radius of the magnet top"""

    # Inlined from Methods.Slot.SlotM15._comp_point_coordinate
    def _comp_point_coordinate(self):
        """Compute the point coordinates needed to plot the Slot.

        Parameters
        ----------
        self : SlotM15
            A SlotM15 object

        Returns
        -------
        point_dict: dict
            A dict of the slot coordinates
        """

        Rbo = self.get_Rbo()

        Z1 = Rbo * np.exp(-1j * self.W0 / 2)

        # alpha_lim = 2 * arcsin(self.W1 * 0.5 / self.Rtopm)  # Angle of the top arc
        # H_top_arc = self.Rtopm * (1 - cos(alpha_lim / 2))  # Height of the top arc
        if self.is_outwards():
            Z2 = (Rbo + self.H0) * np.exp(-1j * self.W0 / 2)
        else:  # inward slot
            Z2 = (Rbo - self.H0) * np.exp(-1j * self.W0 / 2)

        alpha_M = float(np.arcsin(self.W1 / (2 * abs(Z2))))
        ZM1 = abs(Z2) * np.exp(-1j * alpha_M)
        if self.is_outwards():
            ZM0 = abs(Z2) - self.H1
            Zc = ZM0 + self.Rtopm
        else:  # inward slot
            ZM0 = abs(Z2) + self.H1
            Zc = ZM0 - self.Rtopm

        sign = -1 if self.is_outwards() else 1
        x = abs(Z2) - sign * (
            -self.H1 + self.Rtopm - (self.Rtopm**2 - self.W1**2 / 4) ** 0.5
        )
        ZM2 = x - 1j * self.W1 / 2

        point_dict = {}
        point_dict["Z1"] = Z1
        point_dict["Z2"] = Z2
        point_dict["ZM1"] = ZM1
        point_dict["ZM2"] = ZM2
        point_dict["ZM0"] = ZM0
        point_dict["Zc"] = Zc
        # symetry
        point_dict["Z3"] = Z2.conjugate()
        point_dict["Z4"] = Z1.conjugate()
        point_dict["ZM3"] = ZM2.conjugate()
        point_dict["ZM4"] = ZM1.conjugate()

        return point_dict

    # Inlined from Methods.Slot.SlotM15.build_geometry
    def build_geometry(self):
        """Compute the curve (Line) needed to plot the Slot.
        The ending point of a curve is the starting point of the next curve in
        the list

        Parameters
        ----------
        self : SlotM15
            A SlotM15 object

        Returns
        -------
        curve_list: list
            A list of 3 Segments

        """
        Rbo = self.get_Rbo()
        point_dict = self._comp_point_coordinate()
        Z1 = point_dict["Z1"]
        Z2 = point_dict["Z2"]
        Z3 = point_dict["Z3"]
        Z4 = point_dict["Z4"]

        # Creation of curve
        curve_list = []
        if self.H0 > 0:
            curve_list.append(Segment(begin=Z1, end=Z2))
        if self.is_outwards():
            curve_list.append(
                Arc1(begin=Z2, end=Z3, radius=Rbo + self.H0, is_trigo_direction=True)
            )
        else:
            curve_list.append(
                Arc1(begin=Z2, end=Z3, radius=Rbo - self.H0, is_trigo_direction=True)
            )
        if self.H0 > 0:
            curve_list.append(Segment(begin=Z3, end=Z4))

        return curve_list

    # Inlined from Methods.Slot.SlotM15.check
    def check(self):
        """Check that the SlotM13 object is correct

        Parameters
        ----------
        self : SlotM15
            A SlotM15 object

        Returns
        -------
        None
        """
        Rbo = self.get_Rbo()

        # conversion W0 rad -> m
        W0_m = 2 * (Rbo - self.H0) * np.sin(self.W0 / 2)

        if W0_m < self.W1:
            raise SlotCheckError("You must have W1 <= W0")
        if 2 * self.Rtopm < self.W1:
            raise SlotCheckError("You must have W1 <= 2*Rtopm")

    # Inlined from Methods.Slot.SlotM15.comp_angle_opening
    def comp_angle_opening(self):
        """Compute the average opening angle of the Slot

        Parameters
        ----------
        self : SlotM15
            A SlotM15 object

        Returns
        -------
        alpha: float
            Average opening angle of the slot [rad]

        """

        return self.W0

    # Inlined from Methods.Slot.SlotM15.comp_height
    def comp_height(self):
        """Compute the height of the Slot.
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotM15
            A SlotM15 object

        Returns
        -------
        Htot: float
            Height of the slot [m]

        """

        return self.H0

    # Inlined from Methods.Slot.SlotM15.comp_height_active
    def comp_height_active(self):
        """Compute the height of the active area

        Parameters
        ----------
        self : SlotM15
            A SlotM15 object

        Returns
        -------
        Hwind: float
            Height of the active area [m]

        """

        return self.H1

    # Inlined from Methods.Slot.SlotM15.comp_surface
    def comp_surface(self):
        """Compute the Slot total surface (by analytical computation).
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotM15
            A SlotM15 object

        Returns
        -------
        S: float
            Slot total surface [m**2]

        """

        point_dict = self._comp_point_coordinate()
        Z1 = point_dict["Z1"]
        Z2 = point_dict["Z2"]

        R1 = abs(Z1)
        R2 = abs(Z2)

        S1 = np.pi * R1**2 * (self.W0 / (2 * np.pi))
        S2 = np.pi * R2**2 * (self.W0 / (2 * np.pi))

        return abs(S1 - S2)

    # Inlined from Methods.Slot.SlotM15.comp_surface_active
    def comp_surface_active(self):
        """Compute the Slot active inner surface (by analytical computation)

        Parameters
        ----------
        self : SlotM15
            A SlotM15 object

        Returns
        -------
        Swind: float
            Slot active inner surface [m**2]

        """

        # "Main rectangle"
        point_dict = self._comp_point_coordinate()
        ZM1 = point_dict["ZM1"]
        ZM2 = point_dict["ZM2"]
        S1 = abs(ZM1 - ZM2) * self.W1

        # Top Arc
        alpha = 2 * float(np.arcsin(self.W1 / (2 * self.Rtopm)))
        Sarc = (self.Rtopm**2.0) / 2.0 * (alpha - np.sin(alpha))

        # Bottom polar to remove
        alpha = 2 * float(np.arcsin(self.W1 / (2 * abs(ZM1))))
        Sarc2 = (abs(ZM1) ** 2.0) / 2.0 * (alpha - np.sin(alpha))

        return S1 + Sarc - Sarc2

    # Inlined from Methods.Slot.SlotM15.get_surface_active
    def get_surface_active(self, alpha=0, delta=0):
        """Return the full active surface

        Parameters
        ----------
        self : SlotM15
            A SlotM15 object
        alpha : float
            float number for rotation (Default value = 0) [rad]
        delta : complex
            complex number for translation (Default value = 0)

        Returns
        -------
        surf_act: Surface
            Surface corresponding to the Active Area
        """

        # get the name of the lamination
        st = self.get_name_lam()

        point_dict = self._comp_point_coordinate()
        ZM0 = point_dict["ZM0"]
        ZM1 = point_dict["ZM1"]
        ZM2 = point_dict["ZM2"]
        ZM3 = point_dict["ZM3"]
        ZM4 = point_dict["ZM4"]

        curve_list = []
        curve_list.append(Segment(begin=ZM1, end=ZM2))
        if self.is_outwards():
            curve_list.append(
                Arc1(begin=ZM2, end=ZM3, radius=-self.Rtopm, is_trigo_direction=False)
            )
        else:
            curve_list.append(Arc1(begin=ZM2, end=ZM3, radius=self.Rtopm))
        curve_list.append(Segment(begin=ZM3, end=ZM4))
        curve_list.append(
            Arc1(begin=ZM4, end=ZM1, radius=-abs(ZM4), is_trigo_direction=False)
        )

        Zmid = (abs(ZM1) + abs(ZM3)) / 2  # ref. point on x-axis with respective radius

        surface = SurfLine(
            line_list=curve_list, label="Wind_" + st + "_R0_T0_S0", point_ref=Zmid
        )

        # Apply transformation
        surface.rotate(alpha)
        surface.translate(delta)

        return surface

    # Inlined from Methods.Slot.SlotM15.is_airgap_active
    def is_airgap_active(self):
        """Return True if a part or the full active surface is in the airgap

        Parameters
        ----------
        self : SlotM15
            A SlotM15 object

        Returns
        -------
        is_airgap_active : bool
            True if a part or the full active surface is in the airgap
        """

        return self.comp_height_active() > self.H0

    # Inlined from Methods.Slot.SlotM15.plot_schematics
    def plot_schematics(
        self,
        is_default=False,
        is_return_default=False,
        is_add_point_label=False,
        is_add_schematics=True,
        is_add_main_line=True,
        type_add_active=True,
        save_path=None,
        is_show_fig=True,
        fig=None,
        ax=None,
    ):
        """Plot the schematics of the slot

        Parameters
        ----------
        self : SlotM15
            A SlotM15 object
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
            0: No active surface, 1: active surface as winding, 2: active surface as magnet
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
                Zs=2, W0=60 * np.pi / 180, H0=0.03, H1=0.02, W1=0.05, Rtopm=0.05
            )
            lam = LamSlot(
                Rint=40e-3, Rext=0.11, is_internal=True, is_stator=False, slot=slot
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
                sign = +1
            else:
                sign = -1
            Rbo = self.get_Rbo()

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
                R = Rbo + sign * self.H0 * 1.1
                line = Arc1(
                    begin=R * np.exp(-1j * self.W0 / 2),
                    end=R * np.exp(1j * self.W0 / 2),
                    radius=R,
                    is_trigo_direction=True,
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="W0",
                    offset_label=point_dict["Z3"] - line.get_middle(),
                    fontsize=SC_FONT_SIZE,
                )
                # W1
                plot_quote(
                    Z1=point_dict["ZM2"],
                    Zlim1=point_dict["ZM2"] - sign * self.H1,
                    Zlim2=point_dict["ZM3"] - sign * self.H1,
                    Z2=point_dict["ZM3"],
                    offset_label=0.25 * self.H1,
                    fig=fig,
                    ax=ax,
                    label="W1",
                )
                # H0
                line = Segment(begin=point_dict["Z1"], end=point_dict["Z2"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="H0",
                    offset_label=-1j * point_dict["Z4"].imag * 0.3,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # H1
                plot_quote(
                    Z1=point_dict["ZM0"],
                    Zlim1=point_dict["ZM0"] - 1j * 0.5 * self.W1,
                    Zlim2=point_dict["ZM0"] + sign * self.H1 - 1j * 0.5 * self.W1,
                    Z2=point_dict["ZM0"] + sign * self.H1,
                    offset_label=-1j * 0.2 * self.W1,
                    fig=fig,
                    ax=ax,
                    label="H1",
                )
                # Rtopm
                line = Segment(begin=point_dict["Zc"], end=point_dict["ZM0"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="Rtopm",
                    offset_label=sign * self.Rtopm * 0.4
                    + 1j * point_dict["ZM4"].imag * 0.3,
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
                # Z1 Line
                line = Segment(begin=0, end=Rbo * 2 * np.exp(-1j * self.W0 / 2))
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # Z2 Line
                line = Segment(begin=0, end=Rbo * 2 * np.exp(1j * self.W0 / 2))
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
                    end=point_dict["Z4"],
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
                # Magnet Arc
                line = Segment(begin=point_dict["Zc"], end=point_dict["ZM2"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                line = Segment(begin=point_dict["Zc"], end=point_dict["ZM3"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )

            if type_add_active == 1:
                self.plot_active(fig=fig, ax=ax, is_show_fig=False)
            elif type_add_active == 2:
                self.plot_active(
                    fig=fig,
                    ax=ax,
                    is_show_fig=False,
                    enforced_default_color=self.MAGNET_COLOR,
                )

            # Zooming and cleaning
            W = point_dict["Z4"].imag * 1.2
            Rint, Rext = self.comp_radius()

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
