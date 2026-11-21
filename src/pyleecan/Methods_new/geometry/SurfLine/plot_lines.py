import numpy as np

from ....Functions_new.utils.init_fig import init_fig
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure


def plot_lines(self, fig: Figure | None = None, ax: Axes | None = None, is_show_fig: bool = True) -> tuple[Figure, Axes]:
    """Plot the SurfLine-Contour in a matplotlib fig
    (For plotting unclosed contour, for Polygon use plot method from Surface object)

    Parameters
    ----------
    self : SurfLine
        A SurfLine object
    fig : Matplotlib.figure.Figure
        existing figure to use if None create a new one
    ax : Matplotlib.axes.Axes object
        Axis on which to plot the data
    is_show_fig : bool
        To call show at the end of the method

    Returns
    -------
    fig : Matplotlib.figure.Figure
        Figure containing the plot
    ax : Matplotlib.axes.Axes object
        Axis containing the plot
    """

    (fig, ax, patch_leg, label_leg) = init_fig(fig, ax)
    ax.set_xlabel("[m]")
    ax.set_ylabel("[m]")

    for line in self.line_list:
        line.plot(fig=fig, ax=ax)

    # Axis Setup
    ax.axis("equal")

    if is_show_fig:
        fig.show()
    return fig, ax
