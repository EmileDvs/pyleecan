# Experimental dataclass generated from Generator/ClassesRef/Slot/HoleM54.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass
from typing import ClassVar

import matplotlib.pyplot as plt
import numpy as np

from . import ParentMissingError
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
from .arc_1 import Arc1
from .arc_3 import Arc3
from .hole import Hole
from .lam_hole import LamHole
from .segment import Segment
from .surf_line import SurfLine


@dataclass(eq=False)
class HoleM54(Hole):
    """Arc Hole for SyRM

    Attributes
    ----------
    H0 : float
        Hole depth
        Unit: m; Default: 0.003; Minimum: 0
    H1 : float
        Hole width
        Unit: m; Default: 0; Minimum: 0
    W0 : float
        Hole angular width
        Unit: rad; Default: 0.013; Minimum: 0
    R1 : float
        Hole radius
        Unit: m; Default: 0.02; Minimum: 0
    """

    IS_SYMMETRICAL: ClassVar = 1
    MAGNET_COLOR = config_dict["PLOT"]["COLOR_DICT"]["MAGNET_COLOR"]
    H0: float = 0.003
    """Hole depth"""
    H1: float = 0
    """Hole width"""
    W0: float = 0.013
    """Hole angular width"""
    R1: float = 0.02
    """Hole radius"""

    # Inlined from Methods.Slot.HoleM54._comp_point_coordinate
    def _comp_point_coordinate(self):
        """Compute the point coordinates needed to plot the Slot.

        Parameters
        ----------
        self : HoleM54
            A HoleM54 object

        Returns
        -------
        point_dict: dict
            A dict of the slot coordinates
        """

        Rext = self.get_Rext()

        # Compute point coordinates
        Zc0 = Rext - self.H0 + self.R1
        Z0 = Rext - self.H0
        Z1 = (self.R1 * np.exp(1j * (-np.pi + self.W0 / 2))) + Zc0
        Z2 = (self.R1 * np.exp(1j * (np.pi - self.W0 / 2))) + Zc0
        Z4 = ((self.R1 + self.H1) * np.exp(1j * (-np.pi + self.W0 / 2))) + Zc0
        Z3 = ((self.R1 + self.H1) * np.exp(1j * (np.pi - self.W0 / 2))) + Zc0

        point_dict = {}
        point_dict["Z0"] = Z0
        point_dict["Z1"] = Z1
        point_dict["Z2"] = Z2
        point_dict["Z3"] = Z3
        point_dict["Z4"] = Z4
        point_dict["Zc0"] = Zc0

        return point_dict

    # Inlined from Methods.Slot.HoleM54.build_geometry
    def build_geometry(self, alpha=0, delta=0, is_simplified=False):
        """Compute the curve (Arc) needed to plot the Hole.
        The ending point of a curve is the starting point of the next curve in the
        list

        Parameters
        ----------
        self : HoleM54
            A HoleM54 object
        alpha : float
            Angle to rotate the slot (Default value = 0) [rad]
        delta : complex
            Complex to translate the slot (Default value = 0)
        is_simplified : bool
           True to avoid line superposition

        Returns
        -------
        surf_list : list
            List of Air Surface on the slot

        """

        # Get correct label for surfaces
        lam_label = self.parent.get_label()
        R_id, surf_type = self.get_R_id()
        vent_label = lam_label + "_" + surf_type + "_R" + str(R_id) + "-"

        Rext = self.get_Rext()
        # Get all the points
        point_dict = self._comp_point_coordinate()
        Z1 = point_dict["Z1"]
        Z2 = point_dict["Z2"]
        Z3 = point_dict["Z3"]
        Z4 = point_dict["Z4"]

        surf_list = []
        curve_list = []
        curve_list.append(
            Arc1(begin=Z1, end=Z2, radius=-self.R1, is_trigo_direction=False)
        )
        curve_list.append(Arc3(begin=Z2, end=Z3, is_trigo_direction=True))
        curve_list.append(Arc1(begin=Z3, end=Z4, radius=self.R1 + self.H1))
        curve_list.append(Arc3(begin=Z4, end=Z1, is_trigo_direction=True))

        Zref = Rext - self.H0 - self.H1 / 2
        surf_list.append(
            SurfLine(line_list=curve_list, label=vent_label + "T0-S0", point_ref=Zref)
        )

        # Apply the transformations
        for surf in surf_list:
            surf.rotate(alpha)
            surf.translate(delta)

        return surf_list

    # Inlined from Methods.Slot.HoleM54.check
    def check(self):
        """Check that the HoleM54 object is correct

        Parameters
        ----------
        self : HoleM54
            A HoleM54 object

        Returns
        -------
        None

        Raises
        -------
        H54_W0CheckError
            You must have W0 < 2*pi/Zh
        H54_R1CheckError
            You must have H0 < R1
        """

        # Check that everything is set
        if self.W0 is None:
            raise S54_NoneError("You must set W0 !")
        elif self.R1 is None:
            raise S54_NoneError("You must set R1 !")
        elif self.H0 is None:
            raise S54_NoneError("You must set H0 !")
        elif self.H1 is None:
            raise S54_NoneError("You must set H1 !")

        if 2 * np.pi / self.Zh <= self.W0:
            raise H54_W0CheckError("You must have W0 < 2*pi/Zh")

        if self.R1 <= self.H0:
            raise H54_R1CheckError("You must have H0 < R1")

    # Inlined from Methods.Slot.HoleM54.comp_magnetization_dict
    def comp_magnetization_dict(self, is_north=True):
        """Compute the dictionary of the magnetization direction of the magnets (key=magnet_X, value=angle[rad])
        Mangetization angle with Hole centered on Ox axis

        Parameters
        ----------
        self : HoleM54
            a HoleM54 object
        is_north: True
            True: comp north magnetization, else add pi [rad]

        Returns
        -------
        mag_dict: dict
            magnetization dictionary (key=magnet_X, value=angle[rad])
        """

        mag_dict = {}

        return mag_dict

    # Inlined from Methods.Slot.HoleM54.comp_radius
    def comp_radius(self):
        """Compute the radius of the min and max circle that contains the hole

        Parameters
        ----------
        self : HoleM54
            A HoleM54 object

        Returns
        -------
        (Rmin,Rmax): tuple
            Radius of the circle that contains the hole [m]

        """

        Rext = self.get_Rext()

        surf_list = self.build_geometry()
        point_list = []
        for curve in surf_list[0].line_list:
            point_list.extend(curve.discretize())

        Rmax = max([np.abs(point) for point in point_list])
        Rmin = Rext - self.H0 - self.H1
        return (Rmin, Rmax)

    # Inlined from Methods.Slot.HoleM54.comp_surface
    def comp_surface(self):
        """Compute the complete surface of the Hole

        Parameters
        ----------
        self : HoleM54
            A HoleM54 object

        Returns
        -------
        S: float
            Surface of the Hole [m**2]

        """

        Sint = np.pi * self.R1**2
        Sext = np.pi * (self.R1 + self.H1) ** 2
        Sarc = (Sext - Sint) * (self.W0 / (2 * np.pi))

        return Sarc + np.pi * (self.H1 / 2) ** 2

    # Inlined from Methods.Slot.HoleM54.plot_schematics
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
        self : HoleM54
            A HoleM54 object
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
        lam : LamHole / LamSlot
            Default lamination used for the schematics
        """

        # Use some default parameter
        if is_default:
            hole = type(self)(Zh=8, W0=np.pi / 3, H0=25e-3, H1=10e-3, R1=75e-3)
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
            alpha = np.pi / 2  # To rotate the schematics
            fig, ax = lam.plot(
                alpha=np.pi / self.Zh + alpha,
                is_show_fig=False,
                is_lam_only=type_add_active == 0,
                fig=fig,
                ax=ax,
            )  # center hole on Ox axis
            sp = 2 * np.pi / self.Zh
            Rbo = self.get_Rbo()
            point_dict = self._comp_point_coordinate()

            # Adding point label
            if is_add_point_label:
                for name, Z in point_dict.items():
                    Z = Z * np.exp(1j * alpha)
                    ax.text(
                        Z.real,
                        Z.imag,
                        name,
                        fontsize=P_FONT_SIZE,
                        bbox=TEXT_BOX,
                    )

            # Adding schematics
            if is_add_schematics:
                # H1
                line = Segment(
                    Rbo * np.exp(1j * alpha),
                    point_dict["Z0"] * np.exp(1j * alpha),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="H0",
                    offset_label=self.H1 * 0.5,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # H1
                line = Segment(
                    point_dict["Z2"] * np.exp(1j * alpha),
                    point_dict["Z3"] * np.exp(1j * alpha),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="H1",
                    offset_label=self.H1 * 0.5,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # R1
                line = Segment(
                    point_dict["Z1"] * np.exp(1j * alpha),
                    point_dict["Zc0"] * np.exp(1j * alpha),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="R1",
                    offset_label=self.H1 * 0.5,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # W0
                line = Arc1(
                    begin=(point_dict["Z2"] + point_dict["Zc0"])
                    / 2
                    * np.exp(1j * alpha),
                    end=(point_dict["Z1"] + point_dict["Zc0"]) / 2 * np.exp(1j * alpha),
                    radius=self.R1,
                    is_trigo_direction=True,
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="W0",
                    offset_label=1j * self.H1 * 0.5,
                    fontsize=SC_FONT_SIZE,
                )

            if is_add_main_line:
                # Ox axis
                line = Segment(0, lam.Rext * 1.5 * np.exp(1j * alpha))
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # H1 line
                line = Arc3(
                    begin=(point_dict["Zc0"] + 1j * self.R1) * np.exp(1j * alpha),
                    end=(point_dict["Zc0"] - 1j * self.R1) * np.exp(1j * alpha),
                    is_trigo_direction=True,
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                line = Arc3(
                    begin=(point_dict["Zc0"] + 1j * (self.R1 + self.H1))
                    * np.exp(1j * alpha),
                    end=(point_dict["Zc0"] - 1j * (self.R1 + self.H1))
                    * np.exp(1j * alpha),
                    is_trigo_direction=True,
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # R1 lines
                line = Segment(
                    point_dict["Zc0"] * np.exp(1j * alpha),
                    point_dict["Z4"] * np.exp(1j * alpha),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                line = Segment(
                    point_dict["Zc0"] * np.exp(1j * alpha),
                    point_dict["Z3"] * np.exp(1j * alpha),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )

            # Zooming and cleaning
            W = point_dict["Z2"].imag * 1.2
            Rint = point_dict["Z3"].real * 0.9
            Rext = point_dict["Zc0"].real

            ax.axis("equal")
            ax.set_ylim(Rint, Rext)
            ax.set_xlim(-W, W)
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

    class H54_W0CheckError(SlotCheckError):
        """ """

    class S54_NoneError(SlotCheckError):
        """Raised when a propery of HoleM54 is None"""

    class H54_R1CheckError(SlotCheckError):
        """ """


MachineCheckError = HoleM54.MachineCheckError
LaminationCheckError = HoleM54.LaminationCheckError
SlotCheckError = HoleM54.SlotCheckError
H54_W0CheckError = HoleM54.H54_W0CheckError
S54_NoneError = HoleM54.S54_NoneError
H54_R1CheckError = HoleM54.H54_R1CheckError
