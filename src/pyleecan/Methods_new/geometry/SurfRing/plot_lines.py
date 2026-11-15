import numpy as np

from ....Functions_new.init_fig import init_fig
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure


def plot_lines(self, fig: Figure | None = None, ax: Axes | None = None) -> tuple[Figure, Axes]:
    """Plot the SurfRing-Contour in a matplotlib fig
    (For plotting unclosed contour, for Polygon use plot method from Surface object)

    Parameters
    ----------
    self : SurfRing
        A SurfRing object
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

    (fig, ax, patch_leg, label_leg) = init_fig(fig, ax)
    ax.set_xlabel("[m]")
    ax.set_ylabel("[m]")

    points = self.out_surf.discretize(10)
    for idx in range(len(points) - 1):
        z1 = points[idx]
        z2 = points[idx + 1]
        x1 = np.real(z1)
        y1 = np.imag(z1)
        x2 = np.real(z2)
        y2 = np.imag(z2)
        ax.plot([x1, x2], [y1, y2], "k")

    points = self.in_surf.discretize(10)
    for idx in range(len(points) - 1):
        z1 = points[idx]
        z2 = points[idx + 1]
        x1 = np.real(z1)
        y1 = np.imag(z1)
        x2 = np.real(z2)
        y2 = np.imag(z2)
        ax.plot([x1, x2], [y1, y2], "k")

    # Axis Setup
    ax.axis("equal")

    fig.show()
    return fig, ax
