# Experimental dataclass generated from Generator/ClassesRef/Slot/SlotM13.csv
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
class SlotM13(Slot):
    """Rectangular Slot with Rectangular magnet with circular top

    Attributes
    ----------
    W0 : float
        Slot isthmus width.
        Unit: m; Default: 0.0122; Minimum: 0
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
    """Slot isthmus width."""
    H0: float = 0.001
    """Slot isthmus height."""
    W1: float = 0.0122
    """Magnet width"""
    H1: float = 0.001
    """Magnet Height"""
    Rtopm: float = 0.001
    """Radius of the magnet top"""

    # Inlined from Methods.Slot.SlotM13._comp_point_coordinate
    def _comp_point_coordinate(self):
        """Compute the point coordinates needed to plot the Slot.

        Parameters
        ----------
        self : SlotM13
            A SlotM13 object

        Returns
        -------
        point_dict: dict
            A dict of the slot coordinates
        """

        Rbo = self.get_Rbo()

        # alpha is the angle to rotate Z0 so ||Z1,Z10|| = W0
        alpha = float(np.arcsin(self.W0 / (2 * Rbo)))

        Z1 = Rbo * np.exp(-1j * alpha)

        alpha_lim = 2 * np.arcsin(self.W1 * 0.5 / self.Rtopm)  # Angle of the top arc
        H_top_arc = self.Rtopm * (1 - np.cos(alpha_lim / 2))  # Heiht of the top arc
        if self.is_outwards():
            Z2 = Z1 + self.H0
        else:  # inward slot
            Z2 = Z1 - self.H0
        ZM1 = Z2.real - 1j * self.W1 / 2
        if self.is_outwards():
            ZM0 = Z2.real - self.H1
            Zc = ZM0 + self.Rtopm
            ZM2 = ZM1 - self.H1 + H_top_arc
        else:  # inward slot
            ZM0 = Z2.real + self.H1
            Zc = ZM0 - self.Rtopm
            ZM2 = ZM1 + self.H1 - H_top_arc

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

    # Inlined from Methods.Slot.SlotM13.build_geometry
    def build_geometry(self):
        """Compute the curve (Line) needed to plot the Slot.
        The ending point of a curve is the starting point of the next curve in
        the list

        Parameters
        ----------
        self : SlotM13
            A SlotM13 object

        Returns
        -------
        curve_list: list
            A list of 3 Segments

        """
        point_dict = self._comp_point_coordinate()
        Z1 = point_dict["Z1"]
        Z2 = point_dict["Z2"]
        Z3 = point_dict["Z3"]
        Z4 = point_dict["Z4"]

        # Creation of curve
        curve_list = []
        if self.H0 > 0:
            curve_list.append(Segment(Z1, Z2))
        curve_list.append(Segment(Z2, Z3))
        if self.H0 > 0:
            curve_list.append(Segment(Z3, Z4))

        return curve_list

    # Inlined from Methods.Slot.SlotM13.check
    def check(self):
        """Check that the SlotM13 object is correct

        Parameters
        ----------
        self : SlotM13
            A SlotM13 object

        Returns
        -------
        None
        """
        if self.W0 < self.W1:
            raise SlotCheckError("You must have W1 <= W0")
        if 2 * self.Rtopm < self.W1:
            raise SlotCheckError("You must have W1 <= 2*Rtopm")

    # Inlined from Methods.Slot.SlotM13.comp_angle_opening
    def comp_angle_opening(self):
        """Compute the average opening angle of the Slot

        Parameters
        ----------
        self : SlotM13
            A SlotM13 object

        Returns
        -------
        alpha: float
            Average opening angle of the slot [rad]

        """

        Rbo = self.get_Rbo()

        return float(2 * np.arcsin(self.W0 / (2 * Rbo)))

    # Inlined from Methods.Slot.SlotM13.comp_height
    def comp_height(self):
        """Compute the height of the Slot.
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotM13
            A SlotM13 object

        Returns
        -------
        Htot: float
            Height of the slot [m]

        """

        point_dict = self._comp_point_coordinate()
        Z2 = point_dict["Z2"]
        Z3 = point_dict["Z3"]

        Rbo = self.get_Rbo()

        if self.is_outwards():
            return abs(Z2) - Rbo
        else:
            return Rbo - abs((Z2 + Z3) / 2)

    # Inlined from Methods.Slot.SlotM13.comp_height_active
    def comp_height_active(self):
        """Compute the height of the active area

        Parameters
        ----------
        self : SlotM13
            A SlotM13 object

        Returns
        -------
        Hwind: float
            Height of the active area [m]

        """

        point_dict = self._comp_point_coordinate()
        ZM0 = point_dict["ZM0"]
        ZM1 = point_dict["ZM1"]
        ZM2 = point_dict["ZM2"]
        ZM3 = point_dict["ZM3"]
        ZM4 = point_dict["ZM4"]

        if self.is_outwards():
            R1 = np.abs(ZM0)
            R2 = np.abs(ZM1)
            return R2 - R1
        else:
            return self.H1

    # Inlined from Methods.Slot.SlotM13.comp_surface
    def comp_surface(self):
        """Compute the Slot total surface (by analytical computation).
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotM13
            A SlotM13 object

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

    # Inlined from Methods.Slot.SlotM13.comp_surface_active
    def comp_surface_active(self):
        """Compute the Slot active inner surface (by analytical computation)

        Parameters
        ----------
        self : SlotM13
            A SlotM13 object

        Returns
        -------
        Swind: float
            Slot active inner surface [m**2]

        """

        point_dict = self._comp_point_coordinate()
        ZM1 = point_dict["ZM1"]
        ZM2 = point_dict["ZM2"]
        alpha = 2 * float(np.arcsin(self.W1 / (2 * self.Rtopm)))
        Sarc = (self.Rtopm**2.0) / 2.0 * (alpha - np.sin(alpha))

        S1 = abs(ZM1 - ZM2) * self.W1
        return S1 + Sarc

    # Inlined from Methods.Slot.SlotM13.get_surface_active
    def get_surface_active(self, alpha=0, delta=0):
        """Return the full active surface

        Parameters
        ----------
        self : SlotM13
            A SlotM13 object
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
        Z1 = point_dict["Z1"]
        Z4 = point_dict["Z4"]

        curve_list = []
        # Case Z2-Z1 overlapping with ZM1-ZM2
        if self.H0 != 0 and self.H0 < self.H1 and self.W0 == self.W1:
            curve_list.append(Segment(ZM1, Z1))
            curve_list.append(Segment(Z1, ZM2))
        else:
            curve_list.append(Segment(ZM1, ZM2))

        if self.is_outwards():
            curve_list.append(Arc1(ZM2, ZM3, -self.Rtopm, is_trigo_direction=False))
        else:
            curve_list.append(Arc1(ZM2, ZM3, self.Rtopm))

        # Case Z3-Z4 overlapping with ZM3-ZM4
        if self.H0 != 0 and self.H0 < self.H1 and self.W0 == self.W1:
            curve_list.append(Segment(ZM3, Z4))
            curve_list.append(Segment(Z4, ZM4))
        else:
            curve_list.append(Segment(ZM3, ZM4))

        curve_list.append(Segment(ZM4, ZM1))

        Zmid = (ZM1 + ZM3) / 2

        surface = SurfLine(
            line_list=curve_list, label="Wind_" + st + "_R0_T0_S0", point_ref=Zmid
        )

        # Apply transformation
        surface.rotate(alpha)
        surface.translate(delta)

        return surface

    # Inlined from Methods.Slot.SlotM13.is_airgap_active
    def is_airgap_active(self):
        """Return True if a part or the full active surface is in the airgap

        Parameters
        ----------
        self : SlotM13
            A SlotM13 object

        Returns
        -------
        is_airgap_active : bool
            True if a part or the full active surface is in the airgap
        """

        return self.comp_height_active() > self.H0

    # Inlined from Methods.Slot.SlotM13.plot_schematics
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
        self : SlotM13
            A SlotM13 object
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
            slot = type(self)(Zs=4, W0=0.05, H0=0.02, H1=0.02, W1=0.04, Rtopm=0.04)
            lam = LamSlot(
                Rint=0.1, Rext=0.135, is_internal=True, is_stator=False, slot=slot
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
                line = Segment(point_dict["Z3"], point_dict["Z2"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="W0",
                    offset_label=-1 * sign * self.H1 * 0.1 + 1j * self.H1 * 0.2,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # W1
                plot_quote(
                    Z1=point_dict["ZM2"],
                    Zlim1=point_dict["ZM2"] - sign * 0.5 * self.H1,
                    Zlim2=point_dict["ZM3"] - sign * 0.5 * self.H1,
                    Z2=point_dict["ZM3"],
                    offset_label=0.25 * self.H1,
                    fig=fig,
                    ax=ax,
                    label="W1",
                )
                # H0
                line = Segment(point_dict["Z1"], point_dict["Z2"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="H0",
                    offset_label=1j * -0.1 * self.W0,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # H1
                Zlim1 = point_dict["ZM4"] - 1j * sign * 0.3 * self.H1
                plot_quote(
                    Z1=point_dict["ZM4"],
                    Zlim1=Zlim1,
                    Zlim2=point_dict["ZM0"].real + 1j * Zlim1.imag,
                    Z2=point_dict["ZM0"],
                    offset_label=1j * 0.1 * self.W1,
                    fig=fig,
                    ax=ax,
                    label="H1",
                )
                # Rtopm
                line = Segment(point_dict["Zc"], point_dict["ZM0"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="Rtopm",
                    offset_label=sign * self.Rtopm * 0.4 + 1j * 0.1 * self.W1,
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
                line = Segment(point_dict["Zc"], point_dict["ZM2"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                line = Segment(point_dict["Zc"], point_dict["ZM3"])
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
            W = self.W0 / 2 * 1.4
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
