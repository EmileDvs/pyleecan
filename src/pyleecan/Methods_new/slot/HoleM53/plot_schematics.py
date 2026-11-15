import matplotlib.pyplot as plt
import numpy as np

from ....Classes_new.geometry.arc_1 import Arc1
from ....Classes_new.machine.lam_hole import LamHole
from ....Classes_new.geometry.segment import Segment
from ....definitions import config_dict
from ....Functions_new.Plot import ARROW_COLOR, ARROW_WIDTH, MAIN_LINE_COLOR, MAIN_LINE_STYLE, MAIN_LINE_WIDTH, P_FONT_SIZE, SC_FONT_SIZE, SC_LINE_COLOR, SC_LINE_STYLE, SC_LINE_WIDTH, TEXT_BOX, plot_quote
from ....Methods import ParentMissingError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure

MAGNET_COLOR = config_dict["PLOT"]["COLOR_DICT"]["MAGNET_COLOR"]


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
) -> tuple[Figure, Axes]:
    """Plot the schematics of the slot

    Parameters
    ----------
    self : HoleM53
        A HoleM53 object
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
        hole = type(self)(
            Zh=4,
            W1=15e-3,
            W2=20e-3,
            W3=50e-3,
            W4=np.pi / 3,
            H0=75e-3,
            H1=7.5e-3,
            H2=22.5e-3,
            H3=7.5e-3,
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
    elif type_add_active == 0:
        # Remove magnets
        lam = self.parent.copy()
        lam.hole[0].remove_magnet()
        return lam.hole[0].plot_schematics(
            is_default=False,
            is_add_point_label=is_add_point_label,
            is_add_schematics=is_add_schematics,
            is_add_main_line=is_add_main_line,
            type_add_active=2,
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
            # W1
            line = Segment(
                begin=(point_dict["Z8"] + point_dict["Z7"]) / 2 * np.exp(1j * alpha),
                end=(point_dict["Z8s"] + point_dict["Z7s"]) / 2 * np.exp(1j * alpha),
            )
            line.plot(
                fig=fig,
                ax=ax,
                color=ARROW_COLOR,
                linewidth=ARROW_WIDTH,
                label="W1",
                offset_label=self.W1 * 0.3 - 1j * self.W1 * 0.6,
                is_arrow=True,
                fontsize=SC_FONT_SIZE,
            )
            # W2
            line = Segment(
                begin=point_dict["Z8s"] * np.exp(1j * alpha),
                end=point_dict["Z9s"] * np.exp(1j * alpha),
            )
            line.plot(
                fig=fig,
                ax=ax,
                color=ARROW_COLOR,
                linewidth=ARROW_WIDTH,
                label="W2",
                offset_label=(1 + 1j) * self.W1 * 0.2,
                is_arrow=True,
                fontsize=SC_FONT_SIZE,
            )
            # W3
            line = Segment(
                begin=point_dict["Z10s"] * np.exp(1j * alpha),
                end=point_dict["Z9s"] * np.exp(1j * alpha),
            )
            line.plot(
                fig=fig,
                ax=ax,
                color=ARROW_COLOR,
                linewidth=ARROW_WIDTH,
                label="W3",
                offset_label=(1 + 1j) * self.W1 * 0.2,
                is_arrow=True,
                fontsize=SC_FONT_SIZE,
            )
            # W4
            line = Arc1(
                begin=point_dict["Z9"] * np.exp(1j * alpha),
                end=(point_dict["Z8"] + self.W2) * np.exp(1j * alpha),
                radius=self.W2,
                is_trigo_direction=True,
            )
            line.plot(
                fig=fig,
                ax=ax,
                color=ARROW_COLOR,
                linewidth=ARROW_WIDTH,
                label="W4",
                offset_label=(1 + 1j) * self.W1 * 0.2,
                fontsize=SC_FONT_SIZE,
            )
            # H0
            line = Segment(
                begin=point_dict["Z7"].real * np.exp(1j * alpha),
                end=Rbo * np.exp(1j * alpha),
            )
            line.plot(
                fig=fig,
                ax=ax,
                color=ARROW_COLOR,
                linewidth=ARROW_WIDTH,
                label="H0",
                offset_label=(1 + 1j) * self.W1 * 0.3,
                is_arrow=True,
                fontsize=SC_FONT_SIZE,
            )
            # H1
            line = Segment(
                begin=point_dict["Z1s"] * np.exp(1j * alpha),
                end=Rbo * np.exp(1j * np.angle(point_dict["Z1s"])) * np.exp(1j * alpha),
            )
            line.plot(
                fig=fig,
                ax=ax,
                color=ARROW_COLOR,
                linewidth=ARROW_WIDTH,
                label="H1",
                offset_label=self.H2 * 0.2,
                is_arrow=True,
                fontsize=SC_FONT_SIZE,
            )
            # H2
            line = Segment(
                begin=(point_dict["Z3s"] + point_dict["Z4s"]) / 2 * np.exp(1j * alpha),
                end=(point_dict["Z10s"] + point_dict["Z9s"]) / 2 * np.exp(1j * alpha),
            )
            line.plot(
                fig=fig,
                ax=ax,
                color=ARROW_COLOR,
                linewidth=ARROW_WIDTH,
                label="H2",
                offset_label=self.W1 * 0.3,
                is_arrow=True,
                fontsize=SC_FONT_SIZE,
            )
            # H3
            line = Segment(
                begin=point_dict["Z2"] * np.exp(1j * alpha),
                end=point_dict["Z3"] * np.exp(1j * alpha),
            )
            line.plot(
                fig=fig,
                ax=ax,
                color=ARROW_COLOR,
                linewidth=ARROW_WIDTH,
                label="H3",
                offset_label=self.W1 * 0.3,
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
            # H1 radius
            line = Arc1(
                begin=(Rbo - self.H1) * np.exp(-1j * np.pi / 2 * 0.9) * np.exp(1j * alpha),
                end=(Rbo - self.H1) * np.exp(1j * np.pi / 2 * 0.9) * np.exp(1j * alpha),
                radius=Rbo - self.H1,
                is_trigo_direction=True,
            )
            line.plot(
                fig=fig,
                ax=ax,
                color=MAIN_LINE_COLOR,
                linestyle=MAIN_LINE_STYLE,
                linewidth=MAIN_LINE_WIDTH,
            )
            # W2 lines
            line = Segment(
                begin=point_dict["Z6"] * np.exp(1j * alpha),
                end=point_dict["Z8"] * np.exp(1j * alpha),
            )
            line.plot(
                fig=fig,
                ax=ax,
                color=MAIN_LINE_COLOR,
                linestyle=MAIN_LINE_STYLE,
                linewidth=MAIN_LINE_WIDTH,
            )
            line = Segment(
                begin=point_dict["Z6s"] * np.exp(1j * alpha),
                end=point_dict["Z8s"] * np.exp(1j * alpha),
            )
            line.plot(
                fig=fig,
                ax=ax,
                color=MAIN_LINE_COLOR,
                linestyle=MAIN_LINE_STYLE,
                linewidth=MAIN_LINE_WIDTH,
            )
            # H1 lines
            line = Segment(
                begin=0,
                end=Rbo * 1.3 * np.exp(1j * np.angle(point_dict["Z1s"])) * np.exp(1j * alpha),
            )
            line.plot(
                fig=fig,
                ax=ax,
                color=MAIN_LINE_COLOR,
                linestyle=MAIN_LINE_STYLE,
                linewidth=MAIN_LINE_WIDTH,
            )
            # W4 lines
            line = Segment(
                begin=point_dict["Z8"] * np.exp(1j * alpha),
                end=(Rbo * 1.3 + 1j * point_dict["Z8"].imag) * np.exp(1j * alpha),
            )
            line.plot(
                fig=fig,
                ax=ax,
                color=MAIN_LINE_COLOR,
                linestyle=MAIN_LINE_STYLE,
                linewidth=MAIN_LINE_WIDTH,
            )

        # Zooming and cleaning
        W = point_dict["Z1s"].imag * 1.05
        Rint = point_dict["Z7"].real * 0.9
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
