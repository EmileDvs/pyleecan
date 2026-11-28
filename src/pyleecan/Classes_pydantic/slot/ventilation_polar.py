# Experimental pydantic model generated from Generator/ClassesRef/Slot/VentilationPolar.csv
"""Generated experimental pydantic model; do not edit by hand."""

from typing import TYPE_CHECKING, ClassVar

import matplotlib.pyplot as plt
import numpy as np
from pydantic import Field

from ...classes_common.errors import (
    ParentMissingError,
    PolarArcBuildGeometryError,
    VentilationPolarInstanceError,
)
from ...classes_common.parents import container_or_parent
from ...Functions_pydantic.Plot import (
    ARROW_COLOR,
    ARROW_WIDTH,
    MAIN_LINE_COLOR,
    MAIN_LINE_STYLE,
    MAIN_LINE_WIDTH,
    P_FONT_SIZE,
    SC_FONT_SIZE,
    TEXT_BOX,
)
from ..geometry.arc_1 import Arc1
from ..geometry.polar_arc import PolarArc
from ..geometry.segment import Segment
from ..machine.lam_hole import LamHole
from .hole import Hole

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure

    from ..machine.lamination import Lamination


class VentilationPolar(Hole):
    """Polar axial ventilation duct

    Attributes
    ----------
    D0 : float
        Height of the hole
        Unit: m; Default: 1; Minimum: 0
    H0 : float
        Radius of the bottom of Hole
        Unit: m; Default: 1; Minimum: 0
    W1 : float
        Hole angular width
        Unit: rad; Default: 1; Minimum: 0; Maximum: 6.29
    """

    D0: float = Field(default=1, ge=0, json_schema_extra={"unit": "m"})
    """Height of the hole"""
    H0: float = Field(default=1, ge=0, json_schema_extra={"unit": "m"})
    """Radius of the bottom of Hole"""
    W1: float = Field(default=1, ge=0, le=6.29, json_schema_extra={"unit": "rad"})
    """Hole angular width"""

    _package: ClassVar[str] = "Slot"
    """Name of the package of the legacy class module"""

    # Inlined from Methods.Slot.VentilationPolar._comp_point_coordinate
    def _comp_point_coordinate(self, lam: Lamination | None = None) -> dict:
        """Compute the point coordinates needed to plot the Hole.

        Parameters
        ----------
        self : VentilationPolar
            A VentilationPolar object
        lam : Lamination, optional
            Lamination holding the hole (default: the parent)

        Returns
        -------
        point_dict: dict
            A dict of the slot point coordinates
        """

        Z1 = (self.H0) * np.exp(1j * (self.Alpha0 - self.W1 / 2))
        Z2 = (self.H0 + self.D0) * np.exp(1j * (self.Alpha0 - self.W1 / 2))
        Z3 = (self.H0 + self.D0) * np.exp(1j * (self.Alpha0 + self.W1 / 2))
        Z4 = (self.H0) * np.exp(1j * (self.Alpha0 + self.W1 / 2))
        Zc = (self.H0 + (self.D0 / 2)) * np.exp(1j * self.Alpha0)

        point_dict = {}
        # symetry
        point_dict["Z1"] = Z1
        point_dict["Z2"] = Z2
        point_dict["Z3"] = Z3
        point_dict["Z4"] = Z4
        point_dict["Zc"] = Zc
        return point_dict

    # Inlined from Methods.Slot.VentilationPolar.build_geometry
    def build_geometry(
        self,
        alpha: float = 0,
        delta: complex = 0,
        lam: Lamination | None = None,
        lam_label: str | None = None,
    ) -> list:
        """Compute the curve needed to plot the ventilations

        Parameters
        ----------
        self : VentilationPolar
            A VentilationPolar object
        alpha : float
            Angle for rotation (Default value = 0) [rad]
        delta : complex
            Complex for translation (Default value = 0)
        lam : Lamination
            Lamination of the hole (default: the parent of the hole)
        lam_label : str, optional
            Label of the lamination (default: lam.get_label(), which reads
            the machine holding the lamination)

        Returns
        -------
        surf_list: list
            A list of PolarArc

        Raises
        _______
        PolarArcBuildGeometryError
            The parameter 'sym' must be an integer > 0
            The parameter 'alpha' must be an int or float
            The parameter 'delta' must be a complex or float or int number
        """
        lam = container_or_parent(self, lam, "lam")

        if lam_label is None:
            lam_label = lam.get_label()
        R_id, surf_type = self.get_R_id(lam=lam)
        RTS_id = "R" + str(R_id) + "-T0-S0"
        vent_label = lam_label + "_" + surf_type + "_" + RTS_id

        # checking if the param have good type
        if type(alpha) not in [int, float]:
            raise PolarArcBuildGeometryError(
                "The parameter 'alpha' must be an int or float"
            )
        if type(delta) not in [complex, int, float]:
            raise PolarArcBuildGeometryError(
                "The parameter 'delta' must be a complex or float or int number"
            )

        surf_list = []
        # Modulo on Alpha for sym
        Alpha0 = self.Alpha0 % (2 * np.pi / self.Zh)
        Zc = (self.H0 + (self.D0 / 2)) * np.exp(1j * Alpha0)
        surf_list.append(
            PolarArc(
                point_ref=Zc,
                label=vent_label,
                angle=self.W1,
                height=self.D0,
            )
        )

        return surf_list

    # Inlined from Methods.Slot.VentilationPolar.check
    def check(self, lam: Lamination | None = None) -> None:
        """Make sure that the ventilation parameters are correctly set

        Parameters
        ----------
        self : VentilationPolar
            A VentilationPolar object
        lam : Lamination, optional
            Lamination holding the hole (default: the parent)

        Returns
        -------
        None

        Raises
        _______
        VentilationPolarInstanceError
            Zh must be a integer
            H0 must be a float or int
            D0 must be a float or int
            Alpha0 must be a float or int
        """

        if not isinstance(self.Zh, int):
            raise VentilationPolarInstanceError("Zh must be a integer")
        if not isinstance(self.H0, float) and not isinstance(self.H0, int):
            raise VentilationPolarInstanceError("H0 must be a float or int")
        if not isinstance(self.D0, float) and not isinstance(self.D0, int):
            raise VentilationPolarInstanceError("D0 must be a float or int")
        if not isinstance(self.Alpha0, float) and not isinstance(self.Alpha0, int):
            raise VentilationPolarInstanceError("Alpha0 must be a float or int")

    # Inlined from Methods.Slot.VentilationPolar.comp_radius
    def comp_radius(self, lam: Lamination | None = None):
        """Compute the radius of the two circle that contains all the ventilation
        ducts

        Parameters
        ----------
        self : VentilationPolar
            A VentilationPolar object
        lam : Lamination, optional
            Lamination holding the hole (default: the parent)

        Returns
        -------
        (Rmin, Rmax): tuple
            Tuple of circle radius [m]

        """

        self.check(lam=lam)

        Rmin = self.H0
        Rmax = self.D0 + self.H0

        return (Rmin, Rmax)

    # Inlined from Methods.Slot.VentilationPolar.comp_surface
    def comp_surface(self, lam: Lamination | None = None) -> float:
        """Compute the surface of all the axial ventilation ducts

        Parameters
        ----------
        self : VentilationPolar
            A VentilationPolar object
        lam : Lamination, optional
            Lamination holding the hole (default: the parent)

        Returns
        -------
        surface: float
            Axial ventilation ducts total surface [m**2]

        """

        self.check(lam=lam)

        return np.pi * ((self.H0 + self.D0) ** 2 - self.H0**2) / (2 * np.pi / self.W1)

    # Inlined from Methods.Slot.VentilationPolar.get_center
    def get_center(self) -> list:
        """Return a list of the center of the ventilations

        Parameters
        ----------
        self : VentilationPolar
            A VentilationPolar object

        Returns
        -------
        Zc_list: list
            List of list of center complex coordinates

        """

        Zc_list = []

        for ii in range(self.Zh):
            Zc = self.H0 + (self.D0 / 2.0) * np.exp(1j * self.Alpha0) * np.exp(
                1j * 2 * np.pi / self.Zh
            )
            Zc_list.append(Zc)

        return Zc_list

    # Inlined from Methods.Slot.VentilationPolar.plot_schematics
    def plot_schematics(
        self,
        is_default: bool = False,
        is_return_default: bool = False,
        is_add_point_label: bool = False,
        is_add_schematics: bool = True,
        is_add_main_line: bool = True,
        type_add_active=True,
        save_path: str | None = None,
        is_show_fig: bool = True,
        fig: Figure | None = None,
        ax: Axes | None = None,
        lam: Lamination | None = None,
    ) -> tuple[Figure, Axes] | Lamination:
        """Plot the schematics of the slot

        Parameters
        ----------
        self : VentilationPolar
            A VentilationPolar object
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
        lam : Lamination
            Lamination of the hole (default: the parent of the hole)

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
        lam = container_or_parent(self, lam, "lam")

        # Use some default parameter
        if is_default:
            hole = type(self)(
                H0=0.125,
                Zh=8,
                Alpha0=0.3,
                D0=0.05,
                W1=2 * np.pi / 16,
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
                    lam=lam,
                )
        else:
            # Getting the main plot
            if lam is None:
                raise ParentMissingError("Error: The hole is not inside a Lamination")
            fig, ax = lam.plot(
                alpha=0,
                is_show_fig=False,
                is_lam_only=True,  # No magnet
                fig=fig,
                ax=ax,
            )  # center hole on Ox axis
            point_dict = self._comp_point_coordinate(lam=lam)

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
                line = Segment(begin=0, end=point_dict["Z1"])
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
                    begin=point_dict["Z1"] * np.exp(1j * 2 * np.pi / self.Zh),
                    end=point_dict["Z2"] * np.exp(1j * 2 * np.pi / self.Zh),
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
                    offset_label=self.D0 / 4 * (1 - 1.5j),
                    fontsize=SC_FONT_SIZE,
                )
                # W1
                Rtop = self.H0 + self.D0
                Rarc = (Rtop + lam.Rext) / 2
                line = Arc1(
                    begin=Rarc * np.exp(1j * (self.Alpha0 - self.W1 / 2)),
                    end=Rarc * np.exp(1j * (self.Alpha0 + self.W1 / 2)),
                    radius=Rarc,
                    is_trigo_direction=True,
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="W1",
                    offset_label=self.D0 / 4,
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
                # Center axis
                line = Segment(begin=0, end=lam.Rext * 1.5 * np.exp(1j * self.Alpha0))
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # H0 radius
                line = Arc1(
                    begin=self.H0 * np.exp(-1j * np.pi / 2 * 0.9),
                    end=self.H0 * np.exp(1j * np.pi / 2 * 0.9),
                    radius=self.H0,
                    is_trigo_direction=True,
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # H0+D0 radius
                line = Arc1(
                    begin=(self.H0 + self.D0) * np.exp(-1j * np.pi / 2 * 0.9),
                    end=(self.H0 + self.D0) * np.exp(1j * np.pi / 2 * 0.9),
                    radius=(self.H0 + self.D0),
                    is_trigo_direction=True,
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # Vent side 1 axis
                line = Segment(
                    begin=0,
                    end=lam.Rext * 1.5 * np.exp(1j * np.angle(point_dict["Z1"])),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # Vent side 2 axis
                line = Segment(
                    begin=0,
                    end=lam.Rext * 1.5 * np.exp(1j * np.angle(point_dict["Z3"])),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )

            # Zooming and cleaning
            W = abs(point_dict["Z2"].imag) * 1.3
            Rint = lam.Rint
            Rext = lam.Rext

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
