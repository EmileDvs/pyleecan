import numpy as np
import matplotlib.pyplot as plt
from ....Classes_new.optimization.opti_objective import OptiObjective
from . import _get_symbol_data_
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from matplotlib.axes import Axes


def plot_pareto(
    self,
    x_symbol: str,
    y_symbol: str,
    c_symbol: str | None = None,
    cmap=None,
    ax: Axes | None = None,
    title=None,
    grid: bool = False,
    is_show_fig: bool = True,
    save_path: str | None = None,
):
    """Plot the pareto front for 2 objective functions

    Parameters
    ----------
    self : XOutput
    x_symbol : str
        symbol of the first objective function
    y_symbol: str
        symbol of the second objective function
    c_symbol: str
        optional symbol to set the plot colors
    cmap: colormap
        optional colormap
    is_show_fig : bool
        True to show figure after plot
    save_path : str
        full path of the png file where the figure is saved if save_path is not None
    """

    return self.parent.plot_pareto(
        x_symbol,
        y_symbol,
        c_symbol,
        cmap,
        ax,
        title,
        grid,
        is_show_fig,
        save_path,
    )
