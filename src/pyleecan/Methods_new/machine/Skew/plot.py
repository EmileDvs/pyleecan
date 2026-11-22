import numpy as np

from ....Functions_new.Plot import dict_2D
from ....Functions_new.SciDataTool.Plot.plot_2d import plot_2D
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure


def plot(
    self,
    fig: Figure | None = None,
    ax: Axes | None = None,
    lam_name="",
    is_show_fig: bool = False,
    save_path: str | None = None,
    win_title: str | None = None,
) -> None:
    """Plots skew angle

    Parameters
    ----------
    self : Skew
        a Skew object

    """

    # Local import: avoids circular imports
    from ....Classes_new.machine.lam_slot_m import LamSlotM
    from ....Classes_new.machine.lam_h import LamH

    angle_list, z_list = self.comp_pattern()

    legend_list = ["Skew pattern"]
    y_list = [[a * 180 / np.pi for a in angle_list]]
    linestyle_list = ["solid"]


    if isinstance(self.parent, (LamSlotM, LamH)):
        legend_list.append("Rotor d-axis")
        y_list.append([0 for z in z_list])
        linestyle_list.append("dashed")

    plot_2D(
        [z_list],
        y_list,
        xlabel="Axial direction from Non Drive End to Drive End [m]",
        ylabel=lam_name + " skew angle [°]",
        type_plot="curve_point",
        fig=fig,
        ax=ax,
        is_show_fig=is_show_fig,
        save_path=save_path,
        win_title=win_title,
        legend_list=legend_list,
        linestyle_list=linestyle_list,
        **dict_2D,
    )
