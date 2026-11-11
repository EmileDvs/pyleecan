# Experimental dataclass generated from Generator/ClassesRef/Machine/BoreFlower.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

import matplotlib.pyplot as plt
import numpy as np

from ..definitions import config_dict
from ..Functions_new.Geometry.comp_flower_arc import comp_flower_arc
from ..Functions_new.Plot import (
    ARROW_COLOR,
    ARROW_WIDTH,
    MAIN_LINE_COLOR,
    MAIN_LINE_STYLE,
    MAIN_LINE_WIDTH,
    SC_FONT_SIZE,
)
from ._error import ParentMissingError
from .arc_1 import Arc1
from .bore import Bore
from .lamination import Lamination
from .segment import Segment


@dataclass(eq=False)
class BoreFlower(Bore):
    """Class for Bore flower shape

    Attributes
    ----------
    N : int
        Number of flower arc
        Default: 8; Minimum: 0
    Rarc : float
        Radius of the flower arc
        Unit: m; Default: 0.01; Minimum: 0
    """

    MAGNET_COLOR = config_dict["PLOT"]["COLOR_DICT"]["MAGNET_COLOR"]
    N: int = 8
    """Number of flower arc"""
    Rarc: float = 0.01
    """Radius of the flower arc"""

    # Inlined from Methods.Machine.BoreFlower.comp_periodicity_spatial
    def comp_periodicity_spatial(self):
        """Compute the periodicity factor of the Bore

        Parameters
        ----------
        self : BoreFlower
            A BoreFlower object

        Returns
        -------
        per_a : int
            Number of spatial periodicities of the bore
        is_antiper_a : bool
            True if an spatial anti-periodicity is possible after the periodicities
        """

        return self.N, False

    # Inlined from Methods.Machine.BoreFlower.get_bore_line
    def get_bore_line(self, prop_dict=None):
        """Return the bore line description

        Parameters
        ----------
        self : BoreFlower
            A BoreFlower object
        prop_dict : dict
            Property dictionary to apply on the lines

        Returns
        -------
        bore_list : list
            List of bore lines
        """

        if self.parent is not None:
            if self.is_yoke():
                R = self.parent.get_Ryoke()
            else:
                R = self.parent.get_Rbo()
        else:
            raise ParentMissingError(
                "Error: The Bore object is not inside a Lamination"
            )

        # Compute the shape
        (alpha_lim, zL, zR) = comp_flower_arc(2 * np.pi / self.N, self.Rarc, R)

        # Create the lines
        bore_list = []
        for ii in range(self.N):
            rot = np.exp(1j * (2 * np.pi / self.N * (ii - 1) + self.alpha))
            arc = Arc1(
                begin=zR * rot, end=zL * rot, radius=self.Rarc, prop_dict=prop_dict
            )
            bore_list.append(arc)
        return bore_list

    # Inlined from Methods.Machine.BoreFlower.plot_schematics
    def plot_schematics(
        self,
        is_default=False,
        is_add_schematics=True,
        is_add_main_line=True,
        save_path=None,
        is_show_fig=True,
        fig=None,
        ax=None,
    ):
        """Plot the schematics of the slot

        Parameters
        ----------
        self : BoreFlower
            A BoreFlower object
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
            Figure containing the schematics
        ax : Matplotlib.axes.Axes object
            Axis containing the schematics
        """

        # Use some default parameter
        if is_default:
            bore = type(self)(N=8, Rarc=0.2, alpha=np.pi / 8)
            lam = Lamination(
                Rint=0.135, Rext=0.3, is_internal=True, is_stator=False, bore=bore
            )
            return bore.plot_schematics(
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
            if self.parent is None:
                raise ParentMissingError("Error: The bore is not inside a Lamination")
            lam = self.parent
            fig, ax = lam.plot(is_show_fig=False, fig=fig, ax=ax)

            # Comp point coordinates
            lines = self.get_bore_line()
            Zc = lines[1].get_center()
            Z1 = lines[1].get_begin()
            Z2 = lines[1].get_end()
            Zm0 = lines[1].get_middle()
            Zm1 = lines[2].get_middle()
            Rbo = self.parent.get_Rbo()
            H = self.Rarc / 8  # Small distance for label placement

            # Adding schematics
            if is_add_schematics:
                # Rarc
                line = Segment(Zc, Zm0)
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="Rarc",
                    offset_label=1j * H * 1.5,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # Alpha0
                line = Arc1(
                    begin=Rbo,
                    end=Zm0,
                    radius=Rbo,
                    is_trigo_direction=True,
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="alpha",
                    offset_label=H,
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
                # Rarc
                line = Segment(Zc, Z1)
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                line = Segment(Zc, Z2)
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # Machine center
                line = Segment(0, Rbo * np.exp(1j * np.angle(Z2)))
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # Rbo circle arc
                line = Arc1(
                    begin=Rbo * np.exp(-1j * np.pi / 2),
                    end=Rbo * np.exp(1j * np.pi / 2),
                    radius=Rbo,
                    is_trigo_direction=True,
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                line = Arc1(
                    begin=Rbo * np.exp(1j * np.pi / 2),
                    end=Rbo * np.exp(-1j * np.pi / 2),
                    radius=Rbo,
                    is_trigo_direction=True,
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )

            # Zooming and cleaning

            ax.axis("equal")
            ax.set_xlim(0, Rbo)
            ax.set_ylim(-Rbo / 10, Rbo * 1.1)
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
