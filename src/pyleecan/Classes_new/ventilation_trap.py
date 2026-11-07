# Experimental dataclass generated from Generator/ClassesRef/Slot/VentilationTrap.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

import matplotlib.pyplot as plt
import numpy as np

from . import ParentMissingError
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
from .arc_1 import Arc1
from .hole import Hole
from .lam_hole import LamHole
from .segment import Segment
from .trapeze import Trapeze


@dataclass(eq=False)
class VentilationTrap(Hole):
    """Trapezoidal axial ventilation ducts

    Attributes
    ----------
    D0 : float
        Hole height
        Unit: m; Default: 1; Minimum: 0
    H0 : float
        Radius of the hole bottom
        Unit: m; Default: 1; Minimum: 0
    W1 : float
        Hole small basis
        Unit: m; Default: 1; Minimum: 0
    W2 : float
        Hole large basis
        Unit: m; Default: 1; Minimum: 0
    """

    D0: float = 1
    """Hole height"""
    H0: float = 1
    """Radius of the hole bottom"""
    W1: float = 1
    """Hole small basis"""
    W2: float = 1
    """Hole large basis"""

    # Inlined from Methods.Slot.VentilationTrap._comp_point_coordinate
    def _comp_point_coordinate(self):
        """Compute the point coordinates needed to plot the Hole.

        Parameters
        ----------
        self : VentilationPolar
            A VentilationPolar object

        Returns
        -------
        point_dict: dict
            A dict of the slot point coordinates
        """

        Z1 = (self.H0 - 1j * self.W1 / 2) * np.exp(1j * self.Alpha0)
        Z2 = (self.H0 + self.D0 - 1j * self.W2 / 2) * np.exp(1j * self.Alpha0)
        Z3 = (self.H0 + self.D0 + 1j * self.W2 / 2) * np.exp(1j * self.Alpha0)
        Z4 = (self.H0 + 1j * self.W1 / 2) * np.exp(1j * self.Alpha0)
        ZM1 = (Z1 + Z4) / 2
        ZM2 = (Z2 + Z3) / 2
        Zc = (self.H0 + (self.D0 / 2)) * np.exp(1j * self.Alpha0)

        point_dict = {}
        # symetry
        point_dict["Z1"] = Z1
        point_dict["Z2"] = Z2
        point_dict["Z3"] = Z3
        point_dict["Z4"] = Z4
        point_dict["Zc"] = Zc
        point_dict["ZM1"] = ZM1
        point_dict["ZM2"] = ZM2
        return point_dict

    # Inlined from Methods.Slot.VentilationTrap.build_geometry
    def build_geometry(self, alpha=0, delta=0):
        """Compute the curve needed to plot the ventilations

        Parameters
        ----------
        self : VentilationTrap
            A VentilationTrap object
        alpha : float
            Angle for rotation (Default value = 0) [rad]
        delta : complex
            Complex for translation (Default value = 0)

        Returns
        -------
        surf_list: list
            A list of Trapeze
        """

        lam_label = self.parent.get_label()
        R_id, surf_type = self.get_R_id()
        RTS_id = "R" + str(R_id) + "-T0-S0"
        vent_label = lam_label + "_" + surf_type + "_" + RTS_id

        # checking if the param have good type
        if type(alpha) not in [int, float]:
            raise TrapezeBuildGeometryError(
                "The parameter 'alpha' must be an int or float"
            )
        if type(delta) not in [complex, int, float]:
            raise TrapezeBuildGeometryError(
                "The parameter 'delta' must be a complex or float or int number"
            )

        surf_list = []
        # Modulo on Alpha for sym
        Alpha0 = self.Alpha0 % (2 * np.pi / self.Zh)
        Zc = (self.H0 + (self.D0 / 2)) * np.exp(1j * Alpha0)
        surf_list.append(
            Trapeze(
                point_ref=Zc,
                label=vent_label,
                height=self.D0,
                W1=self.W1,
                W2=self.W2,
            )
        )
        return surf_list

    # Inlined from Methods.Slot.VentilationTrap.check
    def check(self):
        """Make sure that the ventialtion parameters are correctly set

        Parameters
        ----------
        self : VentilationTrap
            A VentilationTrap object
        """

        if not isinstance(self.Zh, int):
            raise VentilationTrapInstanceError("Zh must be a integer")
        if not isinstance(self.H0, float) and not isinstance(self.H0, int):
            raise VentilationTrapInstanceError("H0 must be a float or int")
        if not isinstance(self.D0, float) and not isinstance(self.D0, int):
            raise VentilationTrapInstanceError("D0 must be a float or int")
        if not isinstance(self.Alpha0, float) and not isinstance(self.Alpha0, int):
            raise VentilationTrapInstanceError("Alpha0 must be a float or int")

    # Inlined from Methods.Slot.VentilationTrap.comp_radius
    def comp_radius(self):
        """Compute the radius of the two circle that contains all the ventilation
        ducts

        Parameters
        ----------
        self : VentilationTrap
            A VentilationTrap object

        Returns
        -------
        (Rmin, Rmax): tuple
            Tuple of circle radius [m]

        """

        self.check()

        Rmin = np.sqrt(self.W1**2 + self.H0**2)
        Rmax = np.sqrt(self.W2**2 + (self.H0 + self.D0) ** 2)

        return (Rmin, Rmax)

    # Inlined from Methods.Slot.VentilationTrap.comp_surface
    def comp_surface(self):
        """Compute the surface of all the axial ventilation ducts

        Parameters
        ----------
        self : VentilationTrap
            A VentilationTrap object

        Returns
        -------
        surface: float
            Axial ventilation ducts total surface [m**2]

        """

        self.check()

        return (self.W1 + self.W2) * 0.5 * self.D0

    # Inlined from Methods.Slot.VentilationTrap.get_center
    def get_center(self):
        """Return a list of center of the ventilations
        Parameters
        ----------
        self : VentilationTrap
            A VentilationTrap object

        Returns
        -------
        Zc_list: list
            List of list of center complex coordinates

        """

        Zc_list = []

        for ii in range(self.Zh):
            Zc = (
                (self.H0 + self.D0 / 2.0)
                * np.exp(1j * self.Alpha0)
                * np.exp(ii * 1j * 2 * np.pi / self.Zh)
            )
            Zc_list.append(Zc)

        return Zc_list

    # Inlined from Methods.Slot.VentilationTrap.plot_schematics
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
        self : VentilationTrap
            A VentilationTrap object
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
            Figure containing the plot
        ax : Matplotlib.axes.Axes object
            Axis containing the plot
        -------
        lam : LamSlot
            Default lamination used for the schematics
        """

        # Use some default parameter
        if is_default:
            hole = type(self)(
                H0=0.125,
                Zh=8,
                Alpha0=0.3,
                D0=0.05,
                W1=0.05,
                W2=0.08,
            )
            lam = LamHole(
                Rint=0.1, Rext=0.2, is_internal=True, is_stator=False, hole=[hole]
            )
            if is_return_default:
                return lam
            else:
                return hole.plot_schematics(
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
                raise ParentMissingError("Error: The hole is not inside a Lamination")
            lam = self.parent
            fig, ax = lam.plot(
                alpha=0,
                is_show_fig=False,
                is_lam_only=True,  # No magnet
                fig=fig,
                ax=ax,
            )  # center hole on Ox axis
            point_dict = self._comp_point_coordinate()

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
                line = Segment(0, point_dict["ZM1"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="H0",
                    offset_label=self.D0 / 4 * 1j,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # D0
                line = Segment(
                    point_dict["ZM1"] * np.exp(1j * 2 * np.pi / self.Zh),
                    point_dict["ZM2"] * np.exp(1j * 2 * np.pi / self.Zh),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="D0",
                    offset_label=self.D0 / 4,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # Alpha0
                line = Arc1(
                    begin=self.H0 + self.D0 / 2,
                    end=point_dict["Zc"],
                    radius=self.H0 + self.D0 / 2,
                    is_trigo_direction=True,
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="Alpha0",
                    offset_label=self.D0 / 4 * (1 - 1.7j),
                    fontsize=SC_FONT_SIZE,
                )
                # W1
                line = Segment(point_dict["Z1"], point_dict["Z4"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="W1",
                    offset_label=self.D0 / 4 * 1.5j,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # W2
                line = Segment(point_dict["Z2"], point_dict["Z3"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="W2",
                    offset_label=self.D0 / 4 * 1.5j,
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
                # Center axis
                line = Segment(0, lam.Rext * 1.5 * np.exp(1j * self.Alpha0))
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )

            # Zooming and cleaning
            W = abs(point_dict["Z2"].imag) * 1.3
            Rint = self.parent.Rint
            Rext = self.parent.Rext

            ax.axis("equal")
            ax.set_ylim(-Rext / 10, Rext * 0.9)
            ax.set_xlim(Rext / 10, Rext)
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

    class TrapezeBuildGeometryError(Exception):
        """raised when the parameter have not good type"""

    class VentilationTrapInstanceError(Exception):
        """Raised when a Ventilation Trap parameter is not int or float"""


TrapezeBuildGeometryError = VentilationTrap.TrapezeBuildGeometryError
VentilationTrapInstanceError = VentilationTrap.VentilationTrapInstanceError
