# Experimental dataclass generated from Generator/ClassesRef/Slot/SlotM18.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass
from typing import ClassVar

import matplotlib.pyplot as plt
import numpy as np

from ..definitions import config_dict
from ..Functions.labels import COND_BOUNDARY_PROP_LAB, YOKE_LAB, YSML_LAB, YSMR_LAB
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
from ._error import ParentMissingError
from .arc_1 import Arc1
from .lam_slot import LamSlot
from .segment import Segment
from .slot import Slot
from .surf_line import SurfLine


@dataclass(eq=False)
class SlotM18(Slot):
    """Polar Ring magnet

    Attributes
    ----------
    H0 : float
        Magnet Height
        Unit: m; Default: 0.001; Minimum: 0
    """

    IS_SYMMETRICAL: ClassVar = 1
    MAGNET_COLOR = config_dict["PLOT"]["COLOR_DICT"]["MAGNET_COLOR"]
    H0: float = 0.001
    """Magnet Height"""

    # Inlined from Methods.Slot.SlotM18._comp_point_coordinate
    def _comp_point_coordinate(self):
        """Compute the point coordinates needed to plot the Slot.

        Parameters
        ----------
        self : SlotM18
            A SlotM18 object

        Returns
        -------
        point_dict: dict
            A dict of the slot coordinates
        """

        Rbo = self.get_Rbo()

        sp = 2 * np.pi / self.Zs
        Z1 = Rbo * np.exp(-1j * sp / 2)
        ZM1 = Rbo * np.exp(-1j * sp / 2)

        if self.is_outwards():
            ZM2 = (Rbo - self.H0) * np.exp(-1j * sp / 2)
        else:  # inward slot
            ZM2 = (Rbo + self.H0) * np.exp(-1j * sp / 2)

        point_dict = {}
        point_dict["Z1"] = Z1
        point_dict["ZM1"] = ZM1
        point_dict["ZM2"] = ZM2
        # symetry
        point_dict["Z2"] = Z1.conjugate()
        point_dict["ZM3"] = ZM2.conjugate()
        point_dict["ZM4"] = ZM1.conjugate()

        return point_dict

    # Inlined from Methods.Slot.SlotM18.build_geometry
    def build_geometry(self):
        """Compute the curve (Line) needed to plot the Slot.
        The ending point of a curve is the starting point of the next curve in
        the list

        Parameters
        ----------
        self : SlotM18
            A SlotM18 object

        Returns
        -------
        curve_list: list
            A list of 3 Segments

        """
        Rbo = self.get_Rbo()
        point_dict = self._comp_point_coordinate()
        Z1 = point_dict["Z1"]
        Z2 = point_dict["Z2"]

        # Creation of curve
        curve_list = []
        curve_list.append(Arc1(Z1, Z2, Rbo, is_trigo_direction=True))

        return curve_list

    # Inlined from Methods.Slot.SlotM18.check
    def check(self):
        """Check that the SlotM18 object is correct

        Parameters
        ----------
        self : SlotM18
            A SlotM18 object

        Returns
        -------
        None
        """
        pass

    # Inlined from Methods.Slot.SlotM18.comp_angle_opening
    def comp_angle_opening(self):
        """Compute the average opening angle of the Slot

        Parameters
        ----------
        self : SlotM18
            A SlotM18 object

        Returns
        -------
        alpha: float
            Average opening angle of the slot [rad]

        """

        return 2 * np.pi / self.Zs

    # Inlined from Methods.Slot.SlotM18.comp_height
    def comp_height(self):
        """Compute the height of the Slot.
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotM18
            A SlotM18 object

        Returns
        -------
        Htot: float
            Height of the slot [m]

        """

        return 0

    # Inlined from Methods.Slot.SlotM18.comp_height_active
    def comp_height_active(self):
        """Compute the height of the active area

        Parameters
        ----------
        self : SlotM18
            A SlotM18 object

        Returns
        -------
        Hwind: float
            Height of the active area [m]

        """

        return self.H0

    # Inlined from Methods.Slot.SlotM18.comp_surface
    def comp_surface(self):
        """Compute the Slot total surface (by analytical computation).
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotM18
            A SlotM18 object

        Returns
        -------
        S: float
            Slot total surface [m**2]

        """

        return 0

    # Inlined from Methods.Slot.SlotM18.comp_surface_active
    def comp_surface_active(self):
        """Compute the Slot inner active surface (by analytical computation)

        Parameters
        ----------
        self : SlotM18
            A SlotM18 object

        Returns
        -------
        Swind: float
            Slot inner active surface [m**2]

        """

        point_dict = self._comp_point_coordinate()
        ZM1 = point_dict["ZM1"]
        ZM2 = point_dict["ZM2"]

        R1 = abs(ZM1)
        R2 = abs(ZM2)

        S1 = np.pi * R1**2 / self.Zs
        S2 = np.pi * R2**2 / self.Zs

        return abs(S1 - S2)

    # Inlined from Methods.Slot.SlotM18.get_surface_active
    def get_surface_active(self, alpha=0, delta=0):
        """Return the full active surface

        Parameters
        ----------
        self : SlotM18
            A SlotM18 object
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
        Rbo = self.get_Rbo()

        point_dict = self._comp_point_coordinate()
        ZM1 = point_dict["ZM1"]
        ZM2 = point_dict["ZM2"]
        ZM3 = point_dict["ZM3"]
        ZM4 = point_dict["ZM4"]

        curve_list = []
        curve_list.append(
            Segment(ZM1, ZM2, prop_dict={COND_BOUNDARY_PROP_LAB: YSMR_LAB})
        )

        if self.is_outwards():
            curve_list.append(Arc1(ZM2, ZM3, (Rbo - self.H0), is_trigo_direction=True))
        else:
            curve_list.append(Arc1(ZM2, ZM3, (Rbo + self.H0), is_trigo_direction=True))

        curve_list.append(
            Segment(ZM3, ZM4, prop_dict={COND_BOUNDARY_PROP_LAB: YSML_LAB})
        )

        if self.is_outwards():
            curve_list.append(Arc1(ZM4, ZM1, -Rbo, is_trigo_direction=False))
        else:
            curve_list.append(Arc1(ZM4, ZM1, -Rbo, is_trigo_direction=False))
        # If no lamination, BC is required on bore
        curve_list[-1].prop_dict = {COND_BOUNDARY_PROP_LAB: YOKE_LAB}

        Zmid = (abs(ZM1) + abs(ZM3)) / 2

        surface = SurfLine(
            line_list=curve_list, label="Wind_" + st + "_R0_T0_S0", point_ref=Zmid
        )

        # Apply transformation
        surface.rotate(alpha)
        surface.translate(delta)

        return surface

    # Inlined from Methods.Slot.SlotM18.is_airgap_active
    def is_airgap_active(self):
        """Return True if a part or the full active surface is in the airgap

        Parameters
        ----------
        self : SlotM18
            A SlotM18 object

        Returns
        -------
        is_airgap_active : bool
            True if a part or the full active surface is in the airgap
        """

        return True

    # Inlined from Methods.Slot.SlotM18.is_full_pitch_active
    def is_full_pitch_active(self):
        """Returns True if the active surface angular width
        matches the slot pitch (like SlotM17 or SlotM18)
        (used to set Boundary conditions in FEMM airgap)

        Parameters
        ----------
        self : SlotM18
            A SlotM18 object

        Returns
        -------
        is_full_pitch_active : bool
            True if the active surface angular width matches the slot pitch
        """

        return True

    # Inlined from Methods.Slot.SlotM18.plot_schematics
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
        self : SlotM18
            A SlotM18 object
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
            slot = type(self)(Zs=16, H0=15e-3)
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
                # H0
                line = Segment(point_dict["ZM3"], point_dict["ZM4"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="H0",
                    offset_label=1j * self.H0 * 0.7,
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
                # Magnet separation lines
                for ii in range(self.Zs):
                    line = Segment(
                        point_dict["ZM1"] * np.exp(1j * 2 * np.pi / self.Zs * ii),
                        point_dict["ZM2"] * np.exp(1j * 2 * np.pi / self.Zs * ii),
                    )
                    line.plot(
                        fig=fig,
                        ax=ax,
                        color="k",
                        linestyle="-",
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
            W = point_dict["ZM3"].imag * 3
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
