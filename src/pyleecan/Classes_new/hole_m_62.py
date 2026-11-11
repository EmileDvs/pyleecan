# Experimental dataclass generated from Generator/ClassesRef/Slot/HoleM62.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field
from typing import ClassVar

import matplotlib.pyplot as plt
import numpy as np

from ..definitions import config_dict
from ..Functions_new.labels import HOLEM_LAB
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
from .hole_mag import HoleMag
from .lam_hole import LamHole
from .magnet import Magnet
from .segment import Segment
from .surf_line import SurfLine


@dataclass(eq=False)
class HoleM62(HoleMag):
    """Hole M62

    Attributes
    ----------
    W0 : float or None
        Length or Angle Opening
        Unit: m/rad; Default: None; Minimum: 0
    H0 : float or None
        Distance from the lamination bore
        Unit: m; Default: None; Minimum: 0
    H1 : float or None
        Magnet height
        Unit: m; Default: None; Minimum: 0
    W0_is_rad : bool
        W0  unit, False for m, True for rad
        Default: False
    magnet_0 : Magnet or None
        First Magnet
        Default: Magnet()
    """

    IS_SYMMETRICAL: ClassVar = 1
    MAGNET_COLOR = config_dict["PLOT"]["COLOR_DICT"]["MAGNET_COLOR"]
    W0: float | None = None
    """Length or Angle Opening"""
    H0: float | None = None
    """Distance from the lamination bore"""
    H1: float | None = None
    """Magnet height"""
    W0_is_rad: bool = False
    """W0  unit, False for m, True for rad"""
    magnet_0: Magnet | None = field(
        default_factory=lambda: Magnet(), metadata={"default_class": "Magnet"}
    )
    """First Magnet"""

    # Inlined from Methods.Slot.HoleM62._comp_point_coordinate
    def _comp_point_coordinate(self):
        """Compute the point coordinates needed to plot the Slot.

        Parameters
        ----------
        self : HoleM62
            A HoleM62 object

        Returns
        -------
        point_dict: dict
            A dict of the slot coordinates
        """

        Rbo = self.get_Rbo()
        point_dict = {}
        # comp point coordinate (in complex)
        if self.W0_is_rad:
            Z1 = (Rbo - self.H1 - self.H0) * np.exp(-1j * self.W0 / 2)
            Z2 = (Rbo - self.H1) * np.exp(-1j * self.W0 / 2)
            Z3 = (Rbo - self.H1) * np.exp(1j * self.W0 / 2)
            Z4 = (Rbo - self.H1 - self.H0) * np.exp(1j * self.W0 / 2)
            point_dict["Z1"] = Z1
            point_dict["Z2"] = Z2
            point_dict["Z3"] = Z3
            point_dict["Z4"] = Z4

        else:
            Zc1 = ((Rbo - self.H1) ** 2) - ((self.W0 / 2) ** 2)
            Zc = np.sqrt(Zc1)

            Z7 = Zc + 1j * self.W0 / 2
            Z6 = Zc - 1j * self.W0 / 2
            Z8 = Z7 - self.H0
            Z5 = Z6 - self.H0
            point_dict["Z1"] = Z5
            point_dict["Z2"] = Z6
            point_dict["Z3"] = Z7
            point_dict["Z4"] = Z8

        return point_dict

    # Inlined from Methods.Slot.HoleM62.build_geometry
    def build_geometry(self, alpha=0, delta=0, is_simplified=False):
        """Compute the curve (Segment) needed to plot the Slot.
        The ending point of a curve is the starting point of the next curve in
        the list

        Parameters
        ----------
        self : HoleM62
            A HoleM62 object
        alpha : float
            Angle to rotate the slot (Default value = 0) [rad]
        delta : complex
            Complex to translate the slot (Default value = 0)
        is_simplified : bool
            True to avoid line superposition

        Returns
        -------
        surf_list: list
            List of SurfLine needed to draw the HoleM58

        """
        Rbo = self.get_Rbo()

        # Get correct label for surfaces
        lam_label = self.parent.get_label()
        R_id, surf_type = self.get_R_id()
        mag_label = f"{lam_label}_{HOLEM_LAB}_R{R_id}-"
        vent_label = f"{lam_label}_{surf_type}_R{R_id}-"
        point_dict = self._comp_point_coordinate()

        surf_list = []
        # Create all the surfaces for all the case

        # Get all the points
        Z1 = point_dict["Z1"]
        Z2 = point_dict["Z2"]
        Z3 = point_dict["Z3"]
        Z4 = point_dict["Z4"]

        # surface Hole Radial
        curve_list = []
        curve_list.append(Segment(begin=Z1, end=Z2))
        curve_list.append(
            Arc1(
                begin=Z2,
                end=Z3,
                radius=Rbo - self.H1,
                is_trigo_direction=True,
            )
        )
        curve_list.append(Segment(begin=Z3, end=Z4))
        curve_list.append(
            Arc1(
                begin=Z4,
                end=Z1,
                radius=-(abs(Z1)),
                is_trigo_direction=False,
            )
        )
        point_ref = (Z3 + Z1) / 2
        S1 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # Create the surface list by selecting the correct ones
        if self.magnet_0 is None:
            S1.label = vent_label + "T0-S0"
            surf_list = [S1]
        else:
            S1.label = mag_label + "T0-S0"
            surf_list = [S1]

        # Apply the transformations
        for surf in surf_list:
            surf.rotate(alpha)
            surf.translate(delta)

        return surf_list

    # Inlined from Methods.Slot.HoleM62.check
    def check(self):
        """Check that the HoleM62 object is correct

        Parameters
        ----------
        self : HoleM62
            A HoleM62 object

        Returns
        -------
        None

        Raises
        _______
        S62_WCheckError
        """

        # Check that everything is set
        if self.W0 is None:
            raise self.S62_NoneError("You must set W0 !")
        elif self.H0 is None:
            raise self.S62_NoneError("You must set H0 !")
        elif self.H1 is None:
            raise self.S62_NoneError("You must set H1 !")

    # Inlined from Methods.Slot.HoleM62.comp_magnetization_dict
    def comp_magnetization_dict(self, is_north=True):
        """Compute the dictionary of the magnetization direction of the magnets (key=magnet_X, value=angle[rad])
        Mangetization angle with Hole centered on Ox axis

        Parameters
        ----------
        self : HoleM62
            a HoleM62 object
        is_north: True
            True: comp north magnetization, else add pi [rad]

        Returns
        -------
        mag_dict: dict
            magnetization dictionary (key=magnet_X, value=angle[rad])
        """

        # Comp magnet
        point_dict = self._comp_point_coordinate()
        Rbo = self.get_Rbo()

        mag_dict = {}

        S0 = Arc1(
            begin=point_dict["Z2"],
            end=point_dict["Z3"],
            radius=Rbo - self.H1,
            is_trigo_direction=True,
        )
        mag_dict["magnet_0"] = S0.comp_normal()

        if not is_north:
            mag_dict["magnet_0"] += np.pi

        if self.magnetization_dict_offset is not None:
            for key, value in self.magnetization_dict_offset:
                mag_dict[key] += value

        return mag_dict

    # Inlined from Methods.Slot.HoleM62.comp_radius
    def comp_radius(self):
        """Compute the radius of the min and max circle that contains the slot

        Parameters
        ----------
        self : HoleM62
            A HoleM62 object

        Returns
        -------
        (Rmin,Rmax): tuple
            Radius of the circle that contains the slot [m]
        """

        Rbo = self.get_Rbo()

        Rmax = Rbo - self.H1

        if not self.W0_is_rad:
            point_dict = self._comp_point_coordinate()
            Rmin = np.abs(point_dict["Z1"])
        else:
            Rmin = Rbo - self.H1 - self.H0

        return (Rmin, Rmax)

    # Inlined from Methods.Slot.HoleM62.comp_surface
    def comp_surface(self):
        """Compute the surface of the Hole

        Parameters
        ----------
        self : HoleM62
            A HoleM62 object

        Returns
        -------
        S: float
            Surface of the Hole. [m**2]

        """
        Rbo = self.get_Rbo()
        if self.W0_is_rad:  # Polar Arc
            return (
                self.W0 * (Rbo - self.H1) ** 2 / 2
                - self.W0 * (Rbo - self.H1 - self.H0) ** 2 / 2
            )

        else:  # Parallel side
            Rbo = self.get_Rbo()
            # Top surface
            alpha = 2 * np.arcsin((self.W0 / 2) / (Rbo - self.H1))
            Stop = ((Rbo - self.H1) ** 2) * (alpha - np.sin(alpha)) / 2

            # Bottom surface
            point_dict = self._comp_point_coordinate()
            Z1 = point_dict["Z1"]
            R1 = abs(Z1)
            alpha = 2 * np.arcsin((self.W0 / 2) / R1)
            Sbot = R1**2 * (alpha - np.sin(alpha)) / 2

            return self.H0 * self.W0 + Stop - Sbot

    # Inlined from Methods.Slot.HoleM62.comp_surface_magnet_id
    def comp_surface_magnet_id(self, index):
        """Compute the surface of the hole magnet of the corresponding index

        Parameters
        ----------
        self : HoleM62
            A HoleM62 object
        index : int
            Index of the magnet to compute the surface

        Returns
        -------
        Smag: float
            Surface of the Magnet [m**2]
        """

        if index != 0:
            raise Exception("Only one magnet for HoleM62")
        if self.magnet_0 is not None:
            return self.comp_surface()  # Full magnet, no air
        return 0

    # Inlined from Methods.Slot.HoleM62.has_magnet
    def has_magnet(self):
        """Return if the Hole has magnets

        Parameters
        ----------
        self : HoleM62
            A HoleM62 object

        Returns
        -------
        has_magnet : bool
            True if the magnets are not None
        """

        return self.magnet_0 is not None

    # Inlined from Methods.Slot.HoleM62.plot_schematics
    def plot_schematics(
        self,
        is_return_default=False,
        is_default=False,
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
        self : HoleM62
            A HoleM62 object
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
        if is_default:
            hole = type(self)(
                Zh=4,
                W0=80e-3,
                H0=20e-3,
                H1=30e-3,
                W0_is_rad=False,
            )
            lam = LamHole(
                Rint=0.03, Rext=0.12, is_internal=True, is_stator=False, hole=[hole]
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

            # Remove the magnets
            if type_add_active == 0:
                lam.hole[0].remove_magnet()

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
                    begin=Rbo * np.exp(1j * alpha),
                    end=(Rbo - self.H1) * np.exp(1j * alpha),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="H1",
                    offset_label=0.003,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )

                # H0
                line = Segment(
                    begin=point_dict["Z2"] * np.exp(1j * alpha),
                    end=point_dict["Z1"] * np.exp(1j * alpha),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="H0",
                    offset_label=0.003 - 1j * 0.004,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # W0 [m]
                Zlim1 = point_dict["Z4"] - self.H0 * 0.2
                Zlim2 = point_dict["Z1"] - self.H0 * 0.2
                plot_quote(
                    point_dict["Z4"] * np.exp(1j * alpha),
                    Zlim1 * np.exp(1j * alpha),
                    Zlim2 * np.exp(1j * alpha),
                    point_dict["Z1"] * np.exp(1j * alpha),
                    offset_label=-1j * self.H0 * 0.4,
                    fig=fig,
                    ax=ax,
                    label="W0 [m]",
                )

                if is_add_main_line:
                    # Ox axis
                    line = Segment(begin=0, end=lam.Rext * 1.5 * np.exp(1j * alpha))
                    line.plot(
                        fig=fig,
                        ax=ax,
                        color=MAIN_LINE_COLOR,
                        linestyle=MAIN_LINE_STYLE,
                        linewidth=MAIN_LINE_WIDTH,
                    )
                    # Tooth axis
                    line = Segment(
                        begin=0,
                        end=lam.Rext * 1.5 * np.exp(1j * sp / 2) * np.exp(1j * alpha),
                    )
                    line.plot(
                        fig=fig,
                        ax=ax,
                        color=MAIN_LINE_COLOR,
                        linestyle=MAIN_LINE_STYLE,
                        linewidth=MAIN_LINE_WIDTH,
                    )
                    line = Segment(
                        begin=0,
                        end=lam.Rext * 1.5 * np.exp(-1j * sp / 2) * np.exp(1j * alpha),
                    )
                    line.plot(
                        fig=fig,
                        ax=ax,
                        color=MAIN_LINE_COLOR,
                        linestyle=MAIN_LINE_STYLE,
                        linewidth=MAIN_LINE_WIDTH,
                    )

                    line = Segment(
                        begin=point_dict["Z2"] * np.exp(1j * alpha),
                        end=point_dict["Z3"] * np.exp(1j * alpha),
                    )
                    line.plot(
                        fig=fig,
                        ax=ax,
                        color=MAIN_LINE_COLOR,
                        linestyle=MAIN_LINE_STYLE,
                        linewidth=MAIN_LINE_WIDTH,
                    )
                    line = Segment(
                        begin=point_dict["Z1"] * np.exp(1j * alpha),
                        end=point_dict["Z4"] * np.exp(1j * alpha),
                    )
                    line.plot(
                        fig=fig,
                        ax=ax,
                        color=MAIN_LINE_COLOR,
                        linestyle=MAIN_LINE_STYLE,
                        linewidth=MAIN_LINE_WIDTH,
                    )

            # Zooming and cleaning
            W = (point_dict["Z1"] * np.exp(1j * sp)).imag
            Rint = self.parent.Rint
            Rext = self.parent.Rext

            ax.axis("equal")
            ax.set_ylim(Rint, Rext)
            ax.set_xlim(-W, W)
            manager = plt.get_current_fig_manager()
            if manager is not None:
                manager.set_window_title(type(self).__name__ + " Schematics")
            ax.set_title("")
            ax.get_legend().remove()
            ax.set_axis_off()

            # Save / Show
            if save_path is not None:
                fig.savefig(save_path)
                plt.close(fig=fig)
            fig.tight_layout()

            if is_show_fig:
                fig.show()
            return fig, ax

    # Inlined from Methods.Slot.HoleM62.plot_schematics_radial
    def plot_schematics_radial(
        self,
        is_return_default=False,
        is_default=False,
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
        self : HoleM62
            A HoleM62 object
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
        if is_default:
            hole = type(self)(
                Zh=4,
                W0=np.pi / 4,
                H0=20e-3,
                H1=30e-3,
                W0_is_rad=True,
            )
            lam = LamHole(
                Rint=0.03, Rext=0.12, is_internal=True, is_stator=False, hole=[hole]
            )
            if is_return_default:
                return lam
            else:
                return hole.plot_schematics_radial(
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

            # Remove the magnets
            if type_add_active == 0:
                lam.hole[0].remove_magnet()

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
                    begin=Rbo * np.exp(1j * alpha),
                    end=(Rbo - self.H1) * np.exp(1j * alpha),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="H1",
                    offset_label=0.003,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )

                # W0
                line = Arc1(
                    begin=(Rbo - self.H1 - 2 * self.H0)
                    * np.exp(-1j * self.W0 / 2)
                    * np.exp(1j * alpha),
                    end=(Rbo - self.H1 - 2 * self.H0)
                    * np.exp(1j * self.W0 / 2)
                    * np.exp(1j * alpha),
                    radius=Rbo - self.H1,
                    is_trigo_direction=True,
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="W0 [rad]",
                    offset_label=1j * self.H0 / 5 + 0.003,
                    fontsize=SC_FONT_SIZE,
                )
                # H0
                line = Segment(
                    begin=point_dict["Z2"] * np.exp(1j * alpha),
                    end=point_dict["Z1"] * np.exp(1j * alpha),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="H0",
                    offset_label=0.003 - 1j * 0.004,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )

                if is_add_main_line:
                    # Ox axis
                    line = Segment(begin=0, end=lam.Rext * 1.5 * np.exp(1j * alpha))
                    line.plot(
                        fig=fig,
                        ax=ax,
                        color=MAIN_LINE_COLOR,
                        linestyle=MAIN_LINE_STYLE,
                        linewidth=MAIN_LINE_WIDTH,
                    )
                    # Tooth axis
                    line = Segment(
                        begin=0,
                        end=lam.Rext * 1.5 * np.exp(1j * sp / 2) * np.exp(1j * alpha),
                    )
                    line.plot(
                        fig=fig,
                        ax=ax,
                        color=MAIN_LINE_COLOR,
                        linestyle=MAIN_LINE_STYLE,
                        linewidth=MAIN_LINE_WIDTH,
                    )
                    line = Segment(
                        begin=0,
                        end=lam.Rext * 1.5 * np.exp(-1j * sp / 2) * np.exp(1j * alpha),
                    )
                    line.plot(
                        fig=fig,
                        ax=ax,
                        color=MAIN_LINE_COLOR,
                        linestyle=MAIN_LINE_STYLE,
                        linewidth=MAIN_LINE_WIDTH,
                    )

                    line = Segment(
                        begin=0, end=1.5 * point_dict["Z2"] * np.exp(1j * alpha)
                    )
                    line.plot(
                        fig=fig,
                        ax=ax,
                        color=MAIN_LINE_COLOR,
                        linestyle=MAIN_LINE_STYLE,
                        linewidth=MAIN_LINE_WIDTH,
                    )
                    line = Segment(
                        begin=0, end=1.5 * point_dict["Z3"] * np.exp(1j * alpha)
                    )
                    line.plot(
                        fig=fig,
                        ax=ax,
                        color=MAIN_LINE_COLOR,
                        linestyle=MAIN_LINE_STYLE,
                        linewidth=MAIN_LINE_WIDTH,
                    )

            # Zooming and cleaning
            W = (point_dict["Z1"] * np.exp(1j * sp)).imag

            Rint = self.parent.Rint
            Rext = self.parent.Rext

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

    # Inlined from Methods.Slot.HoleM62.remove_magnet
    def remove_magnet(self):
        """Remove the magnet (set to None) of the Hole

        Parameters
        ----------
        self : HoleM62
            a HoleM62 object
        """

        self.magnet_0 = None

    class S62_NoneError(SlotCheckError):
        """Raised when a propery of HoleM62 is None"""
