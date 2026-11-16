import numpy as np

from ....Functions_new.Plot import dict_2D
from ....Functions_new.SciDataTool.Plot.plot_2d import plot_2D
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure


def plot(
    self,
    skew_axis=None,
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

    angle_list, z_list = self.comp_pattern()

    plot_2D(
        [z_list],
        [[a * 180 / np.pi for a in angle_list]],
        xlabel="Axial direction [m]",
        ylabel=lam_name + " skew angle [°]",
        type_plot="curve_point",
        fig=fig,
        ax=ax,
        is_show_fig=is_show_fig,
        save_path=save_path,
        win_title=win_title,
        **dict_2D,
    )
