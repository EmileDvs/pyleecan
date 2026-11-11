# Experimental dataclass generated from Generator/ClassesRef/Slot/SlotM19.csv
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
from ._error import ParentMissingError
from .arc_1 import Arc1
from .lam_slot import LamSlot
from .segment import Segment
from .slot import Slot
from .surf_line import SurfLine


@dataclass(eq=False)
class SlotM19(Slot):
    """trapezoidal  Slot with trapezoidal magnet with polar top

    Attributes
    ----------
    W0 : float
        Slot/magnet width. (top)
        Unit: m; Default: 0; Minimum: 0
    W1 : float
        Slot/magnet width. (bottom)
        Unit: m; Default: 0; Minimum: 0
    H0 : float
        Magnet Height
        Unit: m; Default: 0; Minimum: 0
    """

    IS_SYMMETRICAL: ClassVar = 1
    MAGNET_COLOR = config_dict["PLOT"]["COLOR_DICT"]["MAGNET_COLOR"]
    W0: float = 0
    """Slot/magnet width. (top)"""
    W1: float = 0
    """Slot/magnet width. (bottom)"""
    H0: float = 0
    """Magnet Height"""

    # Inlined from Methods.Slot.SlotM19._comp_point_coordinate
    def _comp_point_coordinate(self):
        """Compute the point coordinates needed to plot the Slot.

        Parameters
        ----------
        self : SlotM19
            A SlotM19 object

        Returns
        -------
        point_dict: dict
            A dict of the slot coordinates
        """

        Rbo = self.get_Rbo()

        # alpha is the angle to rotate Z0 so ||Z1,Z4|| = W1
        alpha = float(np.arcsin(self.W1 / (2 * Rbo)))

        Z1 = Rbo * np.exp(-1j * alpha)

        if self.is_outwards():
            Zmid = Rbo + self.H0

        else:  # inward slot
            Zmid = Rbo - self.H0

        Z2 = Zmid - 1j * (self.W0 / 2)

        point_dict = {}
        point_dict["Z1"] = Z1
        point_dict["Z2"] = Z2
        point_dict["Zmid"] = Zmid
        # symetry
        point_dict["Z3"] = Z2.conjugate()
        point_dict["Z4"] = Z1.conjugate()

        return point_dict

    # Inlined from Methods.Slot.SlotM19.build_geometry
    def build_geometry(self):
        """Compute the curve (Line) needed to plot the Slot.
        The ending point of a curve is the starting point of the next curve in
        the list

        Parameters
        ----------
        self : SlotM19
            A SlotM19 object

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

    # Inlined from Methods.Slot.SlotM19.check
    def check(self):
        """
        Check that the SlotM19 object is correct

        Parameters
        ----------
        self : SlotM19
            A SlotM19 object

        Returns
        -------

        """
        pass

    # Inlined from Methods.Slot.SlotM19.comp_angle_opening
    def comp_angle_opening(self):
        """Compute the average opening angle of the Slot

        Parameters
        ----------
        self : SlotM19
            A SlotM19 object

        Returns
        -------
        alpha: float
            Average opening angle of the slot [rad]

        """

        Rbo = self.get_Rbo()

        return float(2 * np.arcsin(self.W1 / (2 * Rbo)))

    # Inlined from Methods.Slot.SlotM19.comp_height
    def comp_height(self):
        """Compute the height of the Slot.
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotM19
            A SlotM19 object

        Returns
        -------
        Htot: float
            Height of the slot [m]

        """

        point_dict = self._comp_point_coordinate()
        Zmid = point_dict["Zmid"]
        Z1 = point_dict["Z1"]
        Z2 = point_dict["Z2"]
        Z3 = point_dict["Z3"]
        Z4 = point_dict["Z4"]

        Rbo = self.get_Rbo()

        if self.is_outwards():
            return np.abs(np.sqrt(Z2.real**2 + Z2.imag**2)) - np.abs(Rbo)

        else:
            return self.H0

    # Inlined from Methods.Slot.SlotM19.comp_height_active
    def comp_height_active(self):
        """Compute the height of the active area

        Parameters
        ----------
        self : SlotM19
            A SlotM19 object

        Returns
        -------
        Hwind: float
            Height of the active area [m]

        """
        return self.comp_height()

    # Inlined from Methods.Slot.SlotM19.comp_surface
    def comp_surface(self):
        """Compute the Slot total surface (by analytical computation).
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotM19
            A SlotM19 object

        Returns
        -------
        S: float
            Slot total surface [m**2]

        """

        Rbo = self.get_Rbo()
        point_dict = self._comp_point_coordinate()
        Z1 = point_dict["Z1"]
        Z2 = point_dict["Z2"]

        # The bottom is an arc
        alpha = self.comp_angle_opening()
        Sarc = (Rbo**2.0) / 2.0 * (alpha - np.sin(alpha))

        S1 = abs(Z1.real - Z2.real) * (self.W1 + self.W0) / 2

        if self.is_outwards():
            return S1 - Sarc
        else:
            return S1 + Sarc

    # Inlined from Methods.Slot.SlotM19.comp_surface_active
    def comp_surface_active(self):
        """Compute the Slot active inner surface (by analytical computation)

        Parameters
        ----------
        self : SlotM19
            A SlotM19 object

        Returns
        -------
        Swind: float
            Slot active inner surface [m**2]

        """
        return self.comp_surface()  # Magnet perfectly match the slot

    # Inlined from Methods.Slot.SlotM19.get_surface_active
    def get_surface_active(self, alpha=0, delta=0):
        """Return the full active surface

        Parameters
        ----------
        self : SlotM19
            A SlotM19 object
        alpha : float
            float number for rotation (Default value = 0) [rad]
        delta : complex
            complex number for translation (Default value = 0)

        Returns
        -------
        surf_act: Surface
            Surface corresponding to the Active Area
        """
        Rbo = self.get_Rbo()
        # get the name of the lamination
        st = self.get_name_lam()

        point_dict = self._comp_point_coordinate()
        Zmid = point_dict["Zmid"]
        Z1 = point_dict["Z1"]
        Z2 = point_dict["Z2"]
        Z3 = point_dict["Z3"]
        Z4 = point_dict["Z4"]

        curve_list = []
        curve_list.append(Segment(Z1, Z2))
        curve_list.append(Segment(Z2, Z3))
        curve_list.append(Segment(Z3, Z4))

        if self.is_outwards():
            curve_list.append(Arc1(Z4, Z1, -Rbo, is_trigo_direction=False))
        else:
            curve_list.append(Arc1(Z4, Z1, -Rbo, is_trigo_direction=False))

        surface = SurfLine(
            line_list=curve_list,
            label="Wind_" + st + "_R0_T0_S0",
            point_ref=(Z1 + Z3) / 2,
        )

        # Apply transformation
        if alpha != 0:
            surface.rotate(alpha)
        if delta != 0:
            surface.translate(delta)

        return surface

    # Inlined from Methods.Slot.SlotM19.plot_schematics
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
        self : SlotM19
            A SlotM19 object
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
            # definir paramètre par défault
            slot = type(self)(Zs=4, W0=30e-3, H0=17.5e-3, W1=20e-3)
            if is_default == 1:  # Internal Rotor schematics
                lam = LamSlot(
                    Rint=0.1, Rext=0.135, is_internal=True, is_stator=False, slot=slot
                )
                if is_return_default:
                    return lam

            else:  # External Stator schematics
                lam = LamSlot(
                    Rint=0.1, Rext=0.135, is_internal=False, is_stator=True, slot=slot
                )
                if is_return_default:
                    return lam

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
                    offset_label=sign * self.H0 * 0.4,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # W1
                plot_quote(
                    Z1=point_dict["Z1"],
                    Zlim1=point_dict["Z1"] - sign * 0.5 * self.H0,
                    Zlim2=point_dict["Z4"] - sign * 0.5 * self.H0,
                    Z2=point_dict["Z4"],
                    offset_label=0.25 * self.H0,
                    fig=fig,
                    ax=ax,
                    label="W1",
                )
                if lam.is_internal == False and lam.is_stator == True:
                    # Hkey
                    mid = point_dict["Zmid"]
                    line = Segment(mid, mid - sign * self.H0)
                    line.plot(
                        fig=fig,
                        ax=ax,
                        color=ARROW_COLOR,
                        linewidth=ARROW_WIDTH,
                        label="H0",
                        offset_label=1j * 0.1 * self.H0 - 0.0025,
                        is_arrow=True,
                        fontsize=SC_FONT_SIZE,
                    )

                # H0
                mid = point_dict["Zmid"]
                line = Segment(mid, mid - sign * self.H0)
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="H0",
                    offset_label=1j * 0.1 * self.H0 - 0.0025,
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
                # Magnet Arc
                line = Arc1(
                    begin=point_dict["Z1"],
                    end=point_dict["Z4"],
                    radius=abs(point_dict["Z1"]),
                    is_trigo_direction=True,
                )
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
