# File generated according to Generator/ClassesRef/Slot/HoleM62.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Slot/HoleM62"""

from os import linesep
from sys import getsizeof

import matplotlib.pyplot as plt
import numpy as np
from pyleecan.Classes import ParentMissingError
from pyleecan.Classes.Arc1 import Arc1
from pyleecan.Classes.HoleMag import HoleMag
from pyleecan.Classes.LamHole import LamHole
from pyleecan.Classes.Segment import Segment
from pyleecan.Classes.SurfLine import SurfLine
from pyleecan.Classes._check import check_var
from pyleecan.definitions import config_dict
from pyleecan.Functions.Load.import_class import import_class
from pyleecan.Functions.Plot import (
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
from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.labels import HOLEM_LAB
from pyleecan.Functions.load import load_init_dict
from pyleecan.Functions.save import save


class HoleM62(HoleMag):
    """Hole M62"""

    VERSION = 1
    IS_SYMMETRICAL = 1
    MAGNET_COLOR = config_dict["PLOT"]["COLOR_DICT"]["MAGNET_COLOR"]

    # cf Methods.Slot.HoleM62._comp_point_coordinate
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
        point_dict = dict()
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

    # cf Methods.Slot.HoleM62.build_geometry
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

        surf_list = list()
        # Create all the surfaces for all the case

        # Get all the points
        Z1 = point_dict["Z1"]
        Z2 = point_dict["Z2"]
        Z3 = point_dict["Z3"]
        Z4 = point_dict["Z4"]

        # surface Hole Radial
        curve_list = list()
        curve_list.append(Segment(Z1, Z2))
        curve_list.append(
            Arc1(
                begin=Z2,
                end=Z3,
                radius=Rbo - self.H1,
                is_trigo_direction=True,
            )
        )
        curve_list.append(Segment(Z3, Z4))
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

    # cf Methods.Slot.HoleM62.check
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
            raise S62_NoneError("You must set W0 !")
        elif self.H0 is None:
            raise S62_NoneError("You must set H0 !")
        elif self.H1 is None:
            raise S62_NoneError("You must set H1 !")

    # cf Methods.Slot.HoleM62.comp_magnetization_dict
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

        mag_dict = dict()

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

    # cf Methods.Slot.HoleM62.comp_radius
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

    # cf Methods.Slot.HoleM62.comp_surface
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

    # cf Methods.Slot.HoleM62.comp_surface_magnet_id
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

    # cf Methods.Slot.HoleM62.has_magnet
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

    # cf Methods.Slot.HoleM62.plot_schematics
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
                    Rbo * np.exp(1j * alpha), (Rbo - self.H1) * np.exp(1j * alpha)
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
                    point_dict["Z2"] * np.exp(1j * alpha),
                    point_dict["Z1"] * np.exp(1j * alpha),
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
                    line = Segment(0, lam.Rext * 1.5 * np.exp(1j * alpha))
                    line.plot(
                        fig=fig,
                        ax=ax,
                        color=MAIN_LINE_COLOR,
                        linestyle=MAIN_LINE_STYLE,
                        linewidth=MAIN_LINE_WIDTH,
                    )
                    # Tooth axis
                    line = Segment(
                        0, lam.Rext * 1.5 * np.exp(1j * sp / 2) * np.exp(1j * alpha)
                    )
                    line.plot(
                        fig=fig,
                        ax=ax,
                        color=MAIN_LINE_COLOR,
                        linestyle=MAIN_LINE_STYLE,
                        linewidth=MAIN_LINE_WIDTH,
                    )
                    line = Segment(
                        0, lam.Rext * 1.5 * np.exp(-1j * sp / 2) * np.exp(1j * alpha)
                    )
                    line.plot(
                        fig=fig,
                        ax=ax,
                        color=MAIN_LINE_COLOR,
                        linestyle=MAIN_LINE_STYLE,
                        linewidth=MAIN_LINE_WIDTH,
                    )

                    line = Segment(
                        point_dict["Z2"] * np.exp(1j * alpha),
                        point_dict["Z3"] * np.exp(1j * alpha),
                    )
                    line.plot(
                        fig=fig,
                        ax=ax,
                        color=MAIN_LINE_COLOR,
                        linestyle=MAIN_LINE_STYLE,
                        linewidth=MAIN_LINE_WIDTH,
                    )
                    line = Segment(
                        point_dict["Z1"] * np.exp(1j * alpha),
                        point_dict["Z4"] * np.exp(1j * alpha),
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

    # cf Methods.Slot.HoleM62.plot_schematics_radial
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
                    Rbo * np.exp(1j * alpha), (Rbo - self.H1) * np.exp(1j * alpha)
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
                    point_dict["Z2"] * np.exp(1j * alpha),
                    point_dict["Z1"] * np.exp(1j * alpha),
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
                    line = Segment(0, lam.Rext * 1.5 * np.exp(1j * alpha))
                    line.plot(
                        fig=fig,
                        ax=ax,
                        color=MAIN_LINE_COLOR,
                        linestyle=MAIN_LINE_STYLE,
                        linewidth=MAIN_LINE_WIDTH,
                    )
                    # Tooth axis
                    line = Segment(
                        0, lam.Rext * 1.5 * np.exp(1j * sp / 2) * np.exp(1j * alpha)
                    )
                    line.plot(
                        fig=fig,
                        ax=ax,
                        color=MAIN_LINE_COLOR,
                        linestyle=MAIN_LINE_STYLE,
                        linewidth=MAIN_LINE_WIDTH,
                    )
                    line = Segment(
                        0, lam.Rext * 1.5 * np.exp(-1j * sp / 2) * np.exp(1j * alpha)
                    )
                    line.plot(
                        fig=fig,
                        ax=ax,
                        color=MAIN_LINE_COLOR,
                        linestyle=MAIN_LINE_STYLE,
                        linewidth=MAIN_LINE_WIDTH,
                    )

                    line = Segment(0, 1.5 * point_dict["Z2"] * np.exp(1j * alpha))
                    line.plot(
                        fig=fig,
                        ax=ax,
                        color=MAIN_LINE_COLOR,
                        linestyle=MAIN_LINE_STYLE,
                        linewidth=MAIN_LINE_WIDTH,
                    )
                    line = Segment(0, 1.5 * point_dict["Z3"] * np.exp(1j * alpha))
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

    # cf Methods.Slot.HoleM62.remove_magnet
    def remove_magnet(self):
        """Remove the magnet (set to None) of the Hole

        Parameters
        ----------
        self : HoleM62
            a HoleM62 object
        """

        self.magnet_0 = None

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        W0=None,
        H0=None,
        H1=None,
        W0_is_rad=False,
        magnet_0=-1,
        Zh=36,
        mat_void=-1,
        magnetization_dict_offset=None,
        Alpha0=0,
        init_dict=None,
        init_str=None,
    ):
        """Constructor of the class. Can be use in three ways :
        - __init__ (arg1 = 1, arg3 = 5) every parameters have name and default values
            for pyleecan type, -1 will call the default constructor
        - __init__ (init_dict = d) d must be a dictionary with property names as keys
        - __init__ (init_str = s) s must be a string
        s is the file path to load

        ndarray or list can be given for Vector and Matrix
        object or dict can be given for pyleecan Object"""

        if init_str is not None:  # Load from a file
            init_dict = load_init_dict(init_str)[1]
        if init_dict is not None:  # Initialisation by dict
            assert type(init_dict) is dict
            # Overwrite default value with init_dict content
            if "W0" in list(init_dict.keys()):
                W0 = init_dict["W0"]
            if "H0" in list(init_dict.keys()):
                H0 = init_dict["H0"]
            if "H1" in list(init_dict.keys()):
                H1 = init_dict["H1"]
            if "W0_is_rad" in list(init_dict.keys()):
                W0_is_rad = init_dict["W0_is_rad"]
            if "magnet_0" in list(init_dict.keys()):
                magnet_0 = init_dict["magnet_0"]
            if "Zh" in list(init_dict.keys()):
                Zh = init_dict["Zh"]
            if "mat_void" in list(init_dict.keys()):
                mat_void = init_dict["mat_void"]
            if "magnetization_dict_offset" in list(init_dict.keys()):
                magnetization_dict_offset = init_dict["magnetization_dict_offset"]
            if "Alpha0" in list(init_dict.keys()):
                Alpha0 = init_dict["Alpha0"]
        # Set the properties (value check and convertion are done in setter)
        self.W0 = W0
        self.H0 = H0
        self.H1 = H1
        self.W0_is_rad = W0_is_rad
        self.magnet_0 = magnet_0
        # Call HoleMag init
        super(HoleM62, self).__init__(
            Zh=Zh,
            mat_void=mat_void,
            magnetization_dict_offset=magnetization_dict_offset,
            Alpha0=Alpha0,
        )
        # The class is frozen (in HoleMag init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        HoleM62_str = ""
        # Get the properties inherited from HoleMag
        HoleM62_str += super(HoleM62, self).__str__()
        HoleM62_str += "W0 = " + str(self.W0) + linesep
        HoleM62_str += "H0 = " + str(self.H0) + linesep
        HoleM62_str += "H1 = " + str(self.H1) + linesep
        HoleM62_str += "W0_is_rad = " + str(self.W0_is_rad) + linesep
        if self.magnet_0 is not None:
            tmp = self.magnet_0.__str__().replace(linesep, linesep + "\t").rstrip("\t")
            HoleM62_str += "magnet_0 = " + tmp
        else:
            HoleM62_str += "magnet_0 = None" + linesep + linesep
        return HoleM62_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from HoleMag
        if not super(HoleM62, self).__eq__(other):
            return False
        if other.W0 != self.W0:
            return False
        if other.H0 != self.H0:
            return False
        if other.H1 != self.H1:
            return False
        if other.W0_is_rad != self.W0_is_rad:
            return False
        if other.magnet_0 != self.magnet_0:
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()

        # Check the properties inherited from HoleMag
        diff_list.extend(
            super(HoleM62, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
        if (
            other._W0 is not None
            and self._W0 is not None
            and np.isnan(other._W0)
            and np.isnan(self._W0)
        ):
            pass
        elif other._W0 != self._W0:
            if is_add_value:
                val_str = " (self=" + str(self._W0) + ", other=" + str(other._W0) + ")"
                diff_list.append(name + ".W0" + val_str)
            else:
                diff_list.append(name + ".W0")
        if (
            other._H0 is not None
            and self._H0 is not None
            and np.isnan(other._H0)
            and np.isnan(self._H0)
        ):
            pass
        elif other._H0 != self._H0:
            if is_add_value:
                val_str = " (self=" + str(self._H0) + ", other=" + str(other._H0) + ")"
                diff_list.append(name + ".H0" + val_str)
            else:
                diff_list.append(name + ".H0")
        if (
            other._H1 is not None
            and self._H1 is not None
            and np.isnan(other._H1)
            and np.isnan(self._H1)
        ):
            pass
        elif other._H1 != self._H1:
            if is_add_value:
                val_str = " (self=" + str(self._H1) + ", other=" + str(other._H1) + ")"
                diff_list.append(name + ".H1" + val_str)
            else:
                diff_list.append(name + ".H1")
        if other._W0_is_rad != self._W0_is_rad:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._W0_is_rad)
                    + ", other="
                    + str(other._W0_is_rad)
                    + ")"
                )
                diff_list.append(name + ".W0_is_rad" + val_str)
            else:
                diff_list.append(name + ".W0_is_rad")
        if (other.magnet_0 is None and self.magnet_0 is not None) or (
            other.magnet_0 is not None and self.magnet_0 is None
        ):
            diff_list.append(name + ".magnet_0 None mismatch")
        elif self.magnet_0 is not None:
            diff_list.extend(
                self.magnet_0.compare(
                    other.magnet_0,
                    name=name + ".magnet_0",
                    ignore_list=ignore_list,
                    is_add_value=is_add_value,
                )
            )
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from HoleMag
        S += super(HoleM62, self).__sizeof__()
        S += getsizeof(self.W0)
        S += getsizeof(self.H0)
        S += getsizeof(self.H1)
        S += getsizeof(self.W0_is_rad)
        S += getsizeof(self.magnet_0)
        return S

    def as_dict(self, type_handle_ndarray=0, keep_function=False, **kwargs):
        """
        Convert this object in a json serializable dict (can be use in __init__).
        type_handle_ndarray: int
            How to handle ndarray (0: tolist, 1: copy, 2: nothing)
        keep_function : bool
            True to keep the function object, else return str
        Optional keyword input parameter is for internal use only
        and may prevent json serializability.
        """

        # Get the properties inherited from HoleMag
        HoleM62_dict = super(HoleM62, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs,
        )
        HoleM62_dict["W0"] = self.W0
        HoleM62_dict["H0"] = self.H0
        HoleM62_dict["H1"] = self.H1
        HoleM62_dict["W0_is_rad"] = self.W0_is_rad
        if self.magnet_0 is None:
            HoleM62_dict["magnet_0"] = None
        else:
            HoleM62_dict["magnet_0"] = self.magnet_0.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs,
            )
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        HoleM62_dict["__class__"] = "HoleM62"
        return HoleM62_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        W0_val = self.W0
        H0_val = self.H0
        H1_val = self.H1
        W0_is_rad_val = self.W0_is_rad
        if self.magnet_0 is None:
            magnet_0_val = None
        else:
            magnet_0_val = self.magnet_0.copy()
        Zh_val = self.Zh
        if self.mat_void is None:
            mat_void_val = None
        else:
            mat_void_val = self.mat_void.copy()
        if self.magnetization_dict_offset is None:
            magnetization_dict_offset_val = None
        else:
            magnetization_dict_offset_val = self.magnetization_dict_offset.copy()
        Alpha0_val = self.Alpha0
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(
            W0=W0_val,
            H0=H0_val,
            H1=H1_val,
            W0_is_rad=W0_is_rad_val,
            magnet_0=magnet_0_val,
            Zh=Zh_val,
            mat_void=mat_void_val,
            magnetization_dict_offset=magnetization_dict_offset_val,
            Alpha0=Alpha0_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.W0 = None
        self.H0 = None
        self.H1 = None
        self.W0_is_rad = None
        if self.magnet_0 is not None:
            self.magnet_0._set_None()
        # Set to None the properties inherited from HoleMag
        super(HoleM62, self)._set_None()

    def _get_W0(self):
        """getter of W0"""
        return self._W0

    def _set_W0(self, value):
        """setter of W0"""
        check_var("W0", value, "float", Vmin=0)
        self._W0 = value

    W0 = property(
        fget=_get_W0,
        fset=_set_W0,
        doc="""Length or Angle Opening

        :Type: float
        :min: 0
        """,
    )

    def _get_H0(self):
        """getter of H0"""
        return self._H0

    def _set_H0(self, value):
        """setter of H0"""
        check_var("H0", value, "float", Vmin=0)
        self._H0 = value

    H0 = property(
        fget=_get_H0,
        fset=_set_H0,
        doc="""Distance from the lamination bore

        :Type: float
        :min: 0
        """,
    )

    def _get_H1(self):
        """getter of H1"""
        return self._H1

    def _set_H1(self, value):
        """setter of H1"""
        check_var("H1", value, "float", Vmin=0)
        self._H1 = value

    H1 = property(
        fget=_get_H1,
        fset=_set_H1,
        doc="""Magnet height

        :Type: float
        :min: 0
        """,
    )

    def _get_W0_is_rad(self):
        """getter of W0_is_rad"""
        return self._W0_is_rad

    def _set_W0_is_rad(self, value):
        """setter of W0_is_rad"""
        check_var("W0_is_rad", value, "bool")
        self._W0_is_rad = value

    W0_is_rad = property(
        fget=_get_W0_is_rad,
        fset=_set_W0_is_rad,
        doc="""W0  unit, 0 for m, 1 for rad

        :Type: bool
        """,
    )

    def _get_magnet_0(self):
        """getter of magnet_0"""
        return self._magnet_0

    def _set_magnet_0(self, value):
        """setter of magnet_0"""
        if isinstance(value, str):  # Load from file
            try:
                value = load_init_dict(value)[1]
            except Exception as e:
                self.get_logger().error(
                    "Error while loading " + value + ", setting None instead"
                )
                value = None
        if isinstance(value, dict) and "__class__" in value:
            class_obj = import_class(
                "pyleecan.Classes", value.get("__class__"), "magnet_0"
            )
            value = class_obj(init_dict=value)
        elif type(value) is int and value == -1:  # Default constructor
            Magnet = import_class("pyleecan.Classes", "Magnet", "magnet_0")
            value = Magnet()
        check_var("magnet_0", value, "Magnet")
        self._magnet_0 = value

        if self._magnet_0 is not None:
            self._magnet_0.parent = self

    magnet_0 = property(
        fget=_get_magnet_0,
        fset=_set_magnet_0,
        doc="""First Magnet

        :Type: Magnet
        """,
    )

    class MachineCheckError(Exception):
        """ """

        pass

    class LaminationCheckError(MachineCheckError):
        """ """

        pass

    class SlotCheckError(LaminationCheckError):
        """ """

        pass

    class S62_NoneError(SlotCheckError):
        """Raised when a propery of HoleM62 is None"""

        pass


MachineCheckError = HoleM62.MachineCheckError

LaminationCheckError = HoleM62.LaminationCheckError

SlotCheckError = HoleM62.SlotCheckError

S62_NoneError = HoleM62.S62_NoneError
