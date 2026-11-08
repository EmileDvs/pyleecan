# Experimental dataclass generated from Generator/ClassesRef/Slot/SlotM11.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass
from typing import ClassVar

import matplotlib.pyplot as plt
import numpy as np

from ..definitions import config_dict
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
from . import ParentMissingError
from .arc_1 import Arc1
from .lam_slot import LamSlot
from .segment import Segment
from .slot import Slot
from .surf_line import SurfLine


@dataclass(eq=False)
class SlotM11(Slot):
    """Polar Slot with Polar magnet

    Attributes
    ----------
    W0 : float
        Slot isthmus angular width.
        Unit: rad; Default: 0; Minimum: 0
    H0 : float
        Slot isthmus height.
        Unit: m; Default: 0; Minimum: 0
    W1 : float
        Magnet angular width
        Unit: rad; Default: 0; Minimum: 0
    H1 : float
        Magnet Height
        Unit: m; Default: 0; Minimum: 0
    """

    IS_SYMMETRICAL: ClassVar = 1
    MAGNET_COLOR = config_dict["PLOT"]["COLOR_DICT"]["MAGNET_COLOR"]
    KEY_COLOR = config_dict["PLOT"]["COLOR_DICT"]["KEY_COLOR"]
    W0: float = 0
    """Slot isthmus angular width."""
    H0: float = 0
    """Slot isthmus height."""
    W1: float = 0
    """Magnet angular width"""
    H1: float = 0
    """Magnet Height"""

    # Inlined from Methods.Slot.SlotM11._comp_point_coordinate
    def _comp_point_coordinate(self):
        """Compute the point coordinates needed to plot the Slot.

        Parameters
        ----------
        self : SlotM11
            A SlotM11 object

        Returns
        -------
        point_dict: dict
            A dict of the slot coordinates
        """

        Rbo = self.get_Rbo()

        Z1 = Rbo * np.exp(-1j * self.W0 / 2)

        if self.is_outwards():
            Z2 = (Rbo + self.H0) * np.exp(-1j * self.W0 / 2)
            ZM1 = (Rbo + self.H0) * np.exp(-1j * self.W1 / 2)
            ZM2 = (Rbo + self.H0 - self.H1) * np.exp(-1j * self.W1 / 2)
        else:  # inward slot
            Z2 = (Rbo - self.H0) * np.exp(-1j * self.W0 / 2)
            ZM1 = (Rbo - self.H0) * np.exp(-1j * self.W1 / 2)
            ZM2 = (Rbo - self.H0 + self.H1) * np.exp(-1j * self.W1 / 2)

        point_dict = {}
        point_dict["Z1"] = Z1
        point_dict["Z2"] = Z2
        point_dict["ZM1"] = ZM1
        point_dict["ZM2"] = ZM2
        # symetry

        point_dict["Z3"] = Z2.conjugate()
        point_dict["Z4"] = Z1.conjugate()
        point_dict["ZM3"] = ZM2.conjugate()
        point_dict["ZM4"] = ZM1.conjugate()

        return point_dict

    # Inlined from Methods.Slot.SlotM11.build_geometry
    def build_geometry(self):
        """Compute the curve (Line) needed to plot the Slot.
        The ending point of a curve is the starting point of the next curve in
        the list

        Parameters
        ----------
        self : SlotM11
            A SlotM11 object

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
            curve_list.append(Segment(Z1, Z2))
        if self.is_outwards():
            curve_list.append(Arc1(Z2, Z3, Rbo + self.H0, is_trigo_direction=True))
        else:
            curve_list.append(Arc1(Z2, Z3, Rbo - self.H0, is_trigo_direction=True))
        if self.H0 > 0:
            curve_list.append(Segment(Z3, Z4))

        return curve_list

    # Inlined from Methods.Slot.SlotM11.check
    def check(self):
        """Check that the SlotM11 object is correct

        Parameters
        ----------
        self : SlotM11
            A SlotM11 object

        Returns
        -------
        None
        """
        # percentage of the slot pitch that W0 and W1 should not exceed
        slot_pitch_tol = 0.99

        if self.W1 is not None and self.W0 < self.W1:
            raise SlotCheckError("You must have W1 <= W0")
        if self.W1 is not None and self.W1 >= slot_pitch_tol * 2 * np.pi / self.Zs:
            raise SlotCheckError("You must have W1 < pi/p (use ring magnet instead)")
        if self.W0 >= slot_pitch_tol * 2 * np.pi / self.Zs:
            raise SlotCheckError("You must have W0 < pi/p")

    # Inlined from Methods.Slot.SlotM11.comp_angle_opening
    def comp_angle_opening(self):
        """Compute the average opening angle of the Slot

        Parameters
        ----------
        self : SlotM11
            A SlotM11 object

        Returns
        -------
        alpha: float
            Average opening angle of the slot [rad]

        """

        return self.W0

    # Inlined from Methods.Slot.SlotM11.comp_height
    def comp_height(self):
        """Compute the height of the Slot.
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotM11
            A SlotM11 object

        Returns
        -------
        Htot: float
            Height of the slot [m]

        """

        return self.H0

    # Inlined from Methods.Slot.SlotM11.comp_height_active
    def comp_height_active(self):
        """Compute the height of the active area

        Parameters
        ----------
        self : SlotM11
            A SlotM11 object

        Returns
        -------
        Hwind: float
            Height of the active area [m]

        """

        return self.H1

    # Inlined from Methods.Slot.SlotM11.comp_surface
    def comp_surface(self):
        """Compute the Slot total surface (by analytical computation).
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotM11
            A SlotM11 object

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

    # Inlined from Methods.Slot.SlotM11.comp_surface_active
    def comp_surface_active(self):
        """Compute the Slot inner active surface (by analytical computation)

        Parameters
        ----------
        self : SlotM11
            A SlotM11 object

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

        S1 = np.pi * R1**2 * (self.W1 / (2 * np.pi))
        S2 = np.pi * R2**2 * (self.W1 / (2 * np.pi))

        return abs(S1 - S2)

    # Inlined from Methods.Slot.SlotM11.get_surface_active
    def get_surface_active(self, alpha=0, delta=0):
        """Return the full active surface

        Parameters
        ----------
        self : SlotM11
            A SlotM11 object
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
            curve_list.append(
                Arc1(ZM2, ZM3, (Rbo + self.H0 - self.H1), is_trigo_direction=True)
            )
        else:
            curve_list.append(
                Arc1(ZM2, ZM3, (Rbo - self.H0 + self.H1), is_trigo_direction=True)
            )

        # Case Z3-Z4 overlapping with ZM3-ZM4
        if self.H0 != 0 and self.H0 < self.H1 and self.W0 == self.W1:
            curve_list.append(Segment(ZM3, Z4))
            curve_list.append(Segment(Z4, ZM4))
        else:
            curve_list.append(Segment(ZM3, ZM4))

        if self.is_outwards():
            curve_list.append(Arc1(ZM4, ZM1, -Rbo - self.H0, is_trigo_direction=False))
        else:
            curve_list.append(Arc1(ZM4, ZM1, -Rbo + self.H0, is_trigo_direction=False))

        Zmid = (abs(ZM1) + abs(ZM3)) / 2

        surface = SurfLine(
            line_list=curve_list, label="Wind_" + st + "_R0_T0_S0", point_ref=Zmid
        )

        # Apply transformation
        surface.rotate(alpha)
        surface.translate(delta)

        return surface

    # Inlined from Methods.Slot.SlotM11.is_airgap_active
    def is_airgap_active(self):
        """Return True if a part or the full active surface is in the airgap

        Parameters
        ----------
        self : SlotM11
            A SlotM11 object

        Returns
        -------
        is_airgap_active : bool
            True if a part or the full active surface is in the airgap
        """

        return self.H1 > self.H0

    # Inlined from Methods.Slot.SlotM11.is_full_pitch_active
    def is_full_pitch_active(self):
        """Returns True if the active surface angular width
        matches the slot pitch (like SlotM17 or SlotM18)
        (used to set Boundary conditions in FEMM airgap)

        Parameters
        ----------
        self : SlotM11
            A SlotM11 object

        Returns
        -------
        is_full_pitch_active : bool
            True if the active surface angular width matches the slot pitch
        """

        return self.W1 == 2 * np.pi / self.Zs

    # Inlined from Methods.Slot.SlotM11.plot_schematics
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
        self : SlotM11
            A SlotM11 object
        is_default : int
            0: current slot values, 1: default internal rotor schematics, 2: default external stator schematics
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
                Zs=8, H0=20e-3, W0=np.pi / 8, H1=15e-3, W1=np.pi / 8 * 0.75
            )
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
                    offset_label=sign * self.H0 * 0.3,
                    fontsize=SC_FONT_SIZE,
                )
                # H0
                line = Segment(point_dict["Z1"], point_dict["Z2"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="H0",
                    offset_label=1j * point_dict["Z4"].imag * 0.1,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )

                if type_add_active != 0:
                    # W1
                    R = self.get_Rbo() + sign * (self.H0 - self.H1 * 1.1)
                    line = Arc1(
                        begin=R * np.exp(-1j * self.W1 / 2),
                        end=R * np.exp(1j * self.W1 / 2),
                        radius=R,
                        is_trigo_direction=True,
                    )
                    line.plot(
                        fig=fig,
                        ax=ax,
                        color=ARROW_COLOR,
                        linewidth=ARROW_WIDTH,
                        label="W1",
                        offset_label=-1 * sign * self.H0 * 0.3,
                        fontsize=SC_FONT_SIZE,
                    )
                    # H1
                    line = Segment(point_dict["ZM3"], point_dict["ZM4"])
                    line.plot(
                        fig=fig,
                        ax=ax,
                        color=ARROW_COLOR,
                        linewidth=ARROW_WIDTH,
                        label="H1",
                        offset_label=1j * point_dict["Z4"].imag * 0.2,
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
                # Z1 Line
                line = Segment(0, Rbo * 2 * np.exp(-1j * self.W0 / 2))
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # Z2 Line
                line = Segment(0, Rbo * 2 * np.exp(1j * self.W0 / 2))
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                if type_add_active != 0:
                    # ZM1 Line
                    line = Segment(0, Rbo * 2 * np.exp(-1j * self.W1 / 2))
                    line.plot(
                        fig=fig,
                        ax=ax,
                        color=MAIN_LINE_COLOR,
                        linestyle=MAIN_LINE_STYLE,
                        linewidth=MAIN_LINE_WIDTH,
                    )
                    # ZM2 Line
                    line = Segment(0, Rbo * 2 * np.exp(1j * self.W1 / 2))
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

            if type_add_active == 1:
                self.plot_active(fig=fig, ax=ax, is_show_fig=False)
            elif type_add_active == 2:
                self.plot_active(
                    fig=fig,
                    ax=ax,
                    is_show_fig=False,
                    enforced_default_color=self.MAGNET_COLOR,
                )
            elif type_add_active == 5:
                self.plot_active(
                    fig=fig,
                    ax=ax,
                    is_show_fig=False,
                    enforced_default_color=self.KEY_COLOR,
                )

            # Zooming and cleaning
            if self.is_outwards():
                W = point_dict["Z4"].imag * 1.4
            else:
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

    class MachineCheckError(Exception):
        """ """

    class LaminationCheckError(MachineCheckError):
        """ """

    class SlotCheckError(LaminationCheckError):
        """ """


MachineCheckError = SlotM11.MachineCheckError
LaminationCheckError = SlotM11.LaminationCheckError
SlotCheckError = SlotM11.SlotCheckError
