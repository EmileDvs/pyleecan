from ....classes_common.parents import container_or_parent
import matplotlib.pyplot as plt
import numpy as np

from ....Classes_new.geometry.arc_1 import Arc1
from ....Classes_new.machine.lam_slot import LamSlot
from ....Classes_new.geometry.segment import Segment
from ....definitions import config_dict
from ....Functions_new.Plot import ARROW_COLOR, ARROW_WIDTH, MAIN_LINE_COLOR, MAIN_LINE_STYLE, MAIN_LINE_WIDTH, P_FONT_SIZE, SC_FONT_SIZE, SC_LINE_COLOR, SC_LINE_STYLE, SC_LINE_WIDTH, TEXT_BOX, plot_quote
from ....classes_common.errors import ParentMissingError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure
    from ....Classes_new.machine.lamination import Lamination

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
    lam: Lamination | None = None,
) -> tuple[Figure, Axes] | Lamination:
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
    lam : Lamination
        Lamination of the slot (default: the parent of the slot)

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
    lam = container_or_parent(self, lam, "lam")

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
                lam=lam,
            )
    else:
        # Getting the main plot
        if lam is None:
            raise ParentMissingError("Error: The slot is not inside a Lamination")
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
            self.plot_active(fig=fig, ax=ax, is_show_fig=False, lam=lam, lam_label=None if lam is None else lam.get_label(is_add_id=False))
        elif type_add_active == 2:
            self.plot_active(
                fig=fig, ax=ax, is_show_fig=False, enforced_default_color=MAGNET_COLOR, lam=lam, lam_label=None if lam is None else lam.get_label(is_add_id=False)
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
