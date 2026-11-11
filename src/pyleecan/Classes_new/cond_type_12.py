# Experimental dataclass generated from Generator/ClassesRef/Machine/CondType12.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, Patch

from ..definitions import config_dict
from ..Functions_new.init_fig import init_fig
from ..Functions_new.Plot import ARROW_COLOR, ARROW_WIDTH, SC_FONT_SIZE, TEXT_BOX
from ._error import Lam_WindCheckError
from .conductor import Conductor
from .segment import Segment


@dataclass(eq=False)
class CondType12(Conductor):
    """parallel stranded conductor consisting of at least a single round wire

    Attributes
    ----------
    Wwire : float
        cf schematics, single strand diameter without insulation
        Unit: m; Default: 0.015; Minimum: 0
    Wins_cond : float
        (advanced) cf schematics, conductor diameter
        Unit: m; Default: 0.015; Minimum: 0
    Nwppc : int
        number of strands in parallel per conductor
        Default: 1; Minimum: 1
    Wins_wire : float
        (advanced) cf schematics, winding strand insulation thickness
        Unit: m; Default: 0; Minimum: 0
    Kwoh : float
        winding overhang factor which describes the fact that random round wire end-windings can be more or less compressed (0.5 for small motors, 0.8 for large motors) - can be used to tune the average turn length (relevant if type_cond==1)
        Default: 0.5; Minimum: 0
    """

    COND_COLOR = config_dict["PLOT"]["COLOR_DICT"]["PHASE_COLORS"][0].copy()
    INS_COLOR = config_dict["PLOT"]["COLOR_DICT"]["PHASE_COLORS"][1].copy()
    COND_INS_COLOR = config_dict["PLOT"]["COLOR_DICT"]["PHASE_COLORS"][2].copy()
    Wwire: float = 0.015
    """cf schematics, single strand diameter without insulation"""
    Wins_cond: float = 0.015
    """(advanced) cf schematics, conductor diameter"""
    Nwppc: int = 1
    """number of strands in parallel per conductor"""
    Wins_wire: float = 0
    """(advanced) cf schematics, winding strand insulation thickness"""
    Kwoh: float = 0.5
    """winding overhang factor which describes the fact that random round wire end-windings can be more or less compressed (0.5 for small motors, 0.8 for large motors) - can be used to tune the average turn length (relevant if type_cond==1)"""

    # Inlined from Methods.Machine.CondType12.check
    def check(self):
        """Check that the Conductor object is correct

        Parameters
        ----------
        self : CondType12
            A CondType12 object

        Returns
        -------
        None

        Raises
        _______
        C12_WireDontFit
            The wire is too big to fit in the conductor
        C12_WireDontFit
            The wires are too big to fit in the conductor
        """

        Swire = (
            np.power((self.Wwire + 2 * self.Wins_wire) / 2.0, 2) * np.pi * self.Nwppc
        )
        Scond = self.comp_surface()

        if Swire > Scond:
            if self.Nwppc == 1:
                raise self.C12_WireDontFit(
                    "The wire is too big to fit in the conductor"
                )
            else:
                raise self.C12_WireDontFit(
                    "The wires are too big to fit in the conductor"
                )

    # Inlined from Methods.Machine.CondType12.comp_height
    def comp_height(self):
        """Compute the height of the conductor

        Parameters
        ----------
        self : CondType12
            A CondType12 object

        Returns
        -------
        H: float
            Height of the conductor [m]

        """

        return self.comp_width()

    # Inlined from Methods.Machine.CondType12.comp_height_wire
    def comp_height_wire(self):
        """Return wire diameter

        Parameters
        ----------
        self : CondType12
            A CondType12 object

        Returns
        -------
        W: float
            Wire diameter [m]

        """

        return self.Wwire

    # Inlined from Methods.Machine.CondType12.comp_nb_circumferential_wire
    def comp_nb_circumferential_wire(self):
        """Return number of adjacent wires in circumferential direction

        Parameters
        ----------
        self : CondType12
            A CondType12 object

        Returns
        -------
        Nwppc_tan: int
            Number of adjacent wires in circumferential direction

        """

        return int(np.sqrt(self.Nwppc))

    # Inlined from Methods.Machine.CondType12.comp_nb_radial_wire
    def comp_nb_radial_wire(self):
        """Return number of adjacent wires in radial direction

        Parameters
        ----------
        self : CondType12
            A CondType12 object

        Returns
        -------
        Nwppc_rad: int
            Number of adjacent wires in radial direction

        """

        return int(np.sqrt(self.Nwppc))

    # Inlined from Methods.Machine.CondType12.comp_surface
    def comp_surface(self):
        """Compute the surface of the conductor

        Parameters
        ----------
        self : CondType12
            A CondType12 object

        Returns
        -------
        S: float
            Surface of the conductor (with insulation) [m**2]

        """

        return np.pi * ((self.comp_width() / 2.0) ** 2)

    # Inlined from Methods.Machine.CondType12.comp_surface_active
    def comp_surface_active(self):
        """Compute the active surface of the conductor

        Parameters
        ----------
        self : CondType12
            A CondType12 object

        Returns
        -------
        Sact: float
            Surface without insulation [m**2]

        """

        Sact = ((self.Wwire / 2.0) ** 2) * np.pi * self.Nwppc

        return Sact

    # Inlined from Methods.Machine.CondType12.comp_width
    def comp_width(self):
        """Compute the width of the conductor

        Parameters
        ----------
        self : CondType12
            A CondType12 object

        Returns
        -------
        W: float
            Width of the conductor [m]

        """

        if self.Wins_cond is None:
            if self.Nwppc == 1:
                Wins_wire = self.Wins_wire if self.Wins_wire is not None else 0
                width = self.Wwire + 2 * Wins_wire
            else:
                raise Exception("Conductor diameter not set")
        else:
            width = self.Wins_cond

        return width

    # Inlined from Methods.Machine.CondType12.comp_width_wire
    def comp_width_wire(self):
        """Return wire diameter

        Parameters
        ----------
        self : CondType12
            A CondType12 object

        Returns
        -------
        W: float
            Wire diameter [m]

        """

        return self.Wwire

    # Inlined from Methods.Machine.CondType12.is_round_wire
    def is_round_wire(self):
        """Return if wire is round

        Parameters
        ----------
        self : CondType11
            A CondType11 object

        Returns
        -------
        is_round_wire: bool
            is_round_wire is always False since wire is rectangular

        """

        return True

    # Inlined from Methods.Machine.CondType12.plot
    def plot(self, is_show_fig=True, fig=None, ax=None):
        """Plot a Conductor in a matplotlib fig

        Parameters
        ----------
        self : CondType12
            A CondType12 object
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

        Raises
        _______
        NotPlotableError
            You can't plot a coil with Nwppc>4
        """

        patches_list = []

        # Conductor insultation
        patches_list.append(
            Circle((0, 0), self.Wins_cond / 2, color=self.COND_INS_COLOR)
        )

        # Computation of the center of the wire
        center_list = []
        if self.Nwppc == 1:
            center_list.append((0, 0))
        elif self.Nwppc == 2:
            center_list.append((0, self.Wwire / 2 + self.Wins_wire))
            center_list.append((0, -self.Wwire / 2 - self.Wins_wire))
        elif self.Nwppc == 3:
            # The 3 centers are on the edges of an Equilateral Triangle
            # (side length : a = Dwire + 2Wins_wire)
            # The Radius of the circumscribed cercle is : a *sqrt(3)/3
            R = (self.Wwire + 2 * self.Wins_wire) * np.sqrt(3) / 3.0
            center_list.append((0, R))
            # We found the coordinate of the other center by complex rotation
            Z2 = R * 1j * np.exp(1j * 2 * np.pi / 3)
            Z3 = R * 1j * np.exp(-1j * 2 * np.pi / 3)
            center_list.append((Z2.real, Z2.imag))
            center_list.append((Z3.real, Z3.imag))
        elif self.Nwppc == 4:
            # The 4 centers are on the edges of a square
            # (side length : a =Dwire + 2Wins_wire)
            a = self.Wwire / 2 + self.Wins_wire
            center_list.append((a, a))
            center_list.append((a, -a))
            center_list.append((-a, a))
            center_list.append((-a, -a))
        else:
            raise self.NotPlotableError("You can't plot a coil with Nwppc>4")

        # Creation of the wires
        for center in center_list:
            # Wire insulation
            patches_list.append(
                Circle(center, self.Wwire / 2 + self.Wins_wire, color=self.INS_COLOR)
            )
            # Wire conductor
            patches_list.append(Circle(center, self.Wwire / 2, color=self.COND_COLOR))

        # Display
        (fig, ax, _, _) = init_fig(fig=fig, ax=ax)
        for patch in patches_list:
            ax.add_patch(patch)

        # Axis Setup
        ax.axis("equal")

        # The conductor is centered
        ax_lim = self.Wins_cond / 2 + self.Wins_cond / 10
        ax.set_xlim(-ax_lim, ax_lim)
        ax.set_ylim(-ax_lim, ax_lim)

        # Legend
        patch_leg = []  # Symbol
        label_leg = []  # Text
        patch_leg.append(Patch(color=self.COND_INS_COLOR))
        label_leg.append("Coil insulation")
        patch_leg.append(Patch(color=self.INS_COLOR))
        label_leg.append("Wire insulation")
        patch_leg.append(Patch(color=self.COND_COLOR))
        label_leg.append("Active wire section")

        ax.legend(patch_leg, label_leg)
        if is_show_fig:
            fig.show()
        return fig, ax

    # Inlined from Methods.Machine.CondType12.plot_schematics
    def plot_schematics(
        self,
        is_default=False,
        is_add_schematics=True,
        is_add_main_line=True,
        save_path=None,
        is_show_fig=True,
        fig=None,
        ax=None,
        is_single=False,
    ):
        """Plot the schematics of the slot

        Parameters
        ----------
        self : CondType12
            A CondType12 object
        is_default : bool
            True: plot default schematics, else use current slot values
        is_add_schematics : bool
            True to display the schematics information (W0, H0...)
        is_add_main_line : bool
            True to display "main lines" (slot opening and 0x axis)
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
        """

        # Use some default parameter
        if is_default and is_single:
            cond = type(self)(Wins_cond=40e-3, Wwire=35e-3, Wins_wire=5e-3, Nwppc=1)
            return cond.plot_schematics(
                is_default=False,
                is_add_schematics=is_add_schematics,
                is_add_main_line=is_add_main_line,
                save_path=save_path,
                is_show_fig=is_show_fig,
                fig=fig,
                ax=ax,
                is_single=is_single,
            )
        elif is_default:
            cond = type(self)(Wins_cond=40e-3, Wwire=10e-3, Wins_wire=2e-3, Nwppc=4)
            return cond.plot_schematics(
                is_default=False,
                is_add_schematics=is_add_schematics,
                is_add_main_line=is_add_main_line,
                save_path=save_path,
                is_show_fig=is_show_fig,
                fig=fig,
                ax=ax,
            )
        else:
            # Getting the main plot
            fig, ax = self.plot(
                is_show_fig=False, fig=fig, ax=ax
            )  # center slot on Ox axis
            a = self.Wwire / 2 + self.Wins_wire

            # Adding schematics
            if is_add_schematics:
                if is_single:
                    # Wwire
                    line = Segment(-self.Wwire / 2, self.Wwire / 2)
                    line.plot(
                        fig=fig,
                        ax=ax,
                        color=ARROW_COLOR,
                        linewidth=ARROW_WIDTH,
                        label="Conductor diameter",
                        offset_label=1j * self.Wins_wire / 2,
                        is_arrow=True,
                        fontsize=SC_FONT_SIZE,
                    )
                    # Wins_wire
                    line = Segment(
                        1j * (self.Wwire / 2 + self.Wins_wire), 1j * self.Wwire / 2
                    )
                    line.plot(
                        fig=fig,
                        ax=ax,
                        color=ARROW_COLOR,
                        linewidth=ARROW_WIDTH,
                        label="Insulator thickness",
                        offset_label=self.Wins_wire / 2,
                        is_arrow=True,
                        fontsize=SC_FONT_SIZE,
                    )
                else:
                    # Wwire
                    line = Segment(
                        a - self.Wwire / 2 + 1j * a, a + self.Wwire / 2 + 1j * a
                    )
                    line.plot(
                        fig=fig,
                        ax=ax,
                        color=ARROW_COLOR,
                        linewidth=ARROW_WIDTH,
                        label="Strand diameter",
                        offset_label=1j * self.Wins_wire,
                        is_arrow=True,
                        fontsize=SC_FONT_SIZE,
                    )
                    # Wins_wire
                    line = Segment(
                        -self.Wwire / 2 - self.Wins_wire + 1j * self.Wins_wire,
                        -self.Wwire / 2 - self.Wins_wire,
                    )
                    line.plot(
                        fig=fig,
                        ax=ax,
                        color=ARROW_COLOR,
                        linewidth=ARROW_WIDTH,
                        label="Insulator thickness",
                        offset_label=-8 * self.Wins_wire,
                        is_arrow=True,
                        fontsize=SC_FONT_SIZE,
                    )
                    # Wins_cond
                    line = Segment(-1j * self.Wins_cond / 2, 1j * self.Wins_cond / 2)
                    line.plot(
                        fig=fig,
                        ax=ax,
                        color=ARROW_COLOR,
                        linewidth=ARROW_WIDTH,
                        label="Overall diameter",
                        offset_label=-1j * self.Wins_cond * 0.25 + self.Wins_wire / 2,
                        is_arrow=True,
                        fontsize=SC_FONT_SIZE,
                    )
                    # Nwppc_rad
                    ax.text(
                        -a - 2 * self.Wwire,
                        2.5 * a,
                        "Strands in hand: 4",
                        fontsize=SC_FONT_SIZE,
                        bbox=TEXT_BOX,
                    )

            # Zooming and cleaning
            if is_single:
                W = self.comp_width() * 1.2
            else:
                W = self.comp_width() * 1.05

            ax.axis("equal")
            ax.set_xlim(-W / 2, W / 2)
            ax.set_ylim(-W / 2, W / 2)
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

            if is_show_fig:
                fig.show()
            return fig, ax

    class CondCheckError(Lam_WindCheckError):
        """ """

    class Cond12CheckError(CondCheckError):
        """ """

    class C12_WireDontFit(Cond12CheckError):
        """ """

    class NotPlotableError(Exception):
        """ """
