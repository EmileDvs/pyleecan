# Experimental dataclass generated from Generator/ClassesRef/Slot/SlotM17.csv
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
    SC_FONT_SIZE,
)
from ._error import ParentMissingError, SlotCheckError
from .arc_1 import Arc1
from .lam_slot import LamSlot
from .segment import Segment
from .slot import Slot
from .surf_line import SurfLine


@dataclass(eq=False)
class SlotM17(Slot):
    """Full rotor magnet

    Attributes
    ----------
    """

    IS_SYMMETRICAL: ClassVar = 1
    MAGNET_COLOR = config_dict["PLOT"]["COLOR_DICT"]["MAGNET_COLOR"]

    # Inlined from Methods.Slot.SlotM17.build_geometry
    def build_geometry(self):
        """Compute the curve (Line) needed to plot the Slot.
        The ending point of a curve is the starting point of the next curve in
        the list

        Parameters
        ----------
        self : SlotM17
            A SlotM17 object

        Returns
        -------
        curve_list: list
            Empty list (no lamination, only active surface)

        """

        return []

    # Inlined from Methods.Slot.SlotM17.check
    def check(self):
        """Check that the SlotM17 object is correct

        Parameters
        ----------
        self : SlotM17
            A SlotM17 object

        Returns
        -------
        None
        """
        if self.parent is None:
            raise SlotCheckError("SlotM17 must be inside a lamination")
        if self.Zs != 2:
            raise SlotCheckError("SlotM17 must have p=1")
        if not self.parent.is_internal:
            raise SlotCheckError("SlotM17 must be inside an internal lamination")

    # Inlined from Methods.Slot.SlotM17.comp_angle_opening
    def comp_angle_opening(self):
        """Compute the average opening angle of the Slot

        Parameters
        ----------
        self : SlotM17
            A SlotM17 object

        Returns
        -------
        alpha: float
            Average opening angle of the slot [rad]

        """

        return np.pi

    # Inlined from Methods.Slot.SlotM17.comp_height
    def comp_height(self):
        """Compute the height of the Slot.
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotM17
            A SlotM17 object

        Returns
        -------
        Htot: float
            Height of the slot [m]

        """

        return self.parent.Rext - self.parent.Rint

    # Inlined from Methods.Slot.SlotM17.comp_height_active
    def comp_height_active(self):
        """Compute the height of the active area

        Parameters
        ----------
        self : SlotM17
            A SlotM17 object

        Returns
        -------
        Hwind: float
            Height of the active area [m]

        """

        return self.parent.Rext - self.parent.Rint

    # Inlined from Methods.Slot.SlotM17.comp_surface
    def comp_surface(self):
        """Compute the Slot total surface (by analytical computation).
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotM17
            A SlotM17 object

        Returns
        -------
        S: float
            Slot total surface [m**2]

        """

        return np.pi / 2 * (self.parent.Rext**2 - self.parent.Rint**2)

    # Inlined from Methods.Slot.SlotM17.comp_surface_active
    def comp_surface_active(self):
        """Compute the Slot inner active surface (by analytical computation)

        Parameters
        ----------
        self : SlotM17
            A SlotM17 object

        Returns
        -------
        Swind: float
            Slot inner active surface [m**2]

        """

        return np.pi / 2 * (self.parent.Rext**2 - self.parent.Rint**2)

    # Inlined from Methods.Slot.SlotM17.get_surface_active
    def get_surface_active(self, alpha=0, delta=0):
        """Return the full active surface

        Parameters
        ----------
        self : SlotM17
            A SlotM17 object
        alpha : float
            float number for rotation (Default value = 0) [rad]
        delta : complex
            complex number for translation (Default value = 0)

        Returns
        -------
        surf_act: Surface
            Surface corresponding to the Active Area
        """

        self.check()
        # get the name of the lamination
        st = self.get_name_lam()
        Rext = self.parent.Rext
        Rint = self.parent.Rint

        Z1 = -Rext * 1j
        Z2 = Rext
        Z3 = Rext * 1j
        curve_list = []
        curve_list.append(Arc1(begin=Z1, end=Z2, radius=Rext, is_trigo_direction=True))
        curve_list.append(Arc1(begin=Z2, end=Z3, radius=Rext, is_trigo_direction=True))
        if Rint == 0:
            curve_list.append(Segment(begin=Z3, end=Z1))
        else:
            Z4 = Rint * 1j
            Z5 = Rint
            Z6 = -Rint * 1j
            curve_list.append(Segment(begin=Z3, end=Z4))
            curve_list.append(
                Arc1(begin=Z4, end=Z5, radius=-Rint, is_trigo_direction=False)
            )
            curve_list.append(
                Arc1(begin=Z5, end=Z6, radius=-Rint, is_trigo_direction=False)
            )
            curve_list.append(Segment(begin=Z6, end=Z1))

        surface = SurfLine(
            line_list=curve_list,
            label="Wind_" + st + "_R0_T0_S0",
            point_ref=Rint + (Rext - Rint) / 2,
        )

        # Apply transformation
        surface.rotate(alpha)
        surface.translate(delta)

        return surface

    # Inlined from Methods.Slot.SlotM17.is_airgap_active
    def is_airgap_active(self):
        """Return True if a part or the full active surface is in the airgap

        Parameters
        ----------
        self : SlotM17
            A SlotM17 object

        Returns
        -------
        is_airgap_active : bool
            True if a part or the full active surface is in the airgap
        """

        return True

    # Inlined from Methods.Slot.SlotM17.is_full_pitch_active
    def is_full_pitch_active(self):
        """Returns True if the active surface angular width
        matches the slot pitch (like SlotM17 or SlotM18)
        (used to set Boundary conditions in FEMM airgap)

        Parameters
        ----------
        self : SlotM17
            A SlotM17 object

        Returns
        -------
        is_full_pitch_active : bool
            True if the active surface angular width matches the slot pitch
        """

        return True

    # Inlined from Methods.Slot.SlotM17.plot_schematics
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
        self : SlotM17
            A SlotM17 object
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
            slot = type(self)(Zs=2)
            lam = LamSlot(
                Rint=0.05, Rext=0.135, is_internal=True, is_stator=False, slot=slot
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

            # Adding schematics
            if is_add_schematics:
                # Rext
                line = Segment(begin=0, end=lam.Rext * np.exp(1j * np.pi / 4))
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="Rext",
                    offset_label=0.2 * lam.Rext,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # Rint
                line = Segment(begin=0, end=lam.Rint * np.exp(1j * 7 * np.pi / 4))
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="Rint",
                    offset_label=0.2 * lam.Rint,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )

            if is_add_main_line:
                # Ox axis
                line = Segment(begin=-lam.Rext * 2.5, end=lam.Rext * 2.5)
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
            W = lam.Rext * 1.1

            ax.axis("equal")
            ax.set_xlim(-W, W)
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
